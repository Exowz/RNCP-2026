export function EchelleDpe({ etiquette }: { etiquette: string | null }) {
  return <div aria-label={`Étiquette DPE ${etiquette ?? "non disponible"}`} className="dpe-scale">
    {"ABCDEFG".split("").map((lettre) => <span className={lettre === etiquette ? "is-active" : undefined} key={lettre}>{lettre}{lettre === etiquette ? <span className="sr-only">, étiquette du logement</span> : null}</span>)}
  </div>;
}
