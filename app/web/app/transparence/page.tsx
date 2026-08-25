/* eslint-disable react/no-unescaped-entities -- le contenu français est rendu avec les apostrophes typographiques du référentiel. */

import { SiteShell } from "@/components/site-shell";
import { obtenirFicheModele, obtenirRegles, type FicheModele, type Regle } from "@/lib/concorde";

export const dynamic = "force-dynamic";

export default async function Transparence() {
  let regles: Regle[] = [];
  let fiche: FicheModele = {};
  let erreur: string | null = null;
  try { [regles, fiche] = await Promise.all([obtenirRegles(), obtenirFicheModele()]); } catch (cause) {
    erreur = cause instanceof Error ? cause.message : "Les informations de transparence sont indisponibles.";
  }
  return <SiteShell page="/transparence">
    <section className="page-intro"><h1>Les règles que Concorde applique</h1><p>Ces règles sont demandées à l&apos;API du modèle au chargement de cette page. Elles ne sont pas recopiées dans cette interface.</p></section>
    {erreur ? <p role="alert" className="alert">{erreur}</p> : null}
    <section aria-labelledby="rules-heading"><h2 id="rules-heading">Règles de cohérence</h2><div className="rules-list">{regles.map((regle) => <article key={regle.identifiant}><div><h3>{regle.libelle}</h3><p className="rule-id">{regle.identifiant}</p></div><dl className="rule-meta"><div><dt>Seuil</dt><dd>{regle.seuil}</dd></div><div><dt>Gravité</dt><dd>{regle.gravite}</dd></div></dl><p>{regle.justification}</p></article>)}</div></section>
    <section className="technical-section"><h2>Fiche du modèle servi</h2><p>Version : <strong>{fiche.version ?? "non disponible"}</strong>{fiche.entraine_le ? `, entraînée le ${fiche.entraine_le}.` : "."}</p>{fiche.limites?.length ? <ul className="reason-list">{fiche.limites.map((limite) => <li key={limite}>{limite}</li>)}</ul> : <p>Les limites documentées seront affichées lorsque le service de modèle est disponible.</p>}</section>
  </SiteShell>;
}
