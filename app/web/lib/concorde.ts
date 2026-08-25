import "server-only";

export type NiveauConfiance = "eleve" | "moyen" | "faible" | "insuffisant";

export type Presentation = {
  id_mutation: string;
  id_rapprochement: string;
  nom_commune: string;
  code_commune: string;
  code_departement: string;
  etiquette_dpe: string | null;
  type_local: string;
  date_mutation: string;
  surface_reelle_bati: number;
  valeur_fonciere: number;
  a_dpe: boolean;
  niveau_confiance: NiveauConfiance;
};

export type EntreePrediction = {
  id_mutation: string;
  date_mutation: string;
  valeur_fonciere: number;
  surface_reelle_bati: number;
  type_local: "Maison" | "Appartement";
  code_commune: string;
  id_parcelle: string;
  numero_dpe?: string;
  date_dpe?: string;
  etiquette_dpe?: string;
  surface_habitable_dpe?: number;
  type_batiment_dpe?: string;
  annee_construction?: number;
  score_ban?: number;
  conso_kwh_m2_an?: number;
  nb_dpe_candidats: number;
};

export type DetailRapprochement = { presentation: Presentation; donnees: EntreePrediction };
export type CasDemonstration = DetailRapprochement & { identifiant: string; intitule: string };

export type Verdict = {
  id_mutation: string;
  numero_dpe: string | null;
  statut: "evalue" | "non_evaluable";
  score_anomalie: number | null;
  niveau_anomalie: "normal" | "a_verifier" | "atypique" | "non_evaluable";
  score_coherence: number | null;
  motifs: Array<{ identifiant: string; libelle: string; gravite: "majeur" | "mineur"; message: string }>;
  confiance: {
    score: number;
    niveau: NiveauConfiance;
    reserves: Array<{ identifiant: string; message: string; penalite: number }>;
  };
  exposition_aleas: { niveau_max: number; nb_aleas_significatifs: number };
  variables_atypiques: Array<{ variable: string; part_de_l_ecart: number; valeur: number | null }>;
  erreur_reconstruction: number | null;
  explication: string;
  modele: { version: string; entraine_le: string };
};

export type Explication = {
  texte: string;
  source: "modele_local" | "texte_assemble";
};

type ProjectionExplication = Pick<
  Verdict,
  "statut" | "niveau_anomalie" | "score_coherence" | "motifs" | "confiance" | "explication"
>;

export type Regle = { identifiant: string; libelle: string; gravite: "majeur" | "mineur"; seuil: string; justification: string };
export type FicheModele = { version?: string; entraine_le?: string; limites?: string[] };

const dataApi = process.env.CONCORDE_DATA_API_URL ?? "http://127.0.0.1:8001";
const modelApi = process.env.CONCORDE_MODEL_API_URL ?? "http://127.0.0.1:8002";

function cleApi(): string {
  const cle = process.env.CONCORDE_API_KEY;
  if (!cle) throw new Error("CONCORDE_API_KEY est absente de l'environnement du serveur Next.js.");
  return cle;
}

async function appel<T>(base: string, chemin: string, init?: RequestInit): Promise<T> {
  let reponse: Response;
  try {
    reponse = await fetch(`${base}${chemin}`, {
      ...init,
      cache: "no-store",
      headers: { "X-API-Key": cleApi(), ...init?.headers },
    });
  } catch {
    throw new Error("Le service Concorde attendu localement ne répond pas.");
  }
  if (!reponse.ok) throw new Error(`Le service Concorde a refuse la demande (${reponse.status}).`);
  return reponse.json() as Promise<T>;
}

export async function obtenirDemonstrations(): Promise<CasDemonstration[]> {
  return (await appel<{ cas: CasDemonstration[] }>(dataApi, "/rapprochements/demonstration")).cas;
}

export function obtenirDetail(idMutation: string): Promise<DetailRapprochement> {
  return appel(dataApi, `/rapprochements/${encodeURIComponent(idMutation)}`);
}

export function evaluer(donnees: EntreePrediction): Promise<Verdict> {
  return appel(modelApi, "/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(donnees) });
}

function projeterExplication(verdict: Verdict): ProjectionExplication {
  const { statut, niveau_anomalie, score_coherence, motifs, confiance, explication } = verdict;
  return { statut, niveau_anomalie, score_coherence, motifs, confiance, explication };
}

export function expliquer(verdict: Verdict): Promise<Explication> {
  return appel(modelApi, "/expliquer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(projeterExplication(verdict)),
  });
}

export function obtenirRegles(): Promise<Regle[]> { return appel(modelApi, "/regles"); }
export function obtenirFicheModele(): Promise<FicheModele> { return appel(modelApi, "/modele/fiche"); }
