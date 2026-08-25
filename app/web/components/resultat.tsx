/* eslint-disable react/no-unescaped-entities -- le contenu français est rendu avec les apostrophes typographiques du référentiel. */

import Link from "next/link";

import { EchelleDpe } from "@/components/dpe-scale";
import type { DetailRapprochement, Verdict } from "@/lib/concorde";
import { libelleAlea, libelleAnomalie, libelleConfiance } from "@/lib/libelles";

const lectureConfiance = {
  eleve: "Les informations disponibles permettent une lecture solide.",
  moyen: "Des informations manquent : la lecture doit rester prudente.",
  faible: "Les données sont trop fragiles pour une conclusion assurée.",
  insuffisant: "Concorde ne peut pas conclure avec les informations disponibles.",
};

const lectureAnomalie = {
  normal: "Ce cas ressemble aux autres rapprochements connus.",
  a_verifier: "Ce cas mérite une vérification avant toute réutilisation.",
  atypique: "Ce cas s'écarte fortement des autres rapprochements connus.",
  non_evaluable: "Aucun score n'est produit lorsqu'il manque un DPE.",
};



function pourcentage(score: number | null): string {
  return score === null ? "Non calculé" : `${Math.round(score * 100)} %`;
}

export function Resultat({ detail, profil, verdict }: { detail: DetailRapprochement; profil: "particulier" | "analyste"; verdict: Verdict }) {
  const presentation = detail.presentation;
  const autreProfil = profil === "particulier" ? "analyste" : "particulier";
  const lienProfil = `/resultat/${encodeURIComponent(presentation.id_mutation)}?profil=${autreProfil}`;

  return <>
    <nav aria-label="Fil d'Ariane" className="breadcrumb"><Link href="/">Accueil</Link><span aria-hidden="true">/</span><span>Résultat</span></nav>
    <section className="result-heading" aria-labelledby="titre-resultat">
      <div><p className="eyebrow">Cas évalué</p><h1 id="titre-resultat">{presentation.type_local} de {presentation.surface_reelle_bati} m² à {presentation.nom_commune}</h1>
        <p>Vente du {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(presentation.date_mutation))}.{presentation.a_dpe ? "" : " Aucun DPE n'a été rapproché."}</p>
      </div>
      <div className="profile-switch"><p>Restitution : <strong>{profil === "particulier" ? "particulier" : "analyste"}</strong></p><Link className="button secondary" href={lienProfil}>Voir la version {autreProfil}</Link></div>
    </section>

    <section aria-live="polite" aria-labelledby="verdict-heading" className="result-live">
      <h2 id="verdict-heading">Ce que Concorde peut dire</h2><p className="verdict-summary">{verdict.explication}</p>
      <div className="axis-grid">
        <article className="axis axis-coherence"><h3>Cohérence des deux sources</h3><p className="score">{pourcentage(verdict.score_coherence)}</p><p>100 % signifie qu'aucune contradiction connue n'a été détectée. Ce score ne mesure pas le prix du logement.</p></article>
        <article className="axis axis-anomalie"><h3>Ressemblance avec les autres cas</h3><p className="score">{libelleAnomalie[verdict.niveau_anomalie]}</p><p>{lectureAnomalie[verdict.niveau_anomalie]}</p></article>
        <article className="axis axis-confiance"><h3>Confiance dans cette lecture</h3><p className="score">{libelleConfiance[verdict.confiance.niveau]}</p><p>{lectureConfiance[verdict.confiance.niveau]}</p></article>
      </div>
    </section>

    <section className="result-details" aria-label="Éléments de lecture">
      <div><h2>Diagnostic énergétique</h2>{presentation.etiquette_dpe ? <><p>Étiquette DPE : <strong>{presentation.etiquette_dpe}</strong>, sur une échelle de A à G.</p><EchelleDpe etiquette={presentation.etiquette_dpe} /></> : <p>Aucune étiquette : sans diagnostic rapproché, Concorde refuse de calculer un score.</p>}</div>
      <div><h2>Réserves à lire avant le résultat</h2>{verdict.confiance.reserves.length ? <ul className="reason-list">{verdict.confiance.reserves.map((reserve) => <li key={reserve.identifiant}>{reserve.message}</li>)}</ul> : <p>Aucune réserve de confiance n'a été détectée.</p>}</div>
    </section>

    <section className="evidence-section"><h2>Pourquoi ce résultat ?</h2>{verdict.motifs.length ? <ul className="reason-list">{verdict.motifs.map((motif) => <li key={motif.identifiant}><strong>{motif.libelle}.</strong> {motif.message}</li>)}</ul> : <p>Aucune contradiction de cohérence n'a été déclenchée par les règles connues.</p>}<p>Exposition aux aléas : {libelleAlea[verdict.exposition_aleas.niveau_max] ?? "Inconnu"} ({verdict.exposition_aleas.nb_aleas_significatifs} aléa(s) de niveau significatif). Cette exposition est communale, pas parcellaire.</p></section>

    {profil === "analyste" ? <section className="technical-section" aria-labelledby="technique-heading"><h2 id="technique-heading">Détail technique</h2><dl className="technical-list"><div><dt>Mutation</dt><dd>{presentation.id_mutation}</dd></div><div><dt>Rapprochement</dt><dd>{presentation.id_rapprochement}</dd></div><div><dt>Parcelle</dt><dd>{detail.donnees.id_parcelle}</dd></div><div><dt>Version du modèle</dt><dd>{verdict.modele.version}, entraîné le {verdict.modele.entraine_le}</dd></div></dl>{verdict.variables_atypiques.length ? <ul className="reason-list">{verdict.variables_atypiques.map((variable) => <li key={variable.variable}>{variable.variable} représente {Math.round(variable.part_de_l_ecart * 100)} % de l'écart reconstruit.</li>)}</ul> : null}</section> : null}
  </>;
}
