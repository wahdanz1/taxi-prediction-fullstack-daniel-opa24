import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from taxipred.utils.constants import CLEAN_TAXI_CSV_PATH


def load_and_prepare_data():
    """Load and prepare the dataset for training."""
    print("\n---------- Loading and preparing data ----------")
    
    # Load data
    df = pd.read_csv(CLEAN_TAXI_CSV_PATH)
    
    # Separate features and target
    target = 'trip_price'
    X = df.drop(columns=[target])
    y = df[target]
    
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return X, y


def encode_categorical_features(X):
    """Encode categorical variables to numerical values."""
    print("\n---------- Encoding categorical features ----------")
    
    categorical_cols = ['time_of_day', 'day_of_week', 'traffic_conditions', 'weather']
    encoders = {}
    X_encoded = X.copy()
    
    for col in categorical_cols:
        print(f"Encoding {col}...")
        encoders[col] = LabelEncoder()
        X_encoded[col] = encoders[col].fit_transform(X_encoded[col])
    
    print(f"Encoding complete. Shape: {X_encoded.shape}")
    return X_encoded, encoders


def split_data(X, y):
    """Split data into training and testing sets."""
    print("\n---------- Splitting dataset ----------")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test


def get_models():
    """Define models to train and compare."""
    return {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(random_state=42)
    }
    # ----- Model Explanations for PO -----
    # LinearRegression
    # Assumes that price increases in a straight line with distance (like $2 per km always).
    # Works well when relationships are simple and predictable, but taxi pricing has many factors
    # that interact in complex ways (traffic, time of day, weather all affect each other).
    # This makes it less suitable for our taxi pricing problem.
    #
    # RandomForest
    # Uses multiple "decision trees" - imagine having 100 different taxi drivers each make a price
    # estimate, then taking the average. Each driver considers different combinations of factors
    # (some focus on distance + time, others on weather + traffic). This approach handles the
    # complex interactions in taxi pricing much better than simple straight-line thinking.
    #
    # GradientBoosting (Best Performer)
    #Learns from mistakes by building estimates step-by-step. First, it makes a rough price estimate.
    # Then it looks at where it was wrong and creates a second model to fix those errors. It repeats
    # this process, getting more accurate each time. This often gives the most accurate predictions
    # but requires careful setup to avoid memorizing the training data too closely.
    #
    # ----- Glossary for Non-Technical Stakeholders -----
    # Linear relationships:
    # Price changes at a constant rate (like $2 per km, always)
    #
    # Complex patterns:
    # When multiple factors influence each other (distance matters
    # more during rush hour, weather affects travel time, etc.)
    # 
    # Non-linear relationships:
    # Price doesn't increase at a constant rate (first 10km might
    # be $3/km, next 10km might be $2/km due to highway driving)
    # 
    # Subset:
    # A smaller portion of the full dataset (like using 70% of trips to train, 30% to test)
    # 
    # Mixed data types:
    # Combination of numbers (distance, price) and categories (weather: sunny/rainy, time: morning/evening)
    # 
    # Overfitting:
    # When the model memorizes specific examples too closely instead of learning
    # general patterns, like a student who memorizes answers but can't solve new problems


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate a trained model and return metrics."""
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    print(f"{model_name}:")
    print(f"  MAE: ${mae:.2f}")
    print(f"  RMSE: ${rmse:.2f}")
    print(f"  R²: {r2:.3f}")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}


def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    """Train multiple models and evaluate their performance."""
    print("\n---------- Training and evaluating models ----------")
    
    models = get_models()
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        
        # Train model
        model.fit(X_train, y_train)
        trained_models[name] = model
        
        # Evaluate model
        results[name] = evaluate_model(model, X_test, y_test, name)
    
    return results, trained_models


def find_best_model(results, trained_models):
    """Find and return the best performing model."""
    print("\n---------- Model comparison ----------")
    
    best_model_name = min(results.keys(), key=lambda k: results[k]['mae'])
    best_model = trained_models[best_model_name]
    
    print(f"Best model: {best_model_name}")
    print(f"Best MAE: ${results[best_model_name]['mae']:.2f}")
    
    return best_model, best_model_name, results


def main():
    """Main training pipeline."""
    # Load and prepare data
    X, y = load_and_prepare_data()
    
    # Encode categorical features
    X_encoded, encoders = encode_categorical_features(X)
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(X_encoded, y)
    
    # Train and evaluate models
    results, trained_models = train_and_evaluate_models(X_train, X_test, y_train, y_test)
    
    # Find best model
    best_model, best_model_name, all_results = find_best_model(results, trained_models)
    
    return best_model, encoders, all_results


if __name__ == "__main__":
    # Results dictionary with the purpose of serving it via FastAPI to the frontend later on
    best_model, encoders, results = main()
