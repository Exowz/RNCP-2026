/* eslint-disable react/no-unescaped-entities -- le contenu français est rendu avec les apostrophes typographiques du référentiel. */

import { SiteShell } from "@/components/site-shell";

export default function CommentCaMarche() {
  return <SiteShell page="/comment-ca-marche">
    <section className="page-intro"><h1>Une chaîne qui conserve ses incertitudes</h1><p>Concorde ne cherche pas à faire disparaître les ambiguïtés du croisement des données. Il les compte, les explique et refuse de conclure lorsqu&apos;un DPE manque.</p></section>
    <ol className="pipeline" aria-label="Chaîne de traitement Concorde">
      <li><strong>1 735 lignes brutes</strong><span>Collecter les données DVF+, DPE et les informations d'exposition aux aléas.</span></li>
      <li><strong>922 rapprochements</strong><span>Relier ventes et diagnostics par parcelle, sans prétendre que cette clé est parfaite.</span></li>
      <li><strong>716 appariés</strong><span>Comparer les cas qui contiennent une vente et un DPE.</span></li>
      <li><strong>206 sans DPE</strong><span>Conserver les cas non évaluables plutôt qu'inventer un score.</span></li>
    </ol>
    <section className="explanation-grid"><div><h2>Ce qui est comparé</h2><p>Les surfaces, le type de logement, la chronologie du DPE et des signaux de contexte. Le prix est un signal de cohérence, jamais une prédiction.</p></div><div><h2>Ce qui est rendu visible</h2><p>Les contradictions, les réserves liées au géocodage ou à plusieurs DPE, et l'exposition aux aléas sont restitués séparément.</p></div></section>
    <section className="evidence-section"><h2>Une preuve, pas une boîte noire</h2><p>Le nettoyage, les règles de cohérence, le modèle et la livraison continue sont versionnés. Les règles visibles sur la page Transparence viennent du code réellement exécuté.</p></section>
  </SiteShell>;
}
