from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app_pages.theme import CYAN, GREEN, ORANGE, PALETTE, PURPLE, kpi, style_fig

px.defaults.color_discrete_sequence = PALETTE   # app colours for every chart

REPORTS = Path("reports")


def read_report(name, **kwargs):
    # Return None when a report has not been generated yet
    path = REPORTS / name
    return pd.read_csv(path, **kwargs) if path.exists() else None


def classification_tab():
    table = read_report("classification_model_comparison.csv")
    if table is None:
        st.warning("Run src/05_train_classifier.py first.")
        return
    best = table.sort_values("f1_score", ascending=False).iloc[0]
    cols = st.columns(4)
    cols[0].markdown(kpi("BEST MODEL", best["model"], "highest F1 score", CYAN), unsafe_allow_html=True)
    cols[1].markdown(kpi("ACCURACY", f"{best['accuracy'] * 100:.1f}%", "on 20% unseen test data", GREEN), unsafe_allow_html=True)
    cols[2].markdown(kpi("F1 SCORE", f"{best['f1_score']:.3f}", f"precision {best['precision']:.2f} · recall {best['recall']:.2f}", PURPLE), unsafe_allow_html=True)
    cols[3].markdown(kpi("ROC-AUC", f"{best['roc_auc']:.3f}", "ranking quality", ORANGE), unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("**Model comparison**")
        shown = table.sort_values("f1_score", ascending=False).round(4)
        st.dataframe(shown, hide_index=True, width="stretch")
        long = shown.melt(id_vars="model", value_vars=["accuracy", "f1_score", "roc_auc"],
                          var_name="metric", value_name="score")
        fig = px.bar(long, x="model", y="score", color="metric", barmode="group", text_auto=".3f")
        fig.update_yaxes(range=[0.8, 1.0])
        st.plotly_chart(style_fig(fig, 300), width="stretch")
    with right:
        st.markdown("**Confusion matrix (best model, test data)**")
        cm = read_report("classification_confusion_matrix.csv", index_col=0)
        if cm is not None:
            fig = px.imshow(cm.values, text_auto=",d", x=["Predicted: Not good", "Predicted: Good"],
                            y=["Actual: Not good", "Actual: Good"],
                            color_continuous_scale=["#0b1d3a", "#0e7490", CYAN])
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(style_fig(fig, 300), width="stretch")
        st.markdown("**Feature importance (permutation, F1 drop)**")
        imp = read_report("classification_feature_importance.csv", index_col=0)
        if imp is not None:
            top = imp["importance"].sort_values().tail(8)
            fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h", marker_color=PURPLE))
            st.plotly_chart(style_fig(fig, 300), width="stretch")


def regression_tab():
    table = read_report("regression_model_comparison.csv")
    if table is None:
        st.warning("Run src/06_train_regressor.py first.")
        return
    best = table.sort_values("rmse").iloc[0]
    cols = st.columns(4)
    cols[0].markdown(kpi("BEST MODEL", best["model"], "lowest RMSE", CYAN), unsafe_allow_html=True)
    cols[1].markdown(kpi("RMSE", f"₹{best['rmse']:.1f} L", "typical error size", GREEN), unsafe_allow_html=True)
    cols[2].markdown(kpi("MAE", f"₹{best['mae']:.1f} L", "average absolute error", PURPLE), unsafe_allow_html=True)
    cols[3].markdown(kpi("R²", f"{best['r2']:.4f}", "share of variation explained", ORANGE), unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("**Model comparison**")
        shown = table.sort_values("rmse").round(4)
        st.dataframe(shown, hide_index=True, width="stretch")
        long = shown.melt(id_vars="model", value_vars=["rmse", "mae"], var_name="metric", value_name="lakhs")
        fig = px.bar(long, x="model", y="lakhs", color="metric", barmode="group", text_auto=".1f")
        st.plotly_chart(style_fig(fig, 300), width="stretch")
        st.markdown("**Actual vs predicted 5-year price (1,000 test properties)**")
        avp = read_report("regression_actual_vs_predicted.csv")
        if avp is not None:
            fig = px.scatter(avp, x="actual", y="predicted", opacity=0.5)
            lim = [avp["actual"].min(), avp["actual"].max()]
            fig.add_trace(go.Scatter(x=lim, y=lim, mode="lines", line=dict(color=ORANGE, dash="dash"),
                                     name="perfect prediction"))
            st.plotly_chart(style_fig(fig, 300), width="stretch")
    with right:
        st.markdown("**Feature importance (permutation, RMSE increase)**")
        imp = read_report("regression_feature_importance.csv", index_col=0)
        if imp is not None:
            top = imp["importance"].sort_values().tail(8)
            fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h", marker_color=PURPLE))
            st.plotly_chart(style_fig(fig, 340), width="stretch")
        st.info("Current price dominates because the 5-year price is built as price × growth factor. "
                "The score shows how well the model learned that rule, not real market forecasting.")


def method_tab():
    st.markdown("""
**Targets (created in `src/03_features_targets.py`)**
- Yearly growth rate = 4% base + infrastructure score + amenities + under-construction bonus + value gap vs city median − age penalty + small seeded noise.
- `Future_Price_5Y` = current price × (1 + growth rate)^5.
- `Good Investment` = 1 when 5-year appreciation is above 35%.

**Training (`src/05_train_classifier.py`, `src/06_train_regressor.py`)**
- 80/20 train-test split with a fixed seed; the classifier split keeps the class ratio.
- One-hot encoding for categories and scaling for numbers inside one pipeline.
- Growth rate, future price, appreciation and the label are never used as features (no leakage).
- Every run is logged to MLflow (`mlflow ui --backend-store-uri sqlite:///mlflow.db`).

**Limits**
- The dataset has no price history, so the growth model is an assumption, not a learned market trend.
- Scores show how well the models reproduce that rule on unseen rows.
""")


def render(df=None):
    st.title("Model Performance")
    st.caption("Results of the classification and regression models, read from the training reports.")
    view = st.radio("View", ["Classification", "Regression", "Method & limits"], horizontal=True,
                    label_visibility="collapsed")
    if view == "Classification":
        classification_tab()
    elif view == "Regression":
        regression_tab()
    else:
        method_tab()