import plotly.express as px
import streamlit as st

from app_pages.theme import CYAN, PURPLE, GREEN, ORANGE, PALETTE, kpi, insight, style_fig


def render(df):
    st.markdown("""
<div class="hero"><h1>Invest Smarter in India's Real Estate</h1>
<p>Explore the housing market, check if a property is a good investment, and estimate its price after 5 years.</p>
<div class="feat"><div>🏷️ Investment Recommendation</div><div>📈 5-Year Price Forecast</div>
<div>📊 Data-Driven Insights</div><div>🧪 ML Model Tracking</div></div></div>""", unsafe_allow_html=True)

    # --- KPI cards (all values come from the dataset) ---
    cols = st.columns(5)
    cards = [
        ("TOTAL PROPERTIES", f"{len(df):,}", "listings analysed", CYAN),
        ("AVG PROPERTY PRICE", f"₹{df['Price_in_Lakhs'].mean():.1f} L", "mean listed price", GREEN),
        ("AVG PRICE PER SQFT", f"₹{df['Price_per_SqFt_Rs'].mean():,.0f}", "mean of price ÷ size", PURPLE),
        ("GOOD INVESTMENTS", f"{df['Investment_Label'].mean() * 100:.1f}%", "5-yr growth above 35%", ORANGE),
        ("CITIES COVERED", f"{df['City'].nunique()}", f"across {df['State'].nunique()} states", CYAN),
    ]
    for col, (label, value, sub, color) in zip(cols, cards):
        col.markdown(kpi(label, value, sub, color), unsafe_allow_html=True)
    st.write("")

    # --- Row 1: three charts ---
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.markdown("**Top 10 States by Avg Price per SqFt (₹)**")
        g = df.groupby("State")["Price_per_SqFt_Rs"].mean().sort_values().tail(10).reset_index()
        fig = px.bar(g, x="Price_per_SqFt_Rs", y="State", orientation="h", text_auto=".0f")
        fig.update_traces(marker_color=CYAN)
        fig.update_xaxes(range=[g["Price_per_SqFt_Rs"].min() * 0.98, g["Price_per_SqFt_Rs"].max() * 1.01])
        st.plotly_chart(style_fig(fig, 320), width="stretch")
    with c2:
        st.markdown("**Property Type Distribution**")
        g = df["Property_Type"].value_counts().reset_index()
        fig = px.pie(g, names="Property_Type", values="count", hole=0.6, color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(fig, 320), width="stretch")
    with c3:
        st.markdown("**Top 5 Cities by Avg Price (₹ Lakhs)**")
        g = df.groupby("City")["Price_in_Lakhs"].mean().sort_values(ascending=False).head(5).reset_index()
        fig = px.bar(g, x="City", y="Price_in_Lakhs", text_auto=".1f")
        fig.update_traces(marker_color=PURPLE)
        fig.update_yaxes(range=[g["Price_in_Lakhs"].min() * 0.97, g["Price_in_Lakhs"].max() * 1.01])
        st.plotly_chart(style_fig(fig, 320), width="stretch")

    # --- Row 2: heatmap + investment share ---
    c4, c5 = st.columns([1.5, 1])
    with c4:
        st.markdown("**Avg Price Heatmap: State × Property Type (₹ Lakhs)**")
        pivot = df.pivot_table(index="State", columns="Property_Type", values="Price_in_Lakhs", aggfunc="mean")
        pivot = pivot.loc[pivot.mean(axis=1).sort_values().index]
        fig = px.imshow(pivot.round(1), text_auto=True, aspect="auto",
                        color_continuous_scale=["#0b1d3a", "#0e7490", CYAN])
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig, 430), width="stretch")
    with c5:
        st.markdown("**Good Investment Share by Property Type (%)**")
        g = (df.groupby("Property_Type")["Investment_Label"].mean() * 100).reset_index()
        fig = px.bar(g, x="Property_Type", y="Investment_Label", text_auto=".1f")
        fig.update_traces(marker_color=GREEN)
        fig.update_yaxes(range=[0, 60])
        st.plotly_chart(style_fig(fig, 430), width="stretch")

    # --- Key insights computed from the data ---
    state_pps = df.groupby("State")["Price_per_SqFt_Rs"].mean()
    city_price = df.groupby("City")["Price_in_Lakhs"].mean()
    transport = df.groupby("Public_Transport_Accessibility")["Investment_Label"].mean() * 100
    st.markdown("**Key Insights**")
    i1, i2, i3, i4 = st.columns(4)
    i1.markdown(insight("HIGHEST ₹/SQFT STATE", state_pps.idxmax(),
                        f"₹{state_pps.max():,.0f} per sqft on average", GREEN), unsafe_allow_html=True)
    i2.markdown(insight("COSTLIEST CITY", city_price.idxmax(),
                        f"₹{city_price.max():.1f} L average price", CYAN), unsafe_allow_html=True)
    i3.markdown(insight("BEST TRANSPORT TIER", transport.idxmax(),
                        f"{transport.max():.0f}% rated Good Investment", PURPLE), unsafe_allow_html=True)
    i4.markdown(insight("DATA NOTE", "Prices are very uniform",
                        "Differences across cities and types are small (under ~3%)", ORANGE),
                unsafe_allow_html=True)
    st.info("Figures describe the supplied dataset. The Good Investment label comes from a growth-rate "
            "model with stated assumptions; it is not a guarantee of future returns.")