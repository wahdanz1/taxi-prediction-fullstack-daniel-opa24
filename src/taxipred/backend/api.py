from fastapi import FastAPI, HTTPException
from taxipred.backend.data_processing import TaxiData, InputModel, ResponseModel, SuggestionRequest, DistanceRequest
from taxipred.backend.google_services import suggest_address, get_distance

# Initialize the FastAPI app instance
app = FastAPI(
    title="TaxiPred API",
    description="Taxi price prediction API",
    version="1.0.0"
)

taxi_data = TaxiData()

# API Health Check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TaxiPred API"}


# Serve cleaned dataset
@app.get("/taxi/")
async def get_taxi_data():
    return taxi_data.to_json()


# Dataset info
@app.get("/taxi/stats")
async def show_stats():
    try:
        stats = taxi_data.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


# ML prediction
@app.post("/predict", response_model=ResponseModel)
async def predict_price(input_data: InputModel):
    try:
        result = taxi_data.predict_price(
            input_data.trip_distance_km,
            input_data.passenger_count,
            input_data.pickup_datetime,
            input_data.weather,
            input_data.traffic_conditions
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Bad Request: {str(ve)}")
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(re)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/suggestion")
async def get_address_suggestions(request: SuggestionRequest):
    try:
        suggestions = suggest_address(request.query)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion error: {str(e)}")


@app.post("/distance") 
async def get_trip_distance(request: DistanceRequest):
    try:
        distance = get_distance(request.origin, request.destination)
        if distance is None:
            raise HTTPException(status_code=400, detail="Could not calculate distance")
        return {"distance_km": distance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Distance calculation error: {str(e)}")