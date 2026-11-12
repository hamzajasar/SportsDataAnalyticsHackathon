from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    app_name: str = "Sports Analytics API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://hackathon:hackathon@localhost:5432/hackathon"
    cors_origins: list[str] = ["http://localhost:5173"]
    data_dir: Path = ROOT_DIR / "data"
    # Raw-data explorer endpoints (/api/datasets/*). On for local dev, OFF when deployed
    # so the organisers' datasets are never publicly downloadable.
    expose_datasets: bool | None = None

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, v: str) -> str:
        # Hosting providers (Render, Heroku…) give postgres:// or postgresql:// URLs;
        # SQLAlchemy needs the driver named explicitly.
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                return "postgresql+psycopg://" + v[len(prefix) :]
        return v

    @property
    def datasets_enabled(self) -> bool:
        if self.expose_datasets is not None:
            return self.expose_datasets
        return self.environment == "development"


settings = Settings()
