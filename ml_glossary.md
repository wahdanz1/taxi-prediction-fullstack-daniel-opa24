# Model Explanations for PO
## LinearRegression
Assumes that price increases in a straight line with distance (like $2 per km always).
Works well when relationships are simple and predictable, but taxi pricing has many factors
that interact in complex ways (traffic, time of day, weather all affect each other).
This makes it less suitable for our taxi pricing problem.

## RandomForest
Uses multiple "decision trees" - imagine having 100 different taxi drivers each make a price
estimate, then taking the average. Each driver considers different combinations of factors
(some focus on distance + time, others on weather + traffic). This approach handles the
complex interactions in taxi pricing much better than simple straight-line thinking.

## GradientBoosting (Best Performer)
Learns from mistakes by building estimates step-by-step. First, it makes a rough price estimate.
Then it looks at where it was wrong and creates a second model to fix those errors. It repeats
this process, getting more accurate each time. This often gives the most accurate predictions
but requires careful setup to avoid memorizing the training data too closely.
<br><br>
# Glossary for Non-Technical Stakeholders
### Linear relationships:
Price changes at a constant rate (like $2 per km, always)

### Complex patterns:
When multiple factors influence each other (distance matters
more during rush hour, weather affects travel time, etc.)

### Non-linear relationships:
Price doesn't increase at a constant rate (first 10km might
be $3/km, next 10km might be $2/km due to highway driving)

### Subset:
A smaller portion of the full dataset (like using 70% of trips to train, 30% to test)

### Mixed data types:
Combination of numbers (distance, price) and categories (weather: sunny/rainy, time: morning/evening)

### Overfitting:
When the model memorizes specific examples too closely instead of learning
general patterns, like a student who memorizes answers but can't solve new problems