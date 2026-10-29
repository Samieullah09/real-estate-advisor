# Findings

## 1. Quick summary
- The data is very **uniform**. Price, size and location show almost no real pattern.
- The Good Investment result depends mostly on **how cheap the property is compared with its city** and on the **infrastructure score**.
- The models score very high (accuracy 0.915, R2 0.997) because the targets were made from a formula. This shows the models learned that formula. It does not prove they can predict the real market.

## 2. What the data shows (EDA)
- **Price:** ranges from Rs 10 lakh to Rs 500 lakh. The average is Rs 254.6 lakh and the prices are spread almost evenly.
- **Size:** ranges from 500 to 5,000 sq ft. The average is 2,750 sq ft and it is also spread evenly.
- **Size vs price:** correlation is -0.003. Size does not explain price at all.
- **Price per sq ft:** the average is about Rs 13,058. The top state is Karnataka (Rs 13,252) and the lowest is Punjab (Rs 12,931). The gap is only about 2.5%.
- **Costliest cities:** Bangalore (Rs 258.5 lakh), Surat (Rs 258.1 lakh) and Kochi (Rs 257.4 lakh). Even the cheapest city is close (Cuttack, Rs 250.8 lakh).
- **Property type:** Apartment, Independent House and Villa have almost the same price per sq ft (about Rs 13,000 to Rs 13,100).
- **BHK, furnishing and owner type:** average price stays between Rs 254 and Rs 255 lakh for all groups.
- **Data quality:** no missing values or duplicates. In 46.5% of the rows the floor number was higher than the total floors, and this was fixed.

## 3. What affects "Good Investment"
About **44.8%** of the properties are labelled Good Investment (5-year growth above 35%).

| Factor | Good Investment share |
|---|---|
| Transport: High | 55.4% |
| Transport: Medium | 44.7% |
| Transport: Low | 34.2% |
| Under construction | 55.2% |
| Ready to move | 34.3% |
| Apartment / House / Villa | 44.8% / 44.5% / 45.0% |

- Properties with **better transport** and properties that are **under construction** are more often Good Investments.
- Property type makes no difference.
- The strongest signal is **price compared with the city median**. Cheaper-than-city properties are more often Good Investments.
- Newer properties and properties with a higher infrastructure score also do better.

## 3b. Extra checks from the project brief
- **Area vs investment return:** the correlation between size and 5-year appreciation is 0.43. In this data, bigger properties have a lower price per sq ft, and my growth model gives a bonus to properties that are cheaper than their city median. So this link comes from the formula, not from the real market.
- **Infrastructure score vs price:** the correlation with price per sq ft is almost zero (-0.001). Infrastructure score affects the growth rate only because I built it into the formula (correlation 0.36).
- **Crime rate:** the dataset has no crime column, so this analysis was not possible.
- **Resale value:** the dataset has no resale price. I used price per sq ft as the closest measure, and it shows no relation with infrastructure.

## 4. Model results

**Classification (is it a Good Investment?)**

| Model | Accuracy | F1 | ROC-AUC |
|---|---|---|---|
| XGBoost (used in the app) | 0.915 | 0.905 | 0.977 |
| Hist Gradient Boosting | 0.914 | 0.904 | 0.977 |
| Random Forest | 0.901 | 0.890 | 0.969 |
| Logistic Regression | 0.896 | 0.883 | 0.962 |

- On 50,000 test properties the model made about 4,300 mistakes. This is roughly 2,150 wrong "Good" and 2,130 missed "Good".
- Top features: price vs city median, infrastructure score, availability status, price per sq ft, age of property.

**Regression (price after 5 years)**

| Model | RMSE (lakh) | MAE (lakh) | R2 |
|---|---|---|---|
| XGBoost (used in the app) | 9.22 | 6.51 | 0.997 |
| Hist Gradient Boosting | 9.22 | 6.52 | 0.997 |
| Random Forest | 10.31 | 7.34 | 0.997 |
| Linear Regression | 14.99 | 11.70 | 0.993 |

- The average error is about Rs 6.5 lakh on prices that go up to Rs 500+ lakh.
- The most important feature is today's price. This is expected, because future price = today's price x growth.

## 5. How to read these results
- High accuracy is not the same as good real-world prediction.
- The label and the future price come from a formula that I wrote. The models found that formula.
- Real property prices also depend on things this dataset does not have: exact location, builder, demand, interest rates and government rules.
- So the app is a **learning and decision-support demo**. It is not financial advice.

## 6. What I would do next
- Use real historical price data per city and year.
- Add location information such as latitude, longitude and distance to the city centre.
- Add a yearly trend so that growth is learned from real data and not from a formula.