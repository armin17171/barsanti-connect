from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione letta dalle variabili d'ambiente (o da un file .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Connessione DB. Default SQLite locale per facilitare i test fuori da Docker.
    database_url: str = "sqlite:///./data/barsanti.sqlite3"

    # Chiave per firmare i cookie di sessione. In produzione SEMPRE da env.
    secret_key: str = "dev-insecure-secret-change-me"

    # Account admin creato automaticamente al primo avvio.
    admin_username: str = "admin"
    admin_password: str = "admin"

    # Limite upload media (MB)
    max_upload_mb: int = 1024

    # Cartella su disco dove vengono salvati i media caricati.
    media_dir: str = "media"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
