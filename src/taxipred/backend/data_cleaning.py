import pandas as pd
from taxipred.utils.constants import TAXI_CSV_PATH, CLEAN_TAXI_CSV_PATH

def fill_missing_pricing_components(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing pricing components using the fare formula:
        trip_price = base_fare + trip_distance_km * per_km_rate + trip_duration_minutes * per_minute_rate

    If one component is missing and the others are available, it is recalculated to avoid dropping rows.
    """
    df = df.copy()
    filled_count = 0
    calculation_details = {'trip_price': 0, 'base_fare': 0, 'per_km_rate': 0, 
                            'per_minute_rate': 0, 'trip_distance_km': 0, 'trip_duration_minutes': 0}
    
    for idx, row in df.iterrows():
        # Calculate missing trip_price (if all other components present)
        if pd.isna(row['trip_price']) and all(pd.notna(row[col]) for col in ['base_fare', 'per_km_rate', 'per_minute_rate', 'trip_distance_km', 'trip_duration_minutes']):
            calculated_price = (row['base_fare'] + 
                                (row['trip_distance_km'] * row['per_km_rate']) + 
                                (row['trip_duration_minutes'] * row['per_minute_rate']))
            df.loc[idx, 'trip_price'] = calculated_price
            filled_count += 1
            calculation_details['trip_price'] += 1
            
        # Skip if trip_price is still missing (can't calculate other components without it)
        elif pd.isna(row['trip_price']):
            continue
            
        # Calculate missing trip_distance_km (reverse the formula)
        elif pd.isna(row['trip_distance_km']) and all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_km_rate', 'per_minute_rate', 'trip_duration_minutes']):
            if row['per_km_rate'] != 0:  # Avoid division by zero
                calculated_distance = ((row['trip_price'] - row['base_fare'] - 
                                      (row['trip_duration_minutes'] * row['per_minute_rate'])) / 
                                        row['per_km_rate'])
                # Only accept positive distances
                if calculated_distance > 0:
                    df.loc[idx, 'trip_distance_km'] = calculated_distance
                    filled_count += 1
                    calculation_details['trip_distance_km'] += 1
            
        # Calculate missing trip_duration_minutes (reverse the formula)
        elif pd.isna(row['trip_duration_minutes']) and all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_km_rate', 'per_minute_rate', 'trip_distance_km']):
            if row['per_minute_rate'] != 0:  # Avoid division by zero
                calculated_duration = ((row['trip_price'] - row['base_fare'] - 
                                      (row['trip_distance_km'] * row['per_km_rate'])) / 
                                        row['per_minute_rate'])
                # Only accept positive durations
                if calculated_duration > 0:
                    df.loc[idx, 'trip_duration_minutes'] = calculated_duration
                    filled_count += 1
                    calculation_details['trip_duration_minutes'] += 1
            
        # Calculate missing base_fare
        elif pd.isna(row['base_fare']) and all(pd.notna(row[col]) for col in ['trip_price', 'per_km_rate', 'per_minute_rate', 'trip_distance_km', 'trip_duration_minutes']):
            calculated_base_fare = (row['trip_price'] - 
                                   (row['trip_distance_km'] * row['per_km_rate']) - 
                                   (row['trip_duration_minutes'] * row['per_minute_rate']))
            df.loc[idx, 'base_fare'] = max(0, calculated_base_fare)
            filled_count += 1
            calculation_details['base_fare'] += 1
            
        # Calculate missing per_km_rate
        elif pd.isna(row['per_km_rate']) and all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_minute_rate', 'trip_distance_km', 'trip_duration_minutes']):
            if row['trip_distance_km'] > 0:
                calculated_per_km = ((row['trip_price'] - row['base_fare'] - 
                                     (row['trip_duration_minutes'] * row['per_minute_rate'])) / 
                                    row['trip_distance_km'])
                df.loc[idx, 'per_km_rate'] = max(0, calculated_per_km)
                filled_count += 1
                calculation_details['per_km_rate'] += 1
                
        # Calculate missing per_minute_rate
        elif pd.isna(row['per_minute_rate']) and all(pd.notna(row[col]) for col in ['trip_price', 'base_fare', 'per_km_rate', 'trip_distance_km', 'trip_duration_minutes']):
            if row['trip_duration_minutes'] > 0:
                calculated_per_minute = ((row['trip_price'] - row['base_fare'] - 
                                        (row['trip_distance_km'] * row['per_km_rate'])) / 
                                        row['trip_duration_minutes'])
                df.loc[idx, 'per_minute_rate'] = max(0, calculated_per_minute)
                filled_count += 1
                calculation_details['per_minute_rate'] += 1
    
    if filled_count > 0:
        print(f"Calculated {filled_count} missing pricing components using the pricing formula:")
        for component, count in calculation_details.items():
            if count > 0:
                print(f"  - {component}: {count} values")
    
    return df

def clean_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing categorical and passenger-related values:
    - Categorical columns -> mode (or sensible defaults if no mode exists).
    - Passenger count -> median.
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
    
    # Fill missing passenger_count
    missing_passengers = df['passenger_count'].isnull().sum()
    if missing_passengers > 0:
        df['passenger_count'] = df['passenger_count'].fillna(df['passenger_count'].median())
        total_filled += missing_passengers
    
    if total_filled > 0:
        print(f"Filled {total_filled} missing categorical/passenger values")
    
    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features capturing traffic, weather, rush hours, and trip impact:
        - weather_impact, traffic_multiplier
        - is_morning_rush, is_evening_rush, is_peak_hours
        - is_weekend, high_impact_trip
        - condition_score = weather_impact * traffic_multiplier
        - distance_x_conditions = trip_distance_km * condition_score
    """
    df = df.copy()
    print("Creating engineered features...")
    
    df['weather_impact'] = df['weather'].map({'Clear': 1.0, 'Rain': 1.15, 'Snow': 1.3})
    df['traffic_multiplier'] = df['traffic_conditions'].map({'Low': 1.0, 'Medium': 1.1, 'High': 1.25})
    
    df['is_morning_rush'] = (df['time_of_day'] == 'Morning').astype(int)
    df['is_evening_rush'] = (df['time_of_day'] == 'Evening').astype(int)
    df['is_peak_hours'] = (df['is_morning_rush'] | df['is_evening_rush']).astype(int)
    
    df['is_weekend'] = (df['day_of_week'] == 'Weekend').astype(int)
    df['high_impact_trip'] = ((df['weather'] == 'Snow') | (df['traffic_conditions'] == 'High')).astype(int)
    
    df['condition_score'] = df['weather_impact'] * df['traffic_multiplier']
    df['distance_x_conditions'] = df['trip_distance_km'] * df['condition_score']
    
    print("Added 8 engineered features")
    return df

def clean_dataset(input_path: str = TAXI_CSV_PATH, output_path: str = CLEAN_TAXI_CSV_PATH) -> pd.DataFrame:
    """
    Clean the raw taxi dataset into a model-ready format.

    Steps performed:
        1. Remove rows with impossible core values (negative/zero prices, distances, durations).
        2. Recalculate missing pricing components using the fare formula.
        3. Drop pricing component columns to prevent data leakage in ML.
        4. Fill missing categorical and passenger-related features.
        5. Engineer new features capturing traffic, weather, rush hours, etc.
        6. Final cleanup: drop rows with still-missing critical values, validate dataset, and save.

    Returns:
        pd.DataFrame: Cleaned and feature-enhanced taxi dataset ready for ML training.
    """
    print("Loading raw data...")
    df = pd.read_csv(input_path)
    
    print(f"Original dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Convert column names to lowercase for consistency
    df.columns = df.columns.str.lower()
    
    print(f"\nInitial data overview: {len(df)} rows, {df.shape[1]} columns")
    missing_summary = df.isnull().sum()
    for col, missing_count in missing_summary.items():
        if missing_count > 0:
            print(f"Missing {col}: {missing_count}")
    
    # STEP 1 --------------------------------------------------
    print("\nStep 1: Removing rows with impossible core trip values (keeping rows with missing ones)...")
    initial_rows = len(df)

    df_valid_core = df[
        ((df['trip_price'].isnull()) | (df['trip_price'] > 0)) &
        ((df['trip_distance_km'].isnull()) | (df['trip_distance_km'] > 0)) &
        ((df['trip_duration_minutes'].isnull()) | (df['trip_duration_minutes'] > 0))
    ].copy()

    removed_impossible = initial_rows - len(df_valid_core)
    print(f"Removed {removed_impossible} rows with impossible values")
    
    # STEP 2 --------------------------------------------------
    print("\nStep 2: Calculating missing pricing components...")
    df_pricing_filled = fill_missing_pricing_components(df_valid_core)

    # STEP 3 --------------------------------------------------
    print("\nStep 3: Dropping pricing component columns to prevent data leakage...")
    columns_to_drop = ['base_fare', 'per_km_rate', 'per_minute_rate', 'trip_duration_minutes']
    df_no_leakage = df_pricing_filled.drop(columns=columns_to_drop)
    
    # STEP 4 --------------------------------------------------
    print("\nStep 4: Filling missing categorical features...")
    df_categoricals_filled = clean_categorical_features(df_no_leakage)

    # STEP 5 --------------------------------------------------
    print("\nStep 5: Engineering features...")
    df_features = engineer_features(df_categoricals_filled)
    
    # STEP 6 --------------------------------------------------
    print("\nStep 6: Final cleanup (dropping rows still missing critical values)...")
    critical_columns = ['trip_distance_km', 'trip_price']
    
    initial_before_final = len(df_features)
    df_final = df_features.dropna(subset=critical_columns)
    
    removed_final = initial_before_final - len(df_final)
    if removed_final > 0:
        print(f"Removed {removed_final} rows with missing critical values")

    # STEP 7 --------------------------------------------------
    print("\nStep 7: Dropping original categorical features (keeping engineered ones)...")
    categorical_to_drop = ['time_of_day', 'day_of_week', 'traffic_conditions', 'weather']
    existing_categoricals = [col for col in categorical_to_drop if col in df_final.columns]

    if existing_categoricals:
        print(f"Dropping original categoricals: {existing_categoricals}")
        df_final = df_final.drop(columns=existing_categoricals)
        print(f"Kept engineered features: weather_impact, traffic_multiplier, is_morning_rush, is_evening_rush, etc.")
    else:
        print("No categorical features found to drop")

    print(f"Final dataset shape: {df_final.shape}")

    # Verify all columns are numerical
    print("\nFinal feature types:")
    for col in df_final.columns:
        print(f"  {col}: {df_final[col].dtype}")

    non_numeric = df_final.select_dtypes(include=['object']).columns
    if len(non_numeric) == 0:
        print("Success: All features are numerical - no encoding needed in training!")
    else:
        print(f"Warning: Non-numeric columns still present: {list(non_numeric)}")
    
    # Final summary --------------------------------------------------
    total_removed = len(df) - len(df_final)
    retention_rate = (len(df_final) / len(df)) * 100
    
    print("\n=== CLEANING SUMMARY ===")
    print(f"Original dataset: {len(df)} rows, {len(df.columns)} columns")
    print(f"Final dataset: {len(df_final)} rows, {len(df_final.columns)} columns")
    print(f"Total removed: {total_removed} rows ({100-retention_rate:.1f}%)")
    print(f"Data retention rate: {retention_rate:.1f}%")
    print(f"Features retained: {len(df_final.columns)}")
    
    # Verify data quality --------------------------------------------------
    remaining_nulls = df_final.isnull().sum().sum()
    if remaining_nulls == 0:
        print("Success: No null values remaining")
    else:
        print(f"Warning: {remaining_nulls} null values still present")
        print(df_final.isnull().sum()[df_final.isnull().sum() > 0])
    
    # Check for impossible values in final dataset
    print("\nChecking for impossible values...")
    impossible_prices = (df_final['trip_price'] <= 0).sum()
    impossible_distances = (df_final['trip_distance_km'] <= 0).sum()
    
    total_impossible = impossible_prices + impossible_distances
    if total_impossible == 0:
        print("Success: No impossible values remaining")
    else:
        print(f"Warning: {total_impossible} impossible values still present")
    
    # Show feature distribution for verification
    print("\n=== FEATURE OVERVIEW ===")
    print("Categorical features:")
    cat_features = ['time_of_day', 'day_of_week', 'traffic_conditions', 'weather']
    for col in cat_features:
        if col in df_final.columns:
            print(f"  {col}: {df_final[col].nunique()} unique values")
    
    print("Numerical features:")
    num_features = ['trip_distance_km', 'passenger_count', 'trip_price']
    for col in num_features:
        if col in df_final.columns:
            print(f"  {col}: range {df_final[col].min():.2f} - {df_final[col].max():.2f}")
    
    # Save cleaned data
    df_final.to_csv(output_path, index=False)
    print(f"\nCleaned data saved to {output_path}")
    
    return df_final

if __name__ == "__main__":
    clean_data = clean_dataset()
