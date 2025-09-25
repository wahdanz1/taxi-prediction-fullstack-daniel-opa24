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
    """
    Handles taxi dataset operations and ML predictions.
    
    Manages the cleaned taxi dataset, trained model artifacts, and provides
    fare prediction functionality with proper feature engineering.
    """
    
    def __init__(self):
        """Initialize TaxiData with cleaned dataset and model artifacts."""
        self.df = pd.read_csv(CLEAN_TAXI_CSV_PATH)
        self.model = None
        self.model_metrics = None 
        self.feature_importance = None
        self._load_model_artifacts()

    def _load_model_artifacts(self):
        """Load trained model, metrics, and feature importance from disk."""
        try:
            self.model = joblib.load(MODEL_PATH)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Model load error: {e}")
        
        try:
            self.model_metrics = joblib.load(METRICS_PATH)
        except Exception as e:
            print(f"Model metrics load error: {e}")
        
        try:
            self.feature_importance = joblib.load(FEATURE_IMPORTANCE_PATH)
        except Exception as e:
            print(f"Feature importance load error: {e}")

    def _engineer_features_from_input(self, trip_distance_km: float, passenger_count: int,
                                    pickup_datetime: datetime, weather: str, traffic_conditions: str):
        """
        Convert user inputs into engineered features matching training data.
        
        Creates the same feature set used during model training, including
        time-based features, weather/traffic multipliers, and interaction terms.
        
        Args:
            trip_distance_km: Distance of the trip in kilometers
            passenger_count: Number of passengers
            pickup_datetime: Pickup date and time
            weather: Weather condition ("Clear", "Rain", "Snow")
            traffic_conditions: Traffic level ("Low", "Medium", "High")
            
        Returns:
            dict: Engineered features ready for model prediction
        """
        hour = pickup_datetime.hour
        weekday = pickup_datetime.weekday()

        # Determine time period
        if 6 <= hour < 12:
            time_of_day = "Morning"
        elif 12 <= hour < 18:
            time_of_day = "Afternoon"
        elif 18 <= hour < 24:
            time_of_day = "Evening"
        else:
            time_of_day = "Night"

        # Create time-based binary features
        is_morning_rush = 1 if time_of_day == "Morning" else 0
        is_evening_rush = 1 if time_of_day == "Evening" else 0
        is_peak_hours = 1 if is_morning_rush or is_evening_rush else 0
        is_weekend = 1 if weekday > 4 else 0

        # Apply weather and traffic multipliers
        weather_impact = {"Clear": 1.0, "Rain": 1.15, "Snow": 1.3}[weather]
        traffic_multiplier = {"Low": 1.0, "Medium": 1.1, "High": 1.25}[traffic_conditions]

        # Create interaction features
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
        """
        Predict taxi fare using the trained ML model.
        
        Args:
            trip_distance_km: Trip distance in kilometers (must be > 0)
            passenger_count: Number of passengers
            pickup_datetime: Pickup date and time
            weather: Weather condition (default: "Clear")
            traffic_conditions: Traffic level (default: "Medium")
            
        Returns:
            ResponseModel: Prediction results with trip details
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If distance is <= 0
        """
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        if trip_distance_km <= 0:
            raise ValueError("Distance must be greater than 0 km")
        
        # Engineer features to match training data
        features = self._engineer_features_from_input(
            trip_distance_km, passenger_count, pickup_datetime, weather, traffic_conditions
        )
        
        # Create DataFrame with correct column order
        feature_columns = [col for col in self.df.columns if col != "trip_price"]
        feature_values = [features[col] for col in feature_columns]
        df = pd.DataFrame([feature_values], columns=feature_columns)
        
        # Make prediction
        predicted_price = float(self.model.predict(df)[0])
        
        # Prepare response data
        trip_details = {
            "original_distance": trip_distance_km,
            "original_passengers": passenger_count, 
            "pickup_time": pickup_datetime.strftime("%Y-%m-%d %H:%M"),
            "weather_used": weather,
            "traffic_used": traffic_conditions,
            "weather_impact_multiplier": features["weather_impact"],
            "is_rush_hour": bool(features["is_peak_hours"]),
        }
        
        return ResponseModel(
            estimated_price=predicted_price, 
            trip_details=trip_details, 
            status="Prediction completed!"
        )

    def to_json(self):
        """Convert dataset to JSON format for API responses."""
        return json.loads(self.df.to_json(orient="records"))

    def get_stats(self):
        """
        Get dataset statistics for API endpoints.
        
        Returns:
            dict: Dataset statistics including record count, price stats, and distance stats
        """
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


# Pydantic models for API validation
class InputModel(BaseModel):
    """Validation model for taxi fare prediction requests."""
    trip_distance_km: float = Field(gt=0, description="Trip distance in kilometers")
    passenger_count: int = Field(gt=0, lt=5, description="Number of passengers (1-4)")
    pickup_datetime: datetime = Field(description="Pickup date and time")
    weather: str = Field(default="Clear", description="Weather condition")
    traffic_conditions: str = Field(default="Medium", description="Traffic level")


class ResponseModel(BaseModel):
    """Response model for taxi fare predictions."""
    estimated_price: float = Field(description="Predicted fare in currency units")
    trip_details: dict = Field(description="Details about the trip and prediction factors")
    status: str = Field(description="Prediction status message")


# Pydantic models for Google Services API
class SuggestionRequest(BaseModel):
    """Request model for address suggestions."""
    query: str = Field(description="Address search query")


class DistanceRequest(BaseModel):
    """Request model for distance calculations."""
    origin: str = Field(description="Origin address")
    destination: str = Field(description="Destination address")