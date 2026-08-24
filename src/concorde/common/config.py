"""Configuration centralisee, lue depuis l'environnement (12-factor).

Aucun secret n'est ecrit dans le code : les cles d'API et le mot de passe
PostgreSQL viennent de `.env` (non versionne) ou de l'environnement CI.
Voir `.env.example` pour la liste exhaustive des variables. (C17)
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from concorde.common.paths import PROJECT_ROOT

# Roles applicatifs, du moins au plus privilegie (C17 : gestion des droits).
ROLE_HIERARCHY: dict[str, int] = {"reader": 10, "analyst": 20, "admin": 30}


class Settings(BaseSettings):
    """Parametres d'execution de Concorde."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_prefix="CONCORDE_",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Reseau interne ---
    data_api_host: str = "127.0.0.1"
    data_api_port: int = 8001
    model_api_host: str = "127.0.0.1"
    model_api_port: int = 8002
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    model_api_url: str = "http://127.0.0.1:8002"
    data_api_url: str = "http://127.0.0.1:8001"
    lm_studio_url: str = "http://127.0.0.1:1234/v1"
    lm_studio_model: str = "google/gemma-4-e4b"

    # --- Securite (C17) ---
    api_keys: str = Field(
        default="dev-reader-key:reader,dev-analyst-key:analyst,dev-admin-key:admin",
        description="Liste 'cle:role' separee par des virgules.",
    )

    # --- PostgreSQL (C4) ---
    pg_host: str = "127.0.0.1"
    pg_port: int = 5433
    pg_db: str = "concorde"
    pg_user: str = "concorde"
    pg_password: str = "change-me-in-local-env"  # noqa: S105 - valeur factice documentee

    # --- Execution ---
    offline: bool = True
    log_level: str = "INFO"
    log_dir: str = "monitoring/logs"

    @field_validator("log_level")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.upper()

    @property
    def api_key_roles(self) -> dict[str, str]:
        """Table cle d'API -> role, construite a partir de la variable d'environnement."""
        table: dict[str, str] = {}
        for item in self.api_keys.split(","):
            item = item.strip()
            if not item:
                continue
            key, _, role = item.partition(":")
            role = role.strip() or "reader"
            if role not in ROLE_HIERARCHY:
                raise ValueError(f"Role inconnu dans CONCORDE_API_KEYS : {role!r}")
            table[key.strip()] = role
        return table

    @property
    def pg_dsn(self) -> str:
        """DSN PostgreSQL (psycopg3 / SQLAlchemy)."""
        return (
            f"postgresql+psycopg://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instance unique de configuration (mise en cache)."""
    return Settings()
