/* eslint-disable react/no-unescaped-entities -- le contenu français est rendu avec les apostrophes typographiques du référentiel. */

import Link from "next/link";

import { EchelleDpe } from "@/components/dpe-scale";
import { SiteShell } from "@/components/site-shell";
import { obtenirDemonstrations, type CasDemonstration } from "@/lib/concorde";
import { libelleConfiance } from "@/lib/libelles";

export const dynamic = "force-dynamic";

function formatDate(date: string): string {
  return new Intl.DateTimeFormat("fr-FR", { month: "long", year: "numeric" }).format(new Date(date));
}

export default async function Accueil() {
  let demonstrations: CasDemonstration[];
  let erreur: string | null = null;
  try { demonstrations = await obtenirDemonstrations(); } catch (cause) {
    demonstrations = [];
    erreur = cause instanceof Error ? cause.message : "La démonstration est indisponible.";
  }
  return <SiteShell page="/">
    <section className="hero" aria-labelledby="titre-principal"><div className="hero-copy"><h1 id="titre-principal">Peut-on vraiment relier cette vente à ce diagnostic&nbsp;?</h1><p className="lead">Deux bases publiques décrivent le même logement sans partager d'identifiant fiable. Quand on les croise, le rapprochement peut être faux — et rien ne vous le signale. Concorde vous dit quand vous pouvez y croire.</p><Link className="button" href="#demonstration">Examiner les cas réels</Link></div><aside className="hero-proof"><p className="proof-label">Limite explicite</p><p>Concorde n&apos;estime aucun prix et ne produit aucune tarification.</p></aside></section>
    <section className="definitions" aria-labelledby="vocabulaire"><h2 id="vocabulaire">Trois termes pour lire le dossier</h2><p>Le vocabulaire métier est posé avant le résultat : aucune connaissance préalable des jeux de données n&apos;est attendue.</p><dl><div><dt><dfn>DVF+</dfn></dt><dd>Le registre public des ventes immobilières déjà conclues, issu des actes notariés. Il ne contient pas les biens en vente.</dd></div><div><dt><dfn>DPE</dfn></dt><dd>Le diagnostic de performance énergétique, avec une étiquette de A à G.</dd></div><div><dt><dfn>Rapprochement</dfn></dt><dd>L&apos;association supposée d&apos;une vente et d&apos;un diagnostic. C&apos;est cette supposition que Concorde vérifie.</dd></div></dl></section>
    <section className="cases-section" id="demonstration" aria-labelledby="titre-demonstration"><h2 id="titre-demonstration">Cinq dossiers, cinq lectures possibles</h2><p className="section-intro">Chaque exemple vient de la table préparée par Concorde. Aucun cas n&apos;est inventé pour la démonstration.</p>{erreur ? <p role="alert" className="alert">{erreur}</p> : null}<div className="case-grid">{demonstrations.map((cas) => <article className="case-card" key={cas.identifiant}><div><h3>{cas.intitule}</h3><p>{cas.presentation.type_local} de {cas.presentation.surface_reelle_bati} m², vendu en {formatDate(cas.presentation.date_mutation)} à {cas.presentation.nom_commune} ({cas.presentation.code_departement}).</p></div><div>{cas.presentation.etiquette_dpe ? <><EchelleDpe etiquette={cas.presentation.etiquette_dpe} /><p>Confiance attendue : <strong>{libelleConfiance[cas.presentation.niveau_confiance]}</strong>.</p></> : <p><strong>Sans DPE :</strong> Concorde ne conclura pas.</p>}</div><Link className="text-link" href={`/resultat/${encodeURIComponent(cas.presentation.id_mutation)}`}>Ouvrir le dossier</Link></article>)}</div></section>
  </SiteShell>;
}
