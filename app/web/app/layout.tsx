import type { Metadata } from "next";
import "./globals.css";

/**
 * Aucune police distante.
 *
 * Le squelette Next.js importe par defaut `next/font/google`. Ces polices sont
 * telechargees **au moment du build** puis auto-hebergees : le rendu final est
 * hors ligne, mais la construction, elle, exige un reseau. Un `bun run build`
 * relance sans connexion echouerait — exactement le scenario du jour de la
 * soutenance.
 *
 * On utilise donc une pile de polices systeme : rien a telecharger, ni au build
 * ni a l'execution. Si une police de marque devient necessaire, passer par
 * `next/font/local` avec le fichier versionne dans `public/`.
 *
 * Voir `docs/specs-frontend-web.md`, section 4.2.
 */
const PILE_SANS =
  'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
const PILE_MONO =
  'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace';

export const metadata: Metadata = {
  title: "Concorde — fiabilité des rapprochements DVF+ × DPE",
  description:
    "Concorde évalue si le rapprochement entre une vente immobilière et un diagnostic énergétique est fiable. Il n'estime aucun prix.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="fr"
      className="h-full antialiased"
      style={
        {
          "--font-geist-sans": PILE_SANS,
          "--font-geist-mono": PILE_MONO,
        } as React.CSSProperties
      }
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
