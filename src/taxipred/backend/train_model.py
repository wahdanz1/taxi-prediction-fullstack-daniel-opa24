import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from taxipred.utils.constants import (
    CLEAN_TAXI_CSV_PATH,
    MODEL_PATH,
    ENCODERS_PATH,
    METRICS_PATH,
    FEATURE_IMPORTANCE_PATH
)

def load_and_prepare_cleaned_data():
    """Load and prepare the CLEANED dataset for final model training."""
    print("\n---------- Loading cleaned data for model training ----------")
    
    # Load cleaned data
    df = pd.read_csv(CLEAN_TAXI_CSV_PATH)
    
    # Separate features and target
    target = 'trip_price'  # Note: lowercase in cleaned data
    X = df.drop(columns=[target])
    y = df[target]
    
    print(f"Cleaned dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return X, y


def encode_categorical_features(X):
    """Encode categorical variables to numerical values."""
    print("\n---------- Encoding categorical features ----------")
    
    # Check which categorical columns actually exist in the dataset (case-insensitive)
    original_categorical_cols = ['Time_of_Day', 'Day_of_Week', 'Traffic_Conditions', 'Weather']
    lowercase_categorical_cols = ['time_of_day', 'day_of_week', 'traffic_conditions', 'weather']
    
    # Find existing categorical columns (try both cases)
    existing_categorical_cols = []
    for orig, lower in zip(original_categorical_cols, lowercase_categorical_cols):
        if orig in X.columns:
            existing_categorical_cols.append(orig)
        elif lower in X.columns:
            existing_categorical_cols.append(lower)
    
    # Also detect categorical columns by data type
    for col in X.columns:
        if X[col].dtype == 'object' and col not in existing_categorical_cols:
            existing_categorical_cols.append(col)
    
    encoders = {}
    X_encoded = X.copy()
    
    if existing_categorical_cols:
        for col in existing_categorical_cols:
            print(f"Encoding {col}...")
            encoders[col] = LabelEncoder()
            X_encoded[col] = encoders[col].fit_transform(X_encoded[col].astype(str))
        print(f"Encoding complete. Shape: {X_encoded.shape}")
    else:
        print("No categorical features found to encode.")
    
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


def analyze_feature_importance(best_model, X_encoded, encoders, phase="analysis"):
    """Show which features matter most for predictions."""
    if hasattr(best_model, 'feature_importances_'):
        feature_names = X_encoded.columns
        importances = best_model.feature_importances_
        
        print(f"\n--- Feature Importance Analysis ({phase} phase) ---")
        feature_importance_list = []
        for feature, importance in sorted(zip(feature_names, importances), 
                                        key=lambda x: x[1], reverse=True):
            print(f"{feature}: {importance:.4f} ({importance*100:.1f}%)")
            feature_importance_list.append((feature, importance))
        
        # Show cumulative importance
        sorted_importance = sorted(importances, reverse=True)
        cumulative = np.cumsum(sorted_importance)
        
        print(f"\nTop 3 features explain: {cumulative[2]*100:.1f}% of predictions")
        print(f"Top 5 features explain: {cumulative[4]*100:.1f}% of predictions")
        
        return feature_importance_list
    else:
        print(f"\n--- Feature Importance Analysis ({phase} phase) ---")
        print("Model doesn't support feature importance analysis")
        return []


def save_model_and_artifacts(best_model, encoders, results, feature_importance):
    """Save trained model and associated artifacts for deployment."""
    print("\n---------- Saving model and artifacts ----------")
    
    try:
        # Save the trained model
        joblib.dump(best_model, MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
        
        # Save encoders (empty dict for numerical-only data, but good for consistency)
        joblib.dump(encoders, ENCODERS_PATH)
        print(f"Encoders saved to {ENCODERS_PATH}")
        
        # Save model performance metrics for frontend display
        joblib.dump(results, METRICS_PATH)
        print(f"Model metrics saved to {METRICS_PATH}")
        
        # Save feature importance for frontend display
        joblib.dump(feature_importance, FEATURE_IMPORTANCE_PATH)
        print(f"Feature importance saved to {FEATURE_IMPORTANCE_PATH}")
        
        return True
        
    except Exception as e:
        print(f"Error saving model artifacts: {str(e)}")
        return False


def run_final_model_training():
    """Train final model on cleaned data."""
    print("\n" + "="*80)
    print("PRODUCTION MODEL TRAINING ON CLEANED DATA")
    print("="*80)
    
    # Load cleaned data
    X_clean, y_clean = load_and_prepare_cleaned_data()
    
    # Note: Cleaned data has only numerical features, so no encoding needed
    # But let's check anyway for consistency
    X_encoded, encoders = encode_categorical_features(X_clean)
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(X_encoded, y_clean)
    
    # Train and evaluate models
    results, trained_models = train_and_evaluate_models(X_train, X_test, y_train, y_test)
    
    # Find best model
    best_model, best_model_name, all_results = find_best_model(results, trained_models)
    
    # Analyze feature importance on final model
    final_feature_importance = analyze_feature_importance(best_model, X_encoded, encoders, "production")
    
    return best_model, encoders, all_results, final_feature_importance


def main():
    """Main training pipeline - train production model on cleaned data."""
    print("Training Taxi Price Prediction Model on Cleaned Data")
    print("Focus: High-quality model training on 967 clean, validated rows\n")
    
    # Train final model on cleaned data
    best_model, encoders, results, final_feature_importance = run_final_model_training()
    
    # Save model and artifacts for deployment
    # save_success = save_model_and_artifacts(best_model, encoders, results, final_feature_importance)
    
    # Summary
    print("\n" + "="*80)
    print("MODEL TRAINING COMPLETE")
    print("="*80)
    print(f"Production model trained on cleaned data")
    print(f"Encoders created: {len(encoders)} (should be 0 for numerical-only data)")
    print(f"Best model performance: ${results[min(results.keys(), key=lambda k: results[k]['mae'])]['mae']:.2f} MAE")
    
    # if save_success:
    #     print(f"Model artifacts saved successfully")
    #     print(f"Ready for FastAPI deployment and frontend integration")
    # else:
    #     print(f"Warning: Model training successful but saving failed")
    
    return best_model, encoders, results, final_feature_importance


if __name__ == "__main__":
    # Results dictionary with the purpose of serving it via FastAPI to the frontend later on
    best_model, encoders, results, feature_importance = main()
