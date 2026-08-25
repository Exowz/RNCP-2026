/**
 * Libellés d'affichage des valeurs de contrat.
 *
 * `eleve`, `a_verifier`, `majeur`… sont des valeurs du contrat de l'API Concorde.
 * Elles restent en ASCII sans accent : les accentuer casserait les schémas
 * Pydantic côté Python et tout client déjà en place. Ce sont des identifiants,
 * pas du texte destiné à être lu.
 *
 * L'interface ne doit donc jamais les rendre telles quelles — sans quoi
 * l'utilisateur lit « eleve » ou « A Verifier » juste à côté de « Diagnostic
 * énergétique ». La traduction se fait ici, en un seul endroit, pour que les
 * deux pages qui en ont besoin ne divergent pas.
 */

import type { NiveauConfiance } from "@/lib/concorde";

export const libelleConfiance: Record<NiveauConfiance, string> = {
  eleve: "Élevée",
  moyen: "Moyenne",
  faible: "Faible",
  insuffisant: "Insuffisante",
};

export const libelleAnomalie: Record<string, string> = {
  normal: "Conforme aux autres cas",
  a_verifier: "À vérifier",
  atypique: "Atypique",
  non_evaluable: "Non évaluable",
};

/** Échelle Géorisques : le niveau numérique ne parle qu'aux initiés. */
export const libelleAlea = ["Nul", "Très faible", "Faible", "Moyen", "Fort"];
