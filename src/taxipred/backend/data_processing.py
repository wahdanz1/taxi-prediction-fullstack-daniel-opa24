from taxipred.utils.constants import CLEAN_TAXI_CSV_PATH
import pandas as pd
import json


class TaxiData:
    def __init__(self):
        self.df = pd.read_csv(CLEAN_TAXI_CSV_PATH)

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
