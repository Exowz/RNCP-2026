#!/usr/bin/env bash
#
# Rituel de demarrage de la soutenance.
#
#   ./scripts/soutenance.sh start        prepare tout et verifie (a lancer AVANT de se connecter)
#   ./scripts/soutenance.sh check        verifie seulement, sans rien demarrer
#   ./scripts/soutenance.sh api-model    relance la seule API modele (apres la demo D4 de E4)
#   ./scripts/soutenance.sh stop         arrete proprement les services lances ici
#
# Le script est idempotent : le relancer ne casse rien. Il sort en code non nul
# si un seul prerequis manque, pour qu'on le sache AVANT le jury et pas pendant.

set -uo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RACINE" || exit 1

JOURNAUX="$RACINE/monitoring/logs/soutenance"
PIDS="$JOURNAUX/pids"
VENV="$RACINE/.venv/bin"
LMS="$HOME/.lmstudio/bin/lms"
MODELE_LLM="google/gemma-4-e4b"

mkdir -p "$JOURNAUX"

# --- Presentation -----------------------------------------------------------

VERT=$'\033[0;32m'; ROUGE=$'\033[0;31m'; JAUNE=$'\033[0;33m'; GRAS=$'\033[1m'; FIN=$'\033[0m'
ECHECS=0

titre()  { printf '\n%s%s%s\n' "$GRAS" "$1" "$FIN"; }
ok()     { printf '  %s✓%s %s\n' "$VERT" "$FIN" "$1"; }
ko()     { printf '  %s✗%s %s\n' "$ROUGE" "$FIN" "$1"; ECHECS=$((ECHECS + 1)); }
info()   { printf '  %s·%s %s\n' "$JAUNE" "$FIN" "$1"; }

# Attend qu'une URL reponde. attendre <url> <secondes> <libelle>
attendre() {
  local url="$1" limite="$2" libelle="$3" i=0
  while [ "$i" -lt "$limite" ]; do
    if curl -sf -o /dev/null --max-time 2 "$url" 2>/dev/null; then
      ok "$libelle (${i}s)"; return 0
    fi
    sleep 1; i=$((i + 1))
  done
  ko "$libelle — pas de reponse apres ${limite}s"; return 1
}

# Lance un service en arriere-plan et retient son PID. servir <nom> <commande...>
servir() {
  local nom="$1"; shift
  if [ -f "$PIDS/$nom" ] && kill -0 "$(cat "$PIDS/$nom")" 2>/dev/null; then
    info "$nom deja demarre (PID $(cat "$PIDS/$nom"))"; return 0
  fi
  mkdir -p "$PIDS"
  # `< /dev/null` et `nohup` detachent le service du terminal appelant : sans
  # cela, le processus garde ouvert le descripteur de sortie du script, et
  # l'appelant (un tube, un terminal) semble ne jamais se terminer.
  nohup "$@" > "$JOURNAUX/$nom.log" 2>&1 < /dev/null &
  echo $! > "$PIDS/$nom"
  disown 2>/dev/null || true
  info "$nom lance (PID $!) — journal : monitoring/logs/soutenance/$nom.log"
}

# --- Etapes -----------------------------------------------------------------

etape_environnement() {
  titre "1. Environnement"
  [ -x "$VENV/python" ] || { ko "$VENV/python introuvable — l'environnement virtuel manque"; return; }
  ok "environnement Python : $("$VENV/python" --version 2>&1)"

  # shellcheck disable=SC1091
  if source "$RACINE/scripts/spark-env.sh" >/dev/null 2>&1; then
    if [ "${JAVA_HOME:-}" ] && "$JAVA_HOME/bin/java" -version 2>&1 | grep -q '"17'; then
      ok "JAVA_HOME sur JDK 17 (Spark)"
    else
      ko "JAVA_HOME ne pointe pas sur un JDK 17 — Spark echouera"
    fi
    [ "${SPARK_LOCAL_IP:-}" = "127.0.0.1" ] \
      && ok "SPARK_LOCAL_IP=127.0.0.1 (indispensable hors ligne)" \
      || ko "SPARK_LOCAL_IP non defini — Spark cherchera l'adresse mDNS du poste"
  else
    ko "scripts/spark-env.sh n'a pas pu etre source"
  fi
}

etape_postgres() {
  titre "2. PostgreSQL"
  if ! docker info >/dev/null 2>&1; then
    info "demon Docker arrete — demarrage de Docker Desktop"
    open -a Docker 2>/dev/null
    local i=0
    while [ "$i" -lt 60 ]; do
      docker info >/dev/null 2>&1 && break
      sleep 2; i=$((i + 2))
    done
  fi
  docker info >/dev/null 2>&1 || { ko "Docker ne repond pas — demarre Docker Desktop a la main"; return; }
  ok "demon Docker actif"

  docker compose up -d >/dev/null 2>&1
  local i=0
  while [ "$i" -lt 40 ]; do
    if docker inspect --format '{{.State.Health.Status}}' concorde-postgres 2>/dev/null | grep -q healthy; then
      ok "conteneur PostgreSQL sain (port 5433)"; return
    fi
    sleep 1; i=$((i + 1))
  done
  ko "PostgreSQL n'est pas sain apres 40s"
}

etape_lm_studio() {
  titre "3. Service IA local (C8)"
  [ -x "$LMS" ] || { ko "CLI lms introuvable : $LMS"; return; }

  "$LMS" server start >/dev/null 2>&1
  if ! curl -sf -o /dev/null --max-time 5 http://127.0.0.1:1234/v1/models; then
    ko "LM Studio ne repond pas sur 127.0.0.1:1234"; return
  fi
  ok "serveur LM Studio actif"

  # Ne charger QUE si le modele n'est pas deja en memoire : `lms load` sur un
  # modele deja charge tente une seconde instance et echoue sur la garde de
  # ressources (« insufficient system resources »).
  if "$LMS" ps 2>/dev/null < /dev/null | grep -q "gemma-4"; then
    ok "modele $MODELE_LLM deja en memoire"
  else
    # TTL long : evite les ~19 s de repagination au premier appel devant le jury.
    info "chargement du modele (peut prendre ~20 s)"
    "$LMS" load "$MODELE_LLM" --ttl 3600 -y >/dev/null 2>&1 < /dev/null
  fi

  if curl -sf --max-time 5 http://127.0.0.1:1234/v1/models 2>/dev/null | grep -q "gemma-4"; then
    ok "modele $MODELE_LLM expose par l'API"
  else
    ko "modele $MODELE_LLM absent de /v1/models"
  fi
}

etape_artefact() {
  titre "4. Artefact du modele"
  if [ -f "$RACINE/models/concorde_moteur.pt" ]; then
    ok "models/concorde_moteur.pt present ($(du -h "$RACINE/models/concorde_moteur.pt" | cut -f1))"
  else
    ko "artefact absent — executer : python -m concorde.model.entrainement"
  fi
  if [ -f "$RACINE/data/processed/rapprochements.parquet" ]; then
    ok "table des rapprochements presente"
  else
    ko "table absente — executer : python -m concorde.collect && python -m concorde.clean"
  fi
}

etape_front() {
  titre "5. Build du front Next.js"
  if [ -d "$RACINE/app/web/.next" ]; then
    ok "build present (aucune construction devant le jury)"
  else
    info "build absent — construction en cours, patiente"
    (cd "$RACINE/app/web" && CONCORDE_API_KEY="${CONCORDE_API_KEY:-dev-analyst-key}" bun run build > "$JOURNAUX/build-next.log" 2>&1)
    [ -d "$RACINE/app/web/.next" ] && ok "build termine" || ko "build echoue — voir monitoring/logs/soutenance/build-next.log"
  fi
}

etape_services() {
  titre "6. Demarrage des quatre services"
  servir api-data  "$VENV/uvicorn" api.data.main:app  --host 127.0.0.1 --port 8001
  servir api-model "$VENV/uvicorn" api.model.main:app --host 127.0.0.1 --port 8002
  servir app-jinja "$VENV/uvicorn" app.main:app       --host 127.0.0.1 --port 8000
  if [ ! -f "$PIDS/front-next" ] || ! kill -0 "$(cat "$PIDS/front-next" 2>/dev/null)" 2>/dev/null; then
    mkdir -p "$PIDS"
    ( cd "$RACINE/app/web" \
      && CONCORDE_API_KEY="${CONCORDE_API_KEY:-dev-analyst-key}" \
         nohup bun run start > "$JOURNAUX/front-next.log" 2>&1 < /dev/null & \
         echo $! > "$PIDS/front-next" )
    disown 2>/dev/null || true
    info "front-next lance"
  else
    info "front-next deja demarre"
  fi
}

etape_verification() {
  titre "7. Verification"
  attendre http://127.0.0.1:8001/sante 30 "API data     :8001"
  attendre http://127.0.0.1:8002/sante 45 "API modele   :8002"
  attendre http://127.0.0.1:8000/      30 "app Jinja    :8000"
  attendre http://127.0.0.1:3000/      30 "front Next   :3000"

  # Le modele est-il reellement charge, ou l'API est-elle degradee ?
  if curl -sf --max-time 5 http://127.0.0.1:8002/sante 2>/dev/null | grep -q '"modele_charge":true'; then
    ok "modele charge dans l'API"
  else
    ko "API modele demarree mais SANS modele — elle repondra 503"
  fi

  # Le refus sans cle : c'est une preuve qu'on montre en direct.
  local code
  code=$(curl -so /dev/null -w "%{http_code}" --max-time 5 -X POST http://127.0.0.1:8002/predict \
         -H 'Content-Type: application/json' -d '{}' 2>/dev/null)
  [ "$code" = "401" ] && ok "refus sans cle d'API : 401" || ko "attendu 401 sans cle, obtenu $code"
}

bilan() {
  if [ "$ECHECS" -eq 0 ]; then
    printf '\n%s%s  TOUT EST PRET — tu peux te connecter.%s\n' "$GRAS" "$VERT" "$FIN"
    printf '  Accueil de la demonstration : %shttp://127.0.0.1:3000/%s\n' "$GRAS" "$FIN"
    printf '  Repli si le front Next pose probleme : http://127.0.0.1:8000/\n\n'
  else
    printf '\n%s%s  %d PROBLEME(S) — ne te connecte pas encore.%s\n' "$GRAS" "$ROUGE" "$ECHECS" "$FIN"
    printf '  Journaux : monitoring/logs/soutenance/\n\n'
  fi
  return "$ECHECS"
}

# --- Modes ------------------------------------------------------------------

case "${1:-start}" in
  start)
    printf '%sRituel de demarrage — soutenance RNCP%s\n' "$GRAS" "$FIN"
    etape_environnement; etape_postgres; etape_lm_studio
    etape_artefact; etape_front; etape_services; etape_verification
    bilan
    ;;

  check)
    printf '%sVerification seule%s\n' "$GRAS" "$FIN"
    etape_verification
    bilan
    ;;

  api-model)
    # Apres la demonstration D4 de E4, ou l'on arrete volontairement l'API.
    titre "Relance de l'API modele"
    rm -f "$PIDS/api-model"
    servir api-model "$VENV/uvicorn" api.model.main:app --host 127.0.0.1 --port 8002
    attendre http://127.0.0.1:8002/sante 45 "API modele   :8002"
    bilan
    ;;

  stop)
    titre "Arret des services"
    for nom in api-data api-model app-jinja front-next; do
      if [ -f "$PIDS/$nom" ]; then
        pid=$(cat "$PIDS/$nom")
        kill "$pid" 2>/dev/null && ok "$nom arrete (PID $pid)" || info "$nom deja arrete"
        rm -f "$PIDS/$nom"
      fi
    done
    pkill -f "next-server" 2>/dev/null
    info "PostgreSQL et LM Studio restent actifs (docker compose down / lms server stop)"
    printf '\n'
    ;;

  *)
    printf 'Usage : %s [start|check|api-model|stop]\n' "$0"
    exit 2
    ;;
esac
