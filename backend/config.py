"""
Configuration settings for Social Impact Tracker
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DATABASE_DIR = BASE_DIR / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATABASE_DIR / "social_impact.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True

# Compression settings
COMPRESSION_ENABLED = True
DICTIONARY_COMPRESSION_THRESHOLD = 3  # Minimum occurrences to compress

# Metric calculation weights for composite score
METRIC_WEIGHTS = {
    "outcome_improvement": 0.40,  # 40% weight
    "cost_efficiency": 0.35,      # 35% weight (inverted cost per beneficiary)
    "growth_rate": 0.25           # 25% weight
}

# Normalization ranges for metrics
NORMALIZATION_RANGES = {
    "outcome_improvement": (0, 100),  # Expected range for outcome improvement
    "cost_per_beneficiary": (0, 1000),  # Expected range for cost per beneficiary
    "growth_rate": (-1, 2)  # Expected range for growth rate (-100% to 200%)
}

# Application metadata
APP_NAME = "Social Impact Tracker"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A nonprofit analytics system for measuring and optimizing program impact"

# CORS settings
CORS_ORIGINS = [
    "http://localhost:8501",  # Streamlit default port
    "http://localhost:3000",  # Common frontend port
]
