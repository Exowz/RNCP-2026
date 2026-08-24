"""Initialise PostgreSQL local et importe les references de demonstration."""

from concorde.database import initialiser_et_importer

if __name__ == "__main__":
    print(f"{initialiser_et_importer()} communes importees dans PostgreSQL.")
