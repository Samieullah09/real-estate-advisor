from pathlib import Path

import pandas as pd
import streamlit as st

from app_pages import eda, model_perf, overview, predict
from app_pages.theme import brand, inject_css

st.set_page_config(page_title="EstateIQ | Investment Advisor", page_icon="🏢",
                   layout="wide", initial_sidebar_state="expanded")
inject_css()

DATA_PATH = Path("data/processed/housing_ml_ready.csv.gz")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


df = load_data()

brand()
st.sidebar.write("")
page = st.sidebar.radio("NAVIGATION", ["🏠  Home", "📊  EDA Explorer",
                                       "💡  Investment Advisor", "🤖  Model Performance"])
page = page.split("  ", 1)[1]            # drop the emoji prefix
st.sidebar.divider()
st.sidebar.caption(f"{len(df):,} PROPERTIES · {df['City'].nunique()} CITIES")

if page == "Home":
    overview.render(df)
elif page == "EDA Explorer":
    eda.render(df)
elif page == "Investment Advisor":
    predict.render(df)
else:
    model_perf.render(df)