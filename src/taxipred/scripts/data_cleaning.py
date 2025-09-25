import pandas as pd
from taxipred.utils.constants import TAXI_CSV_PATH, CLEAN_TAXI_CSV_PATH


def fill_missing_pricing_components(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing pricing components using taxi fare formula.
    
    Uses the relationship: trip_price = base_fare + (distance x per_km_rate) + (duration x per_minute_rate)
    to calculate missing values when other components are available.
    
    Args:
        df: DataFrame with potentially missing pricing components
        
    Returns:
        DataFrame with calculated missing pricing values
    """
    df = df.copy()
    filled_count = 0
    calculation_details = {
        'trip_price': 0, 'base_fare': 0, 'per_km_rate': 0,
        'per_minute_rate': 0, 'trip_distance_km': 0, 'trip_duration_minutes': 0
    }
    
    for idx, row in df.iterrows():
        pricing_cols = ['base_fare', 'per_km_rate', 'per_minute_rate', 'trip_distance_km', 'trip_duration_minutes']
        
        # Calculate missing trip_price if all components are present
        if pd.isna(row['trip_price']) and all(pd.notna(row[col]) for col in pricing_cols):
            calculated_price = (row['base_fare'] + 
                              (row['trip_distance_km'] * row['per_km_rate']) + 
                              (row['trip_duration_minutes'] * row['per_minute_rate']))
            df.loc[idx, 'trip_price'] = calculated_price
            filled_count += 1
            calculation_details['trip_price'] += 1
            
        elif pd.isna(row['trip_price']):
            continue  # Can't calculate other components without trip_price
            
        # Calculate missing distance by reversing the formula
        elif (pd.isna(row['trip_distance_km']) and 
              all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_km_rate', 'per_minute_rate', 'trip_duration_minutes'])):
            if row['per_km_rate'] != 0:
                calculated_distance = ((row['trip_price'] - row['base_fare'] - 
                                       (row['trip_duration_minutes'] * row['per_minute_rate'])) / 
                                        row['per_km_rate'])
                if calculated_distance > 0:
                    df.loc[idx, 'trip_distance_km'] = calculated_distance
                    filled_count += 1
                    calculation_details['trip_distance_km'] += 1
        
        # Calculate missing duration by reversing the formula  
        elif (pd.isna(row['trip_duration_minutes']) and 
              all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_km_rate', 'per_minute_rate', 'trip_distance_km'])):
            if row['per_minute_rate'] != 0:
                calculated_duration = ((row['trip_price'] - row['base_fare'] - 
                                      (row['trip_distance_km'] * row['per_km_rate'])) / 
                                       row['per_minute_rate'])
                if calculated_duration > 0:
                    df.loc[idx, 'trip_duration_minutes'] = calculated_duration
                    filled_count += 1
                    calculation_details['trip_duration_minutes'] += 1
        
        # Calculate missing base fare
        elif (pd.isna(row['base_fare']) and 
              all(pd.notna(row[col]) for col in ['trip_price', 'per_km_rate', 'per_minute_rate', 'trip_distance_km', 'trip_duration_minutes'])):
            calculated_base_fare = (row['trip_price'] - 
                                   (row['trip_distance_km'] * row['per_km_rate']) - 
                                   (row['trip_duration_minutes'] * row['per_minute_rate']))
            df.loc[idx, 'base_fare'] = max(0, calculated_base_fare)
            filled_count += 1
            calculation_details['base_fare'] += 1
        
        # Calculate missing per-km rate
        elif (pd.isna(row['per_km_rate']) and 
              all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_minute_rate', 'trip_distance_km', 'trip_duration_minutes'])):
            if row['trip_distance_km'] > 0:
                calculated_per_km = ((row['trip_price'] - row['base_fare'] - 
                                     (row['trip_duration_minutes'] * row['per_minute_rate'])) / 
                                    row['trip_distance_km'])
                df.loc[idx, 'per_km_rate'] = max(0, calculated_per_km)
                filled_count += 1
                calculation_details['per_km_rate'] += 1
        
        # Calculate missing per-minute rate
        elif (pd.isna(row['per_minute_rate']) and 
              all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_km_rate', 'trip_distance_km', 'trip_duration_minutes'])):
            if row['trip_duration_minutes'] > 0:
                calculated_per_minute = ((row['trip_price'] - row['base_fare'] - 
                                        (row['trip_distance_km'] * row['per_km_rate'])) / 
                                        row['trip_duration_minutes'])
                df.loc[idx, 'per_minute_rate'] = max(0, calculated_per_minute)
                filled_count += 1
                calculation_details['per_minute_rate'] += 1
    
    if filled_count > 0:
        print(f"Calculated {filled_count} missing pricing components using fare formula:")
        for component, count in calculation_details.items():
            if count > 0:
                print(f"  - {component}: {count} values")
    
    return df


def clean_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing categorical and passenger values with sensible defaults.
    
    Args:
        df: DataFrame with missing categorical values
        
    Returns:
        DataFrame with filled categorical features
    """
    df = df.copy()
    total_filled = 0
    
    categorical_defaults = {
        'time_of_day': 'Afternoon',
        'day_of_week': 'Weekday',
        'traffic_conditions': 'Medium',
        'weather': 'Clear'
    }
    
    for col, default in categorical_defaults.items():
        missing = df[col].isnull().sum()
        if missing > 0:
            fill_value = df[col].mode()[0] if not df[col].mode().empty else default
            df[col] = df[col].fillna(fill_value)
            total_filled += missing
    
    # Fill passenger count with median
    missing_passengers = df['passenger_count'].isnull().sum()
    if missing_passengers > 0:
        df['passenger_count'] = df['passenger_count'].fillna(df['passenger_count'].median())
        total_filled += missing_passengers
    
    if total_filled > 0:
        print(f"Filled {total_filled} missing categorical/passenger values")
    
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features for improved model performance.
    
    Generates weather/traffic multipliers, time-based indicators, 
    and interaction features that capture pricing patterns.
    
    Args:
        df: DataFrame with categorical features
        
    Returns:
        DataFrame with additional engineered features
    """
    df = df.copy()
    print("Creating engineered features...")
    
    # Weather and traffic impact multipliers
    df['weather_impact'] = df['weather'].map({'Clear': 1.0, 'Rain': 1.15, 'Snow': 1.3})
    df['traffic_multiplier'] = df['traffic_conditions'].map({'Low': 1.0, 'Medium': 1.1, 'High': 1.25})
    
    # Time-based binary features
    df['is_morning_rush'] = (df['time_of_day'] == 'Morning').astype(int)
    df['is_evening_rush'] = (df['time_of_day'] == 'Evening').astype(int)
    df['is_peak_hours'] = (df['is_morning_rush'] | df['is_evening_rush']).astype(int)
    df['is_weekend'] = (df['day_of_week'] == 'Weekend').astype(int)
    
    # High-impact trip indicator
    df['high_impact_trip'] = ((df['weather'] == 'Snow') | (df['traffic_conditions'] == 'High')).astype(int)
    
    # Interaction features
    df['condition_score'] = df['weather_impact'] * df['traffic_multiplier']
    df['distance_x_conditions'] = df['trip_distance_km'] * df['condition_score']
    
    print("Added 8 engineered features")
    return df


def clean_dataset(input_path: str = TAXI_CSV_PATH, output_path: str = CLEAN_TAXI_CSV_PATH) -> pd.DataFrame:
    """
    Clean raw taxi dataset for ML training.
    
    Implements a comprehensive cleaning pipeline that handles missing values,
    prevents data leakage, and creates engineered features for improved prediction.
    
    Process:
    1. Remove impossible values (negative prices/distances) 
    2. Use pricing formula to recover missing components
    3. Drop pricing components to prevent data leakage
    4. Fill categorical features with sensible defaults
    5. Engineer interaction and time-based features
    6. Final validation and cleanup
    
    Args:
        input_path: Path to raw taxi CSV file
        output_path: Path for cleaned output CSV
        
    Returns:
        Cleaned DataFrame ready for ML training
    """
    print("Loading raw data...")
    df = pd.read_csv(input_path)
    print(f"Original dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Standardize column names
    df.columns = df.columns.str.lower()
    
    # Report initial missing values
    print(f"\nInitial missing values:")
    missing_summary = df.isnull().sum()
    for col, missing_count in missing_summary.items():
        if missing_count > 0:
            print(f"  {col}: {missing_count}")
    
    # Remove impossible core values while keeping missing ones for recovery
    print("\nRemoving rows with impossible core trip values...")
    initial_rows = len(df)
    df_valid = df[
        ((df['trip_price'].isnull()) | (df['trip_price'] > 0)) &
        ((df['trip_distance_km'].isnull()) | (df['trip_distance_km'] > 0)) &
        ((df['trip_duration_minutes'].isnull()) | (df['trip_duration_minutes'] > 0))
    ].copy()
    
    removed_impossible = initial_rows - len(df_valid)
    print(f"Removed {removed_impossible} rows with impossible values")
    
    # Recover missing pricing components using domain knowledge
    print("\nRecovering missing pricing components...")
    df_pricing_filled = fill_missing_pricing_components(df_valid)
    
    # Prevent data leakage by dropping pricing formula components
    print("\nDropping pricing components to prevent data leakage...")
    leakage_columns = ['base_fare', 'per_km_rate', 'per_minute_rate', 'trip_duration_minutes']
    df_no_leakage = df_pricing_filled.drop(columns=leakage_columns)
    
    # Fill categorical features
    print("\nFilling categorical features...")
    df_categoricals_filled = clean_categorical_features(df_no_leakage)
    
    # Create engineered features
    print("\nEngineering features...")
    df_features = engineer_features(df_categoricals_filled)
    
    # Final cleanup - remove any remaining rows with missing critical values
    print("\nFinal cleanup...")
    critical_columns = ['trip_distance_km', 'trip_price']
    initial_before_final = len(df_features)
    df_final = df_features.dropna(subset=critical_columns)
    
    removed_final = initial_before_final - len(df_final)
    if removed_final > 0:
        print(f"Removed {removed_final} rows with missing critical values")
    
    # Drop original categorical features, keep engineered ones
    print("\nReplacing categorical features with engineered alternatives...")
    original_categoricals = ['time_of_day', 'day_of_week', 'traffic_conditions', 'weather']
    existing_categoricals = [col for col in original_categoricals if col in df_final.columns]
    
    if existing_categoricals:
        df_final = df_final.drop(columns=existing_categoricals)
        print(f"Dropped original categoricals: {existing_categoricals}")
        print("Kept engineered features: weather_impact, traffic_multiplier, time indicators")
    
    # Validation and summary
    print(f"\nFinal dataset shape: {df_final.shape}")
    print("Final feature types:")
    for col in df_final.columns:
        print(f"  {col}: {df_final[col].dtype}")
    
    # Verify data quality
    non_numeric = df_final.select_dtypes(include=['object']).columns
    if len(non_numeric) == 0:
        print("Success: All features are numerical")
    else:
        print(f"Warning: Non-numeric columns present: {list(non_numeric)}")
    
    # Summary statistics
    total_removed = len(df) - len(df_final)
    retention_rate = (len(df_final) / len(df)) * 100
    
    print(f"\n=== CLEANING SUMMARY ===")
    print(f"Original: {len(df)} rows, {len(df.columns)} columns")
    print(f"Final: {len(df_final)} rows, {len(df_final.columns)} columns") 
    print(f"Data retention: {retention_rate:.1f}%")
    
    # Quality checks
    remaining_nulls = df_final.isnull().sum().sum()
    impossible_prices = (df_final['trip_price'] <= 0).sum()
    impossible_distances = (df_final['trip_distance_km'] <= 0).sum()
    
    if remaining_nulls == 0 and impossible_prices == 0 and impossible_distances == 0:
        print("Success: No null or impossible values remaining")
    else:
        print(f"Warning: {remaining_nulls} nulls, {impossible_prices + impossible_distances} impossible values")
    
    # Save cleaned data
    df_final.to_csv(output_path, index=False)
    print(f"\nCleaned data saved to {output_path}")
    
    return df_final


if __name__ == "__main__":
    clean_dataset()
