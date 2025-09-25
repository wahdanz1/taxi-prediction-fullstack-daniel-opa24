import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
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


def load_cleaned_data():
    """
    Load cleaned numerical dataset for model training.
    
    Returns:
        tuple: Feature matrix (X) and target vector (y)
    """
    print("Loading cleaned numerical data for model training...")
    
    df = pd.read_csv(CLEAN_TAXI_CSV_PATH)
    
    # Separate features and target
    target = 'trip_price'
    X = df.drop(columns=[target])
    y = df[target]
    
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Verify all features are numerical
    non_numeric = X.select_dtypes(include=['object']).columns
    if len(non_numeric) == 0:
        print("Confirmed: All features are numerical - no encoding required")
    else:
        print(f"Warning: Found non-numeric columns: {list(non_numeric)}")
    
    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    """
    Split data into training and testing sets.
    
    Args:
        X: Feature matrix
        y: Target vector
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
        
    Returns:
        tuple: X_train, X_test, y_train, y_test
    """
    print("Splitting dataset...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test


def get_models():
    """
    Define regression models for comparison.
    
    Returns:
        dict: Model name to model instance mapping
    """
    return {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(random_state=42)
    }


def evaluate_model(model, X_test, y_test, model_name):
    """
    Evaluate trained model performance.
    
    Args:
        model: Trained model instance
        X_test: Test features
        y_test: Test targets
        model_name: Name for logging
        
    Returns:
        dict: Performance metrics (MAE, RMSE, R²)
    """
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    print(f"{model_name}: MAE=${mae:.2f}, RMSE=${rmse:.2f}, R²={r2:.3f}")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}


def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    """
    Train multiple models and compare performance.
    
    Args:
        X_train: Training features
        X_test: Test features  
        y_train: Training targets
        y_test: Test targets
        
    Returns:
        tuple: (results dict, trained models dict)
    """
    print("\nTraining and evaluating models...")
    
    models = get_models()
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
        results[name] = evaluate_model(model, X_test, y_test, name)
    
    return results, trained_models


def find_best_model(results, trained_models):
    """
    Identify best performing model based on MAE.
    
    Args:
        results: Performance metrics for each model
        trained_models: Dictionary of trained models
        
    Returns:
        tuple: (best_model, best_model_name, results)
    """
    print("\nModel comparison:")
    
    best_model_name = min(results.keys(), key=lambda k: results[k]['mae'])
    best_model = trained_models[best_model_name]
    
    print(f"Best model: {best_model_name} (MAE: ${results[best_model_name]['mae']:.2f})")
    
    return best_model, best_model_name, results


def analyze_feature_importance(model, feature_columns):
    """
    Analyze and display feature importance if supported by model.
    
    Args:
        model: Trained model instance
        feature_columns: Column names for features
        
    Returns:
        list: Feature importance pairs (name, importance)
    """
    if not hasattr(model, 'feature_importances_'):
        print("\nFeature importance analysis: Not supported by this model")
        return []
    
    print("\nFeature importance analysis:")
    
    importances = model.feature_importances_
    feature_importance_list = []
    
    for feature, importance in sorted(zip(feature_columns, importances), 
                                    key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {importance:.4f} ({importance*100:.1f}%)")
        feature_importance_list.append((feature, importance))
    
    # Show cumulative importance of top features
    sorted_importance = sorted(importances, reverse=True)
    cumulative = np.cumsum(sorted_importance)
    
    print(f"\nTop 3 features explain: {cumulative[2]*100:.1f}% of predictions")
    if len(cumulative) >= 5:
        print(f"Top 5 features explain: {cumulative[4]*100:.1f}% of predictions")
    
    return feature_importance_list


def save_model_artifacts(model, results, feature_importance):
    """
    Save trained model and associated artifacts for deployment.
    
    Args:
        model: Best performing trained model
        results: All model performance metrics
        feature_importance: Feature importance analysis results
        
    Returns:
        bool: Success status
    """
    print("\nSaving model and artifacts...")
    
    try:
        # Save trained model
        joblib.dump(model, MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
        
        # Save empty encoders (no encoding needed for numerical data)
        encoders = {}
        joblib.dump(encoders, ENCODERS_PATH)
        print(f"Encoders saved to {ENCODERS_PATH}")
        
        # Save performance metrics
        joblib.dump(results, METRICS_PATH)
        print(f"Metrics saved to {METRICS_PATH}")
        
        # Save feature importance
        joblib.dump(feature_importance, FEATURE_IMPORTANCE_PATH)
        print(f"Feature importance saved to {FEATURE_IMPORTANCE_PATH}")
        
        return True
        
    except Exception as e:
        print(f"Error saving artifacts: {str(e)}")
        return False


def train_production_model():
    """
    Complete model training pipeline for production deployment.
    
    Returns:
        tuple: (best_model, results, feature_importance)
    """
    print("="*60)
    print("TAXI PRICE PREDICTION MODEL TRAINING")
    print("="*60)
    
    # Load cleaned data
    X, y = load_cleaned_data()
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Train and evaluate models
    results, trained_models = train_and_evaluate_models(X_train, X_test, y_train, y_test)
    
    # Select best model
    best_model, best_model_name, all_results = find_best_model(results, trained_models)
    
    # Analyze feature importance
    feature_importance = analyze_feature_importance(best_model, X.columns)
    
    return best_model, all_results, feature_importance


def main():
    """
    Main training pipeline - train and save production model.
    
    Returns:
        tuple: (best_model, results, feature_importance)
    """
    print("Training Taxi Price Prediction Model")
    print("Objective: Train production model on cleaned, engineered dataset\n")
    
    # Train production model
    best_model, results, feature_importance = train_production_model()
    
    # Save artifacts for deployment
    save_success = save_model_artifacts(best_model, results, feature_importance)
    
    # Summary
    best_mae = min(results[model]['mae'] for model in results)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print(f"Best model performance: ${best_mae:.2f} MAE")
    print(f"Model artifacts saved: {'Success' if save_success else 'Failed'}")
    
    if save_success:
        print("Ready for FastAPI deployment")
    else:
        print("Warning: Training succeeded but artifact saving failed")
    
    return best_model, results, feature_importance


if __name__ == "__main__":
    main()
