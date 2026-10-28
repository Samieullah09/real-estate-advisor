import time

import joblib
import mlflow
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline


from modeling_common import (load_data, make_preprocessor, save_city_medians,
                             split_data, feature_importance)

MODELS = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, n_jobs=-1, random_state=42),
    "Hist Gradient Boosting": HistGradientBoostingClassifier(
        max_iter=200, max_depth=6, learning_rate=0.1, random_state=42),
}

# Add XGBoost only if it is installed
try:
    from xgboost import XGBClassifier
    MODELS["XGBoost"] = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                                      tree_method="hist", n_jobs=-1, random_state=42)
except ImportError:
    print("XGBoost not installed, skipping it")


def main():
    df = load_data()
    save_city_medians(df)
    X_train, X_test, y_train, y_test = split_data(df, "Investment_Label", stratify=True)

    mlflow.set_experiment("Real_Estate_Investment_Advisor")
    rows, fitted = [], {}

    for name, model in MODELS.items():
        start = time.time()
        pipe = Pipeline([("prep", make_preprocessor()), ("model", model)])
        with mlflow.start_run(run_name=f"clf_{name}"):
            pipe.fit(X_train, y_train)
            pred = pipe.predict(X_test)
            proba = pipe.predict_proba(X_test)[:, 1]
            metrics = {
                "accuracy": accuracy_score(y_test, pred),
                "precision": precision_score(y_test, pred),
                "recall": recall_score(y_test, pred),
                "f1_score": f1_score(y_test, pred),
                "roc_auc": roc_auc_score(y_test, proba),
            }
            mlflow.set_tag("task", "classification")
            mlflow.log_param("model", name)
            mlflow.log_params({k: v for k, v in model.get_params().items()
                               if k in ("n_estimators", "max_depth", "learning_rate", "max_iter")})
            mlflow.log_metrics(metrics)
        rows.append({"model": name, **metrics})
        fitted[name] = pipe
        print(f"{name}: " + " | ".join(f"{k} {v:.4f}" for k, v in metrics.items())
              + f" | {time.time() - start:.0f}s")

    # Save comparison table and the best model (by F1)
    table = pd.DataFrame(rows).sort_values("f1_score", ascending=False)
    table.to_csv("reports/classification_model_comparison.csv", index=False)
    best_name = table.iloc[0]["model"]
    best = fitted[best_name]
    joblib.dump(best, "models/investment_classifier.joblib")

    # Confusion matrix and feature importance of the best model
    cm = confusion_matrix(y_test, best.predict(X_test))
    pd.DataFrame(cm, index=["Actual 0", "Actual 1"], columns=["Pred 0", "Pred 1"]).to_csv(
        "reports/classification_confusion_matrix.csv")
    feature_importance(best, X_test, y_test, "f1").to_csv(
        "reports/classification_feature_importance.csv", header=["importance"])
    print("\nBest model:", best_name)
    print(cm)


if __name__ == "__main__":
    main()