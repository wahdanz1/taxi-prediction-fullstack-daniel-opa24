from pydantic import BaseModel, Field
from datetime import datetime
import pandas as pd
import json
import joblib

from taxipred.utils.constants import (
    CLEAN_TAXI_CSV_PATH,
    MODEL_PATH,
    METRICS_PATH,
    FEATURE_IMPORTANCE_PATH
)

class TaxiData:
    def __init__(self):
        self.df = pd.read_csv(CLEAN_TAXI_CSV_PATH)
        self.model = None
        self.model_metrics = None 
        self.feature_importance = None
        self._load_model_artifacts()

    def _load_model_artifacts(self):
        try:
            self.model = joblib.load(MODEL_PATH)
            print("Model loaded successfully!")
        except Exception as me:
            print(f"Model load error: {me}")
        
        try:
            self.model_metrics = joblib.load(METRICS_PATH)
        except Exception as mme:
            print(f"Model Metrics load error: {mme}")
        
        try:
            self.feature_importance = joblib.load(FEATURE_IMPORTANCE_PATH)
        except Exception as fie:
            print(f"Feature Importance load error: {fie}")

    def _engineer_features_from_input(self, trip_distance_km: float, passenger_count: int,
                                    pickup_datetime: datetime, weather: str, traffic_conditions: str):
        """Convert user inputs into the same engineered features used in training."""
        # Extract time info from datetime
        hour = pickup_datetime.hour
        weekday = pickup_datetime.weekday()

        # Determine time_of_day
        if 6 <= hour < 12:
            time_of_day = "Morning"
        elif 12 <= hour < 18:
            time_of_day = "Afternoon"
        elif 18 <= hour < 24:
            time_of_day = "Evening"
        else:
            time_of_day = "Night"

        # Binary features
        is_morning_rush = 1 if time_of_day == "Morning" else 0
        is_evening_rush = 1 if time_of_day == "Evening" else 0
        is_peak_hours = 1 if is_morning_rush or is_evening_rush else 0
        is_weekend = 1 if weekday > 4 else 0

        # Map weather and traffic
        weather_impact = {"Clear": 1.0, "Rain": 1.15, "Snow": 1.3}[weather]
        traffic_multiplier = {"Low": 1.0, "Medium": 1.1, "High": 1.25}[traffic_conditions]

        # Interaction features
        condition_score = weather_impact * traffic_multiplier
        distance_x_conditions = trip_distance_km * condition_score
        high_impact_trip = 1 if weather == "Snow" or traffic_conditions == "High" else 0

        return {
            "trip_distance_km": trip_distance_km,
            "passenger_count": passenger_count,
            "weather_impact": weather_impact,
            "traffic_multiplier": traffic_multiplier,
            "is_morning_rush": is_morning_rush,
            "is_evening_rush": is_evening_rush,
            "is_peak_hours": is_peak_hours,
            "is_weekend": is_weekend,
            "high_impact_trip": high_impact_trip,
            "condition_score": condition_score,
            "distance_x_conditions": distance_x_conditions
        }
    
    def predict_price(self, trip_distance_km: float, passenger_count: int, pickup_datetime: datetime,
                    weather: str = "Clear", traffic_conditions: str = "Medium"):
        """Predict taxi fare using the trained model."""
        # Validation
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        if trip_distance_km <= 0:
            raise ValueError("Distance has to be more than 0 km.")
        
        # Engineer features
        features = self._engineer_features_from_input(trip_distance_km, passenger_count, pickup_datetime, weather, traffic_conditions)
        
        # DataFrame with correct column order
        list_of_column_names = [col for col in self.df.columns if col != "trip_price"]
        list_of_values = [features[col] for col in list_of_column_names]
        df = pd.DataFrame([list_of_values], columns=list_of_column_names)
        
        # Predict
        predicted_price = self.model.predict(df)[0]
        
        # Return response using ResponseModel
        trip_details = {
            "original_distance": trip_distance_km,
            "original_passengers": passenger_count, 
            "pickup_time": pickup_datetime.strftime("%Y-%m-%d %H:%M"),
            "weather_used": weather,
            "traffic_used": traffic_conditions,
            "weather_impact_multiplier": features["weather_impact"],
            "is_rush_hour": bool(features["is_peak_hours"]),
        }
        predicted_price = float(predicted_price)
        response = ResponseModel(estimated_price=predicted_price, trip_details=trip_details, status="Prediction completed!")
        
        return response

    def to_json(self):
        return json.loads(self.df.to_json(orient = "records"))

    def get_stats(self):
        try:
            return {
                "total_records": int(len(self.df)),
                "columns": list(self.df.columns),
                "price_stats": {
                    "min": float(self.df['trip_price'].min()),
                    "max": float(self.df['trip_price'].max()),
                    "mean": float(self.df['trip_price'].mean()),
                    "median": float(self.df['trip_price'].median())
                },
                "distance_stats": {
                    "min": float(self.df['trip_distance_km'].min()),
                    "max": float(self.df['trip_distance_km'].max()),
                    "mean": float(self.df['trip_distance_km'].mean())
                }
            }
        except Exception as e:
            print(f"Error in get_stats: {e}")
            return {"error": str(e)}


# Pydantic model for user input
class InputModel(BaseModel):
    trip_distance_km: float = Field(gt=0)
    passenger_count: int = Field(gt=0, lt=5)
    pickup_datetime: datetime
    weather: str = "Clear"
    traffic_conditions: str = "Medium"

# Pydantic model for reponse after prediction
class ResponseModel(BaseModel):
    estimated_price: float
    trip_details: dict
    status: str

# Pydantic models for Google Services
class SuggestionRequest(BaseModel):
    query: str

class DistanceRequest(BaseModel):
    origin: str
    destination: str
