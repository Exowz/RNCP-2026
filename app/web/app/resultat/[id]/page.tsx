import { notFound } from "next/navigation";

import { Resultat } from "@/components/resultat";
import { SiteShell } from "@/components/site-shell";
import { evaluer, obtenirDetail } from "@/lib/concorde";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ id: string }>; searchParams: Promise<{ profil?: string }> };

export default async function PageResultat({ params, searchParams }: Props) {
  const { id } = await params;
  const { profil } = await searchParams;
  const restitution = profil === "analyste" ? "analyste" : "particulier";
  let detail;
  let verdict;
  let erreur: string | null = null;
  try {
    detail = await obtenirDetail(id);
    verdict = await evaluer(detail.donnees);
  } catch (cause) {
    if (cause instanceof Error && cause.message.includes("(404)")) notFound();
    erreur = cause instanceof Error ? cause.message : "Le résultat est indisponible.";
  }
  if (erreur || !detail || !verdict) return <SiteShell page=""><h1>Résultat indisponible</h1><p role="alert" className="alert">{erreur ?? "Le résultat est indisponible."}</p></SiteShell>;
  return <SiteShell page=""><Resultat detail={detail} profil={restitution} verdict={verdict} /></SiteShell>;
}
