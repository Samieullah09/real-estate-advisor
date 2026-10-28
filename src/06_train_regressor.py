import time

import joblib
import mlflow
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline

from modeling_common import load_data, make_preprocessor, split_data, feature_importance

MODELS = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=12, n_jobs=-1, random_state=42),
    "Hist Gradient Boosting": HistGradientBoostingRegressor(
        max_iter=200, max_depth=6, learning_rate=0.1, random_state=42),
}

# Add XGBoost only if it is installed
try:
    from xgboost import XGBRegressor
    MODELS["XGBoost"] = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1,
                                     tree_method="hist", n_jobs=-1, random_state=42)
except ImportError:
    print("XGBoost not installed, skipping it")


def main():
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df, "Future_Price_5Y")

    mlflow.set_experiment("Real_Estate_Investment_Advisor")
    rows, fitted = [], {}

    for name, model in MODELS.items():
        start = time.time()
        pipe = Pipeline([("prep", make_preprocessor()), ("model", model)])
        with mlflow.start_run(run_name=f"reg_{name}"):
            pipe.fit(X_train, y_train)
            pred = pipe.predict(X_test)
            metrics = {
                "rmse": root_mean_squared_error(y_test, pred),
                "mae": mean_absolute_error(y_test, pred),
                "r2": r2_score(y_test, pred),
            }
            mlflow.set_tag("task", "regression")
            mlflow.log_param("model", name)
            mlflow.log_params({k: v for k, v in model.get_params().items()
                               if k in ("n_estimators", "max_depth", "learning_rate", "max_iter")})
            mlflow.log_metrics(metrics)
        rows.append({"model": name, **metrics})
        fitted[name] = pipe
        print(f"{name}: " + " | ".join(f"{k} {v:.4f}" for k, v in metrics.items())
              + f" | {time.time() - start:.0f}s")

    # Save comparison table and the best model (lowest RMSE)
    table = pd.DataFrame(rows).sort_values("rmse")
    table.to_csv("reports/regression_model_comparison.csv", index=False)
    best_name = table.iloc[0]["model"]
    best = fitted[best_name]
    joblib.dump(best, "models/price_regressor.joblib")

    # Actual vs predicted sample and feature importance of the best model
    sample = X_test.sample(1000, random_state=42)
    pd.DataFrame({"actual": y_test.loc[sample.index],
                  "predicted": best.predict(sample)}).to_csv(
        "reports/regression_actual_vs_predicted.csv", index=False)
    feature_importance(best, X_test, y_test, "neg_root_mean_squared_error").to_csv(
        "reports/regression_feature_importance.csv", header=["importance"])
    print("\nBest model:", best_name)
    print("Average Future_Price_5Y: %.1f lakhs" % df["Future_Price_5Y"].mean())


if __name__ == "__main__":
    main()