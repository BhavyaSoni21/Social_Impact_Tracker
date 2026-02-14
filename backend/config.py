import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATABASE_DIR / "social_impact.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True

COMPRESSION_ENABLED = True
DICTIONARY_COMPRESSION_THRESHOLD = 3

METRIC_WEIGHTS = {
    "outcome_improvement": 0.40,
    "cost_efficiency": 0.35,
    "growth_rate": 0.25
}

NORMALIZATION_RANGES = {
    "outcome_improvement": (0, 100),
    "cost_per_beneficiary": (0, 1000),
    "growth_rate": (-1, 2)
}

APP_NAME = "Social Impact Tracker"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A nonprofit analytics system for measuring and optimizing program impact"

CORS_ORIGINS = [
    "http://localhost:8501",
    "http://localhost:3000",
]
