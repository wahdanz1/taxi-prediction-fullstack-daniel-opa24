from pathlib import Path
from importlib.resources import files

# Original data (read-only from package)
TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")

# For cleaned data - use the same package location
CLEAN_TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing_clean.csv")