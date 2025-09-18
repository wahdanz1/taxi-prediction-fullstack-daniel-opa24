from pathlib import Path
from importlib.resources import files

# Original data (read-only from package)
TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")

# Cleaned data (read/write from project root)
PROJECT_ROOT = Path(__file__).parents[3]  # Go up to project root
CLEAN_TAXI_CSV_PATH = PROJECT_ROOT / "data" / "taxi_trip_pricing_clean.csv"