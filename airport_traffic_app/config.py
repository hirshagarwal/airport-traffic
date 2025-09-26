from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from the project-level .env if present.
load_dotenv(Path(__file__).resolve().parent / ".env")


@dataclass
class AppConfig:
    """Configuration container for service credentials and shared settings."""

    tsa_api_key: Optional[str]
    flights_api_key: Optional[str]


def load_config() -> AppConfig:
    """Load application configuration from environment variables."""
    from os import getenv

    return AppConfig(
        tsa_api_key=getenv("TSA_API_KEY"),
        flights_api_key=getenv("FLIGHTS_API_KEY"),
    )
