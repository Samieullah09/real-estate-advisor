\# EstateIQ: Real Estate Investment Advisor
**Live demo:** https://estateiq-advisor.streamlit.app/



Predicts whether an Indian residential property is a good investment and estimates its price after 5 years.

Built with Python, scikit-learn, Streamlit, Plotly and MLflow.



\## Features

\- \*\*Investment Advisor\*\*: Good Investment / Needs Review verdict with confidence and a 5-year price estimate

\- \*\*EDA Explorer\*\*: 20 exploratory questions with filters and data-driven insights

\- \*\*Model Performance\*\*: classification and regression comparison, confusion matrix, feature importance

\- \*\*MLflow tracking**: every training run (parameters, metrics and task tags) is logged


## Documentation
- [Methodology](docs/METHODOLOGY.md)
- [Findings](docs/FINDINGS.md)
- [Use Cases](docs/USE_CASES.md)


## MLflow experiment tracking
![Classification runs](docs/01_classification_runs.png)
![Regression runs](docs/02_regression_runs.png)
![Metric charts](docs/03_chart_view.png)
![Run details](docs/04_run_detail.png)


\## Project structure

&#x20;   app.py              Streamlit entry point

&#x20;   app\_pages/          Page modules and theme

&#x20;   src/                Pipeline: audit, clean, features/targets, EDA charts, training

&#x20;   models/             Trained classifier and regressor (joblib)

&#x20;   reports/            Model comparison tables and metrics

&#x20;   data/processed/     Model-ready dataset (gzip)

&#x20;   assets/             Background and sidebar images



\## Run locally

&#x20;   pip install -r requirements.txt

&#x20;   streamlit run app.py



To retrain the models and view experiments (needs the raw dataset in `data/raw/`):



&#x20;   pip install -r requirements-dev.txt

&#x20;   python src/01\_audit.py

&#x20;   python src/02\_clean.py

&#x20;   python src/03\_features\_targets.py

&#x20;   python src/05\_train\_classifier.py

&#x20;   python src/06\_train\_regressor.py

&#x20;   mlflow ui --backend-store-uri sqlite:///mlflow.db



\## Methodology (short)

\- Dataset: 250,000 listings across 42 Indian cities, no missing values or duplicates.

\- Target 1 (classification): property is a Good Investment if its estimated 5-year appreciation is above 35%.

\- Target 2 (regression): estimated price after 5 years.

\- Both targets come from a documented per-property growth-rate model (infrastructure, amenities, age,

&#x20; availability, price versus city median, plus small noise). The dataset has no real future prices.

\- Models compared: Logistic Regression, Random Forest, Hist Gradient Boosting (and XGBoost if installed).

\- Best classifier: Hist Gradient Boosting (accuracy 0.914, F1 0.904, ROC-AUC 0.977).



\## Limitations

The dataset appears synthetic: prices, sizes and locations show almost no real-world correlation.

Because the labels come from the growth model above, high scores show that the models learned

that formula. They do not prove predictive power on the real market.

This project is for learning and demonstration, not financial advice.

