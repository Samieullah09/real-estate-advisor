\# Methodology



\## 1. Problem

The goal of this project is to help a buyer take a better decision about a property.

There are two tasks:

\- \*\*Classification:\*\* Is this property a good investment or not?

\- \*\*Regression:\*\* What will be the price of this property after 5 years?



\## 2. Data

\- File: `india\_housing\_prices.csv`

\- Size: 250,000 properties and 23 columns

\- Coverage: 42 cities in 20 states of India

\- Quality: no missing values and no duplicate rows



\## 3. Data cleaning

\- I removed extra spaces from the text columns.

\- In 46.5% of the rows, `Floor\_No` was higher than `Total\_Floors`. This is not possible, so I fixed `Total\_Floors` to match the floor number.

\- The original `Price\_per\_SqFt` was rounded in lakhs and had only about 100 different values. So I calculated it again in rupees using price and size.

\- I marked price per sqft outliers with a flag. I did not delete them.



\## 4. Feature engineering

I created some new columns to help the models:

\- `Amenity\_Count`: how many amenities the property has

\- `Infra\_Score`: one score from nearby schools, nearby hospitals and public transport

\- `Floor\_Ratio`: floor number divided by total floors

\- `Price\_vs\_City\_Median`: price per sqft compared with the median of the same city



\## 5. How the targets were created

The dataset does not have future prices, so I could not use a real answer column.

I built a simple growth model for each property. The yearly growth rate is:



\- 4% base growth

\- plus a bonus for a good infrastructure score

\- plus a small bonus for more amenities

\- minus a small amount for older properties

\- plus a small bonus if the property is under construction

\- plus a bonus if the price is lower than the city median

\- plus a very small random noise



Then:

\- `Future\_Price\_5Y = Price x (1 + growth rate) ^ 5`

\- If the price grows by more than 35% in 5 years, the property is labelled \*\*Good Investment\*\*. About 44.8% of the properties get this label.



Important: `Growth\_Rate`, `Future\_Price\_5Y` and the label are \*\*not\*\* used as input features. If I used them, the model would see the answer and the result would be fake (data leakage).



\## 6. Models and evaluation

\- I split the data into 80% for training and 20% for testing (50,000 test rows).

\- Numbers are scaled and text columns are one-hot encoded inside one pipeline, so the same steps run in the app.



\*\*Classification models:\*\* Logistic Regression, Random Forest, Hist Gradient Boosting.

The best model is \*\*Hist Gradient Boosting\*\*:

\- Accuracy 0.914

\- F1 score 0.904

\- ROC-AUC 0.977



\*\*Regression models:\*\* Linear Regression, Random Forest, Hist Gradient Boosting.

The best model is \*\*Hist Gradient Boosting\*\*:

\- RMSE about 9.2 lakhs

\- R2 about 0.997



(XGBoost is supported in the code. It is used automatically if it is installed.)



\## 7. Experiment tracking

I used MLflow. Every training run saves its model name, parameters and metrics.

Screenshots are in the `docs` folder:

\- `01\_classification\_runs.png`

\- `02\_regression\_runs.png`

\- `03\_chart\_view.png`

\- `04\_run\_detail.png`



\## 8. Deployment

The app is built with Streamlit and it is live here:

https://estateiq-advisor.streamlit.app/



Pages: Home, EDA Explorer (20 questions), Investment Advisor and Model Performance.



\## 9. Limitations

\- The dataset looks synthetic (made-up). Price, size and location have almost no real link with each other.

\- The labels come from my growth model, not from real market history. So the high score only shows that the models learned this formula. It does not prove that they can predict the real market.

\- This project is for learning and demonstration. It is not financial advice.

