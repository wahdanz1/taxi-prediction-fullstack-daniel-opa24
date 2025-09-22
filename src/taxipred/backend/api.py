from fastapi import FastAPI, HTTPException
from taxipred.backend.data_processing import TaxiData

# Initialize the FastAPI app instance
app = FastAPI(
    title="TaxiPred API",
    description="Taxi price prediction API",
    version="1.0.0"
)

taxi_data = TaxiData()

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
@app.post("/predict")
async def predict_price():
    # Transform input using encoders
    # Make prediction
    # Return result
    # --- Placeholder for now
    return {"estimated_price": 45.50, "status": "prediction_placeholder"}


# API Health Check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TaxiPred API"}