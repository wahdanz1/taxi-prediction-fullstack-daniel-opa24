MODEL_DESCRIPTIONS = {
    "LinearRegression": "Assumes price increases linearly with distance (like $2/km always). Works well for simple relationships, but taxi pricing has many interacting factors (traffic, time, weather) that make this approach less suitable.",
    
    "RandomForest": "Uses multiple decision trees - like having 100 taxi drivers each make an estimate, then averaging. Each considers different factor combinations. Handles complex interactions better than linear approaches.",
    
    "GradientBoosting": "Builds estimates iteratively, learning from mistakes. Makes a rough estimate, analyzes errors, creates a second model to fix them, repeats. Often most accurate but risks overfitting if not carefully tuned."
}

GLOSSARY_TERMS = {
    "Linear relationships": "Price changes at a constant rate (e.g., $2 per km, always)",
    
    "Non-linear relationships": "Price doesn't increase constantly (first 10km might be $3/km, next 10km $2/km due to highway driving)",
    
    "Complex patterns": "Multiple factors influence each other (distance matters more during rush hour, weather affects travel time)",
    
    "Subset": "A portion of the full dataset (e.g., 70% for training, 30% for testing)",
    
    "Mixed data types": "Combination of numbers (distance, price) and categories (weather types, time periods)",
    
    "Overfitting": "Model memorizes specific examples rather than learning general patterns"
}