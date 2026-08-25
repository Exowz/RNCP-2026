/* eslint-disable react/no-unescaped-entities -- le contenu français est rendu avec les apostrophes typographiques du référentiel. */

import Link from "next/link";
import type { ReactNode } from "react";

const navigation = [
  { href: "/", label: "Accueil" },
  { href: "/comment-ca-marche", label: "Comment ça marche" },
  { href: "/transparence", label: "Transparence" },
];

export function SiteShell({ children, page }: { children: ReactNode; page: string }) {
  return <>
    <a className="skip-link" href="#contenu">Aller au contenu principal</a>
    <header className="site-header"><div className="container header-content">
      <Link className="brand" href="/">Concorde<span>Fiabilité des rapprochements DVF+ et DPE</span></Link>
      <nav aria-label="Navigation principale"><ul className="nav-list">
        {navigation.map((item) => <li key={item.href}><Link aria-current={page === item.href ? "page" : undefined} href={item.href}>{item.label}</Link></li>)}
      </ul></nav>
    </div></header>
    <main className="container main-content" id="contenu">{children}</main>
    <footer className="site-footer"><div className="container"><p>Concorde croise des données publiques DVF+, DPE et Géorisques pour rendre l'incertitude visible.</p><p>Il ne fournit ni estimation de prix, ni tarification.</p></div></footer>
  </>;
}
