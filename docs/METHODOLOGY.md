# Methodology

## 1. Problem
The goal of this project is to help a buyer take a better decision about a property.
There are two tasks:
- **Classification:** Is this property a good investment or not?
- **Regression:** What will be the price of this property after 5 years?

## 2. Data
- File: `india_housing_prices.csv`
- Size: 250,000 properties and 23 columns
- Coverage: 42 cities in 20 states of India
- Quality: no missing values and no duplicate rows

## 3. Data cleaning
- I removed extra spaces from the text columns.
- In 46.5% of the rows, `Floor_No` was higher than `Total_Floors`. This is not possible, so I fixed `Total_Floors` to match the floor number.
- The original `Price_per_SqFt` was rounded in lakhs and had only about 100 different values. So I calculated it again in rupees using price and size.
- I marked price per sqft outliers with a flag. I did not delete them.

## 4. Feature engineering
I created some new columns to help the models:
- `Amenity_Count`: how many amenities the property has
- `Infra_Score`: one score from nearby schools, nearby hospitals and public transport
- `Floor_Ratio`: floor number divided by total floors
- `Price_vs_City_Median`: price per sqft compared with the median of the same city

## 5. How the targets were created
The dataset does not have future prices, so I could not use a real answer column.
I built a simple growth model for each property. The yearly growth rate is:

- 4% base growth
- plus a bonus for a good infrastructure score
- plus a small bonus for more amenities
- minus a small amount for older properties
- plus a small bonus if the property is under construction
- plus a bonus if the price is lower than the city median
- plus a very small random noise

Then:
- `Future_Price_5Y = Price x (1 + growth rate) ^ 5`
- If the price grows by more than 35% in 5 years, the property is labelled **Good Investment**. About 44.8% of the properties get this label.

Important: `Growth_Rate`, `Future_Price_5Y` and the label are **not** used as input features. If I used them, the model would see the answer and the result would be fake (data leakage).

## 6. Models and evaluation
- I split the data into 80% for training and 20% for testing (50,000 test rows).
- Numbers are scaled and text columns are one-hot encoded inside one pipeline, so the same steps run in the app.

**Classification models:** Logistic Regression, Random Forest, Hist Gradient Boosting and XGBoost.
The best model is **XGBoost**:
- Accuracy 0.915
- F1 score 0.905
- ROC-AUC 0.977

**Regression models:** Linear Regression, Random Forest, Hist Gradient Boosting and XGBoost.
The best model is **XGBoost**:
- RMSE about 9.2 lakhs
- R2 about 0.997

## 7. Experiment tracking
I used MLflow. Every training run saves its model name, parameters and metrics.
Screenshots are in the `docs` folder:
- `01_classification_runs.png`
- `02_regression_runs.png`
- `03_chart_view.png`
- `04_run_detail.png`

## 8. Deployment
The app is built with Streamlit and it is live here:
https://estateiq-advisor.streamlit.app/

Pages: Home, EDA Explorer (20 questions), Property Explorer, Investment Advisor and Model Performance.

The **Property Explorer** page lets the user filter the cleaned listings by state, city, property type, BHK, price, size and availability, sort them, and download the matching rows as a CSV file.

## 9. Limitations
- The dataset looks synthetic (made-up). Price, size and location have almost no real link with each other.
- The labels come from my growth model, not from real market history. So the high score only shows that the models learned this formula. It does not prove that they can predict the real market.
- This project is for learning and demonstration. It is not financial advice.
