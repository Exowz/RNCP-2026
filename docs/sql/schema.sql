CREATE TABLE IF NOT EXISTS reference_commune (
    code_commune CHAR(5) PRIMARY KEY,
    nom_commune TEXT NOT NULL,
    code_postal CHAR(5) NOT NULL,
    departement CHAR(2) NOT NULL,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (code_commune ~ '^[0-9][0-9AB][0-9]{3}$')
);

CREATE INDEX IF NOT EXISTS idx_reference_commune_departement
    ON reference_commune (departement);

CREATE TABLE IF NOT EXISTS exposition_alea (
    code_commune CHAR(5) NOT NULL REFERENCES reference_commune (code_commune),
    type_alea TEXT NOT NULL,
    niveau SMALLINT NOT NULL CHECK (niveau BETWEEN 0 AND 4),
    PRIMARY KEY (code_commune, type_alea)
);

CREATE INDEX IF NOT EXISTS idx_exposition_alea_niveau
    ON exposition_alea (niveau) WHERE niveau >= 3;
