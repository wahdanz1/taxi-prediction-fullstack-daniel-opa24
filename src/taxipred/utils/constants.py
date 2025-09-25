from pathlib import Path
from importlib.resources import files

API_BASE_URL = "http://127.0.0.1:8000"

# Original data (read-only from package)
TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing.csv")

# For cleaned data - use the same package location
CLEAN_TAXI_CSV_PATH = files("taxipred").joinpath("data/taxi_trip_pricing_clean.csv")

# Trained Model Artifacts
MODEL_PATH = files("taxipred").joinpath("backend/models/taxi_price_model.joblib")
ENCODERS_PATH = files("taxipred").joinpath("backend/models/encoders.joblib") 
METRICS_PATH = files("taxipred").joinpath("backend/models/model_metrics.joblib")
FEATURE_IMPORTANCE_PATH = files("taxipred").joinpath("backend/models/feature_importance.joblib")