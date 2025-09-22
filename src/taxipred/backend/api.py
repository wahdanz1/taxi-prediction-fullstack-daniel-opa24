from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData

app = FastAPI()

taxi_data = TaxiData()

# Serve cleaned dataset
@app.get("/taxi/")
async def get_taxi_data():
    return taxi_data.to_json() # Return dataset


# Dataset info
@app.get("/taxi/stats")
async def show_stats():
    pass

# ML prediction
@app.post("/predict")
async def predict_price():
    # Transform input using encoders
    # Make prediction
    # Return result
    pass


# API Health Check endpoint
@app.get("/health")
async def health_check():
    pass