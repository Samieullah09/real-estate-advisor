import json

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = "data/processed/housing_ml_ready.csv"

CATEGORICAL = ["City", "Property_Type", "Furnished_Status", "Public_Transport_Accessibility",
               "Parking_Space", "Security", "Facing", "Owner_Type", "Availability_Status"]
NUMERIC = ["BHK", "Size_in_SqFt", "Price_in_Lakhs", "Price_per_SqFt_Rs", "Age_of_Property",
           "Nearby_Schools", "Nearby_Hospitals", "Floor_No", "Total_Floors", "Amenity_Count",
           "Infra_Score", "Floor_Ratio", "Price_vs_City_Median"]
FEATURES = CATEGORICAL + NUMERIC
# Growth_Rate, Future_Price_5Y, Appreciation_5Y_Pct and the label are NOT features (leakage)


def load_data():
    return pd.read_csv(DATA_PATH)


def make_preprocessor():
    # One-hot encode categories, scale numeric columns
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ("num", StandardScaler(), NUMERIC),
    ])


def split_data(df, target, stratify=False):
    X, y = df[FEATURES], df[target]
    return train_test_split(X, y, test_size=0.2, random_state=42,
                            stratify=y if stratify else None)


def save_city_medians(df, path="models/city_median_pps.json"):
    # The app needs these to compute Price_vs_City_Median for a new property
    medians = df.groupby("City")["Price_per_SqFt_Rs"].median().to_dict()
    with open(path, "w") as f:
        json.dump(medians, f)


def feature_importance(pipe, X_test, y_test, scoring):
    # Model-agnostic importance per original feature, measured on a test sample
    idx = X_test.sample(5000, random_state=42).index
    result = permutation_importance(pipe, X_test.loc[idx], y_test.loc[idx], scoring=scoring,
                                    n_repeats=5, random_state=42, n_jobs=-1)
    return pd.Series(result.importances_mean, index=X_test.columns).sort_values(ascending=False)