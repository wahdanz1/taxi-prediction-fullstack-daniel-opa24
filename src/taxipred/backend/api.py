from fastapi import FastAPI, HTTPException
from taxipred.backend.data_processing import TaxiData, InputModel, ResponseModel, SuggestionRequest, DistanceRequest
from taxipred.backend.google_services import suggest_address, get_distance

app = FastAPI(
    title="TaxiPred API",
    description="AI-powered taxi fare prediction API with location services",
    version="1.2.0"
)

taxi_data = TaxiData()


@app.get("/health")
async def health_check() -> dict:
    """API health check endpoint."""
    return {"status": "healthy", "service": "TaxiPred API"}


@app.get("/taxi/")
async def get_taxi_data() -> list:
    """
    Retrieve the cleaned taxi dataset in JSON format.
    
    Returns:
        List of taxi trip records with all features used for training
    """
    return taxi_data.to_json()


@app.get("/taxi/stats")
async def get_dataset_stats() -> dict:
    """
    Get statistical summary of the taxi dataset.
    
    Returns:
        Dataset statistics including record counts, price distribution, and distance metrics
    """
    try:
        return taxi_data.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@app.post("/predict", response_model=ResponseModel)
async def predict_fare(input_data: InputModel) -> ResponseModel:
    """
    Predict taxi fare using ML model.
    
    Uses trained model with engineered features including distance, time factors,
    weather conditions, and traffic patterns to estimate fare price.
    
    Args:
        input_data: Trip details including distance, passengers, datetime, weather, and traffic
        
    Returns:
        Fare prediction with detailed breakdown of factors considered
        
    Raises:
        HTTPException: 400 for invalid input, 500 for prediction errors
    """
    try:
        result = taxi_data.predict_price(
            input_data.trip_distance_km,
            input_data.passenger_count,
            input_data.pickup_datetime,
            input_data.weather,
            input_data.traffic_conditions
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/suggestion")
async def get_address_suggestions(request: SuggestionRequest) -> dict:
    """
    Get address suggestions using Google Places API.
    
    Provides autocomplete suggestions for Swedish addresses to improve
    user experience when entering pickup and destination locations.
    
    Args:
        request: Address search query
        
    Returns:
        Dictionary containing list of address suggestions
    """
    try:
        suggestions = suggest_address(request.query)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Address suggestion error: {str(e)}")


@app.post("/distance")
async def calculate_trip_distance(request: DistanceRequest) -> dict:
    """
    Calculate driving distance between two addresses.
    
    Uses Google Distance Matrix API to compute actual road distance
    rather than straight-line distance for accurate fare prediction.
    
    Args:
        request: Origin and destination addresses
        
    Returns:
        Dictionary containing distance in kilometers
        
    Raises:
        HTTPException: 400 if distance cannot be calculated, 500 for API errors
    """
    try:
        distance = get_distance(request.origin, request.destination)
        if distance is None:
            raise HTTPException(status_code=400, detail="Could not calculate distance between addresses")
        return {"distance_km": distance}
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Distance calculation error: {str(e)}")
