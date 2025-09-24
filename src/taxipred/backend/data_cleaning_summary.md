# Data Cleaning Summary - The Complete Journey

## What I Did and Why (All Three Rounds)

This is my complete journey of cleaning the taxi dataset and learning some hard lessons about data leakage along the way. Started with 1,000 rows and went through three different cleaning approaches before landing on something that actually makes sense.

## Round 1: Initial EDA and Basic Cleaning (Jupyter Notebook)

Started by exploring the dataset in my Jupyter notebook. Found 1,000 rows with 11 columns, but about 266 rows had missing values scattered around. Did some basic analysis:

- Checked for impossible values (negative prices, zero distances) - found none
- Looked at correlations - `Trip_Distance_km` was clearly the strongest predictor (0.85 correlation)
- Found some outliers in prices and distances, but kept them since they represent real taxi scenarios
- Filled missing categorical values with mode, numerical values with median
- Removed rows with 2+ missing values
- Got down to 815 clean rows

Saved this as my first cleaned CSV and moved on to model training.

## Round 2: The "AI Calculator" Approach

Trained my first model on the cleaned data, felt pretty good about it. Then talked with classmates about the actual use case:
> *"What happens when users only input pickup/destination addresses and pickup time for the Google Maps distance calculation? The model will be missing tons of fields!"*

This sent me on a second cleaning journey where I decided to run a feature importance analysis to see what actually matters.

**Feature importance results:**
```
trip_distance_km: 77.4%
per_km_rate: 10.4%
trip_duration_minutes: 7.1%
per_minute_rate: 4.0%
base_fare: 0.8%
--- Top 5 features explain 99.7% of predictions ---
traffic_conditions: 0.1%
passenger_count: 0.1%
day_of_week: 0.0%
weather: 0.0%
time_of_day: 0.0%
```

The results were clear: the top 5 pricing components explain 99.7% of what determines taxi prices. All the categorical stuff I was worried about? Basically useless. They contribute less than 0.3% combined.

So I completely redesigned my cleaning approach:
- Kept only the 6 columns that actually drive pricing
- Used mathematical recovery to fill missing values: `trip_price = base_fare + (distance x per_km_rate) + (duration x per_minute_rate)`
- Managed to save 233 missing values this way
- Got a model with $3.39 MAE and 0.973 R²

Felt great about the data retention (96.7%) and the low error rate.

## Round 3: The Reality Check 

Then my classmate pointed out something that made me realize I'd just built a fancy AI-powered calculator:
> *"If your model has access to per_km_rate, trip_duration_minutes, per_minute_rate, and base_fare, then it can just calculate trip_price = base_fare + (distance x per_km_rate) + (duration x per_minute_rate). At that point, you don't need machine learning - you need a calculator."*

This was a brutal reality check. My Round 2 approach was basically data leakage - I was giving the model the pricing formula components to predict the price. Of course it performed well.

So I went back to the drawing board for Round 3.

## Round 3: Actual Machine Learning

Redesigned everything to avoid data leakage while still using domain knowledge:

**Step 1: Mathematical recovery (but then drop the leakage columns)**
- Still used the pricing formula to fill missing values for data quality
- But then dropped `base_fare`, `per_km_rate`, `per_minute_rate`, and `trip_duration_minutes`
- This way I get clean data without giving the model the answers

**Step 2: Feature engineering**
Instead of relying on weak categorical signals, I created engineered features:
- `weather_impact`: Clear=1.0, Rain=1.15, Snow=1.3
- `traffic_multiplier`: Low=1.0, Medium=1.1, High=1.25  
- `is_morning_rush`, `is_evening_rush`, `is_peak_hours`: Boolean indicators
- `is_weekend`: Weekend vs weekday pricing
- `high_impact_trip`: Snow OR high traffic conditions
- `condition_score`: Combined weather and traffic impact
- `distance_x_conditions`: Interaction between distance and conditions

**Step 3: Smart categorical handling**
Instead of filling missing values with generic defaults, I tried to preserve patterns (though the EDA later showed these patterns are weak in this synthetic dataset).

## The Disappointing Truth About This Dataset

After all this work, my EDA revealed something frustrating: this synthetic dataset has extremely weak categorical pricing signals. Looking at the boxplots:
- **Weather:** Clear, Rain, and Snow have nearly identical price distributions
- **Traffic:** High, Medium, Low show minimal differences  
- **Time of day:** All periods look remarkably similar
- **Day type:** Weekday vs Weekend are almost indistinguishable

My final model achieved $15.74 MAE and 0.821 R², with distance still dominating at 97% importance.

## The Kaggle Reality Check

I also found Kaggle notebooks reporting much lower errors, but these approaches relied on leakage (including `Base_Fare` and `Per_Km_Rate`). While it yields better scores, it doesn’t reflect real-world prediction. This is basically the same "AI calculator" mistake I made in Round 2.

Their approach would get great scores (probably under $5 MAE) but it's completely meaningless for real-world prediction.

## What I Actually Learned

This journey taught me way more than just getting a low error rate:

1. **Data leakage is subtle and dangerous** - It's easy to accidentally give your model the answers
2. **Domain knowledge is powerful** - The pricing formula helped me recover 233 missing values
3. **Feature engineering matters** - When raw features don't work, you need to create better ones
4. **Synthetic datasets have limitations** - This dataset doesn't reflect realistic condition-based pricing
5. **Higher error rates can be more honest** - $15.74 MAE for genuine prediction beats $3.39 MAE through cheating

The educational value wasn't in achieving the lowest possible error rate. It was in learning to think critically about what constitutes fair prediction, recognizing data leakage, and understanding that real-world ML is messier than competition scores suggest.

## Final Results Comparison

- **Round 1 (basic cleaning)**: 815 rows, basic model
- **Round 2 (AI calculator)**: 967 rows, $3.39 MAE, 0.973 R² - but data leakage
- **Round 3 (proper ML)**: 977 rows, $15.74 MAE, 0.821 R² - honest prediction

Round 3 is the winner not because of the scores, but because it actually solves the real problem: predicting taxi prices from information users can provide, without cheating by using the pricing formula components.

## Dataset Reality (Claude's Conclusion based on my EDA/Cleaning-journey)

"This synthetic dataset appears designed to test whether students can avoid the data leakage trap. Most people (like the user on Kaggle) fall for it and get artificially great results. The weak categorical signals are probably intentional - forcing you to think creatively about feature engineering rather than relying on obvious relationships.

Your teacher likely chose this dataset precisely because it teaches these hard lessons about data leakage, domain knowledge, and the difference between competition metrics and real-world value."