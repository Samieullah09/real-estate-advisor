import json
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app_pages.theme import CYAN, GREEN, ORANGE, PURPLE, kpi, style_fig
from src.modeling_common import FEATURES

AMENITIES = ["Gym", "Pool", "Garden", "Playground", "Clubhouse"]
TRANSPORT_SCORE = {"Low": 0, "Medium": 0.5, "High": 1}   # same mapping as src/03_features_targets.py


@st.cache_resource
def load_models():
    classifier = joblib.load("models/investment_classifier.joblib")
    regressor = joblib.load("models/price_regressor.joblib")
    with open("models/city_median_pps.json") as f:
        medians = json.load(f)
    return classifier, regressor, medians


def build_row(v, medians):
    # Recreate the engineered features exactly like the training pipeline did
    pps = v["price"] * 100000 / v["size"]
    infra = (v["schools"] / 10 + v["hospitals"] / 10 + TRANSPORT_SCORE[v["transport"]]) / 3
    row = {
        "City": v["city"], "Property_Type": v["ptype"], "Furnished_Status": v["furnished"],
        "Public_Transport_Accessibility": v["transport"], "Parking_Space": v["parking"],
        "Security": v["security"], "Facing": v["facing"], "Owner_Type": v["owner"],
        "Availability_Status": v["availability"], "BHK": v["bhk"], "Size_in_SqFt": v["size"],
        "Price_in_Lakhs": v["price"], "Price_per_SqFt_Rs": pps, "Age_of_Property": v["age"],
        "Nearby_Schools": v["schools"], "Nearby_Hospitals": v["hospitals"], "Floor_No": v["floor"],
        "Total_Floors": v["total_floors"], "Amenity_Count": len(v["amenities"]),
        "Infra_Score": infra, "Floor_Ratio": v["floor"] / v["total_floors"],
        "Price_vs_City_Median": pps / medians[v["city"]],
    }
    return pd.DataFrame([row])[FEATURES]


def render(df):
    st.title("Investment Advisor")
    st.caption("Enter property details to check if it is a good investment and estimate its price after 5 years.")
    classifier, regressor, medians = load_models()

    left, right = st.columns([1, 1.45])
    with left:
        with st.container(border=True):
            st.markdown("**Property details**")
            a, b = st.columns(2)
            state = a.selectbox("State", sorted(df["State"].unique()))
            cities = sorted(df.loc[df["State"] == state, "City"].unique())
            city = b.selectbox("City", cities)
            a, b = st.columns(2)
            ptype = a.selectbox("Property type", sorted(df["Property_Type"].unique()))
            bhk = b.selectbox("BHK", [1, 2, 3, 4, 5], index=2)
            a, b = st.columns(2)
            size = a.number_input("Size (sq ft)", 500, 5000, 1800, step=50)
            price = b.number_input("Price (₹ lakhs)", 10.0, 500.0, 185.0, step=5.0)
            a, b, c = st.columns(3)
            age = a.number_input("Age (years)", 0, 35, 6)
            floor = b.number_input("Floor no.", 0, 30, 5)
            total_floors = c.number_input("Total floors", 1, 30, 12)
            a, b = st.columns(2)
            schools = a.slider("Nearby schools", 1, 10, 6)
            hospitals = b.slider("Nearby hospitals", 1, 10, 5)
            a, b, c = st.columns(3)
            transport = a.selectbox("Transport", ["Low", "Medium", "High"], index=2)
            parking = b.selectbox("Parking", ["Yes", "No"])
            security = c.selectbox("Security", ["Yes", "No"])
            a, b = st.columns(2)
            furnished = a.selectbox("Furnishing", sorted(df["Furnished_Status"].unique()))
            facing = b.selectbox("Facing", sorted(df["Facing"].unique()))
            a, b = st.columns(2)
            owner = a.selectbox("Owner type", sorted(df["Owner_Type"].unique()))
            availability = b.selectbox("Availability", sorted(df["Availability_Status"].unique()))
            amenities = st.multiselect("Amenities", AMENITIES, default=["Gym", "Pool", "Garden"])
            st.caption("Inputs are limited to the dataset's range (price 10-500 L, size 500-5000 sq ft).")
            go_btn = st.button("Get Investment Analysis", type="primary", width="stretch")

    if go_btn:
        if floor > total_floors:
            st.session_state["advisor"] = {"error": "Floor number cannot be higher than total floors."}
        else:
            values = dict(city=city, ptype=ptype, furnished=furnished, transport=transport, parking=parking,
                          security=security, facing=facing, owner=owner, availability=availability,
                          bhk=bhk, size=size, price=price, age=age, schools=schools, hospitals=hospitals,
                          floor=floor, total_floors=total_floors, amenities=amenities)
            row = build_row(values, medians)
            st.session_state["advisor"] = {
                "prob": float(classifier.predict_proba(row)[0, 1]),
                "future": float(regressor.predict(row)[0]),
                "price": price, "city": city, "ptype": ptype, "bhk": bhk,
                "vs_city": float(row["Price_vs_City_Median"].iloc[0]),
            }

    with right:
        result = st.session_state.get("advisor")
        if result is None:
            st.info("Fill in the details on the left and press **Get Investment Analysis**.")
            return
        if "error" in result:
            st.error(result["error"])
            return
        show_result(df, result)


def show_result(df, r):
    good = r["prob"] >= 0.5
    confidence = r["prob"] if good else 1 - r["prob"]
    growth_total = (r["future"] / r["price"] - 1) * 100
    yearly = ((r["future"] / r["price"]) ** (1 / 5) - 1) * 100

    c1, c2 = st.columns(2)
    c1.markdown(kpi("INVESTMENT RECOMMENDATION", "Good Investment" if good else "Needs Further Review",
                    f"Model confidence {confidence * 100:.0f}%", GREEN if good else ORANGE),
                unsafe_allow_html=True)
    c2.markdown(kpi("ESTIMATED PRICE AFTER 5 YEARS", f"₹{r['future']:.1f} L",
                    f"{growth_total:+.1f}% vs today (≈ {yearly:.1f}% per year)", CYAN),
                unsafe_allow_html=True)
    st.write("")

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Probability of being a Good Investment**")
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=r["prob"] * 100, number=dict(suffix="%"),
            gauge=dict(axis=dict(range=[0, 100]), bar=dict(color=GREEN if good else ORANGE),
                       bgcolor="rgba(148,163,184,.12)", borderwidth=0,
                       threshold=dict(line=dict(color="white", width=3), value=50))))
        st.plotly_chart(style_fig(fig, 260), width="stretch")
    with g2:
        st.markdown("**5-year price path (steady yearly growth assumed)**")
        years = list(range(0, 6))
        values = [r["price"] * (1 + yearly / 100) ** y for y in years]
        fig = go.Figure(go.Scatter(x=years, y=values, mode="lines+markers",
                                   line=dict(color=CYAN, width=3), marker=dict(size=8)))
        fig.update_xaxes(title="Years from now")
        st.plotly_chart(style_fig(fig, 260), width="stretch")

    f1, f2 = st.columns(2)
    with f1:
        st.markdown("**What drives the model overall (feature importance)**")
        path = Path("reports/classification_feature_importance.csv")
        if path.exists():
            imp = pd.read_csv(path, index_col=0)["importance"].sort_values().tail(8)
            fig = go.Figure(go.Bar(x=imp.values, y=imp.index, orientation="h", marker_color=PURPLE))
            st.plotly_chart(style_fig(fig, 300), width="stretch")
        else:
            st.info("Run src/05_train_classifier.py to create the feature importance file.")
    with f2:
        diff = (r["vs_city"] - 1) * 100
        st.markdown("**Price compared with the city median**")
        st.metric(f"₹/sqft vs {r['city']} median", f"{abs(diff):.0f}% {'below' if diff < 0 else 'above'}")
        st.markdown("**Similar properties in the dataset**")
        sim = df[(df["City"] == r["city"]) & (df["Property_Type"] == r["ptype"]) & (df["BHK"] == r["bhk"])]
        sim = sim.assign(gap=(sim["Price_in_Lakhs"] - r["price"]).abs()).nsmallest(5, "gap")
        st.dataframe(sim[["Locality", "Size_in_SqFt", "Price_in_Lakhs", "Age_of_Property",
                          "Investment_Label_Name"]].rename(columns={
            "Size_in_SqFt": "Size", "Price_in_Lakhs": "Price (L)", "Age_of_Property": "Age",
            "Investment_Label_Name": "Label"}), hide_index=True, width="stretch")
    st.caption("The model learned the project's growth-rate rules. This is a screening tool, "
               "not financial advice or a guaranteed forecast.")