import plotly.express as px
import streamlit as st

from app_pages.theme import PALETTE, style_fig
from src import eda_charts as eda

# Use the app colours for every Plotly Express chart
px.defaults.color_discrete_sequence = PALETTE

GROUPS = {
    "Price & Size (Q1-5)": ["q1_price_distribution", "q2_size_distribution", "q3_pps_by_type",
                            "q4_size_vs_price", "q5_outliers"],
    "Location (Q6-10)": ["q6_pps_by_state", "q7_price_by_city", "q8_age_by_locality",
                         "q9_bhk_by_city", "q10_top_locality_trend"],
    "Relationships (Q11-15)": ["q11_correlation", "q12_schools_vs_pps", "q13_hospitals_vs_pps",
                               "q14_price_by_furnishing", "q15_pps_by_facing"],
    "Ownership & Amenities (Q16-20)": ["q16_owner_type", "q17_availability", "q18_parking_vs_price",
                                       "q19_amenities_vs_pps", "q20_transport_vs_pps"],
}


def gap(series):
    # Difference between the highest and lowest group, in percent of the lowest
    return (series.max() - series.min()) / series.min() * 100


def build_insights(df):
    # Every sentence is calculated from the (filtered) data, nothing is hard-coded
    p, s, pps = df["Price_in_Lakhs"], df["Size_in_SqFt"], "Price_per_SqFt_Rs"
    by = lambda col, val="Price_per_SqFt_Rs": df.groupby(col)[val].mean()
    state, city = by("State"), df.groupby("City")["Price_in_Lakhs"].mean()
    loc_age = df.groupby("Locality")["Age_of_Property"].median()
    bhk = df.groupby("City")["BHK"].value_counts(normalize=True) * 100
    owner = df["Owner_Type"].value_counts(normalize=True) * 100
    avail = df["Availability_Status"].value_counts(normalize=True) * 100
    parking = df.groupby("Parking_Space")["Price_in_Lakhs"].mean()
    amen, transport = by("Amenity_Count"), by("Public_Transport_Accessibility")
    good = df.groupby("Public_Transport_Accessibility")["Investment_Label"].mean() * 100
    corr = df[["Size_in_SqFt", "Price_in_Lakhs", pps]].corr()
    return {
        "q1_price_distribution": f"Prices run from ₹{p.min():.0f}L to ₹{p.max():.0f}L (mean ₹{p.mean():.1f}L) and are spread almost evenly.",
        "q2_size_distribution": f"Sizes run from {s.min()} to {s.max()} sq ft (mean {s.mean():.0f}) and are spread almost evenly.",
        "q3_pps_by_type": f"Average ₹/sqft differs by only {gap(by('Property_Type')):.1f}% between property types.",
        "q4_size_vs_price": f"Correlation between size and price is {corr.loc['Size_in_SqFt', 'Price_in_Lakhs']:.3f}: size alone does not explain price.",
        "q5_outliers": f"{df['Is_PPS_Outlier'].sum():,} properties ({df['Is_PPS_Outlier'].mean() * 100:.1f}%) are ₹/sqft outliers, mostly small size with a high price.",
        "q6_pps_by_state": f"{state.idxmax()} is highest (₹{state.max():,.0f}) and {state.idxmin()} lowest (₹{state.min():,.0f}), a gap of {gap(state):.1f}%.",
        "q7_price_by_city": f"{city.idxmax()} has the highest average price (₹{city.max():.1f}L), {city.idxmin()} the lowest (₹{city.min():.1f}L), a gap of {gap(city):.1f}%.",
        "q8_age_by_locality": f"Median age by locality ranges from {loc_age.min():.0f} to {loc_age.max():.0f} years: localities are similar in age.",
        "q9_bhk_by_city": f"Each BHK type holds between {bhk.min():.0f}% and {bhk.max():.0f}% of listings in every city.",
        "q10_top_locality_trend": "The data has no date column, so Year_Built is the time axis. Lines zigzag without a steady trend because each year has few listings.",
        "q11_correlation": f"Real features are almost uncorrelated. The visible links with ₹/sqft (price {corr.loc[pps, 'Price_in_Lakhs']:.2f}, size {corr.loc[pps, 'Size_in_SqFt']:.2f}) exist only because ₹/sqft = price ÷ size. Infra_Score is built from schools, hospitals and transport, so it links to them by design.",
        "q12_schools_vs_pps": f"Across 1 to 10 nearby schools, average ₹/sqft varies by only {gap(by('Nearby_Schools')):.1f}% with no clear trend.",
        "q13_hospitals_vs_pps": f"Across 1 to 10 nearby hospitals, average ₹/sqft varies by only {gap(by('Nearby_Hospitals')):.1f}% with no clear trend.",
        "q14_price_by_furnishing": f"Furnishing status changes average price by only {gap(df.groupby('Furnished_Status')['Price_in_Lakhs'].mean()):.1f}%.",
        "q15_pps_by_facing": f"Facing direction changes average ₹/sqft by only {gap(by('Facing')):.1f}%.",
        "q16_owner_type": "Owner types share the listings almost equally: " + ", ".join(f"{k} {v:.0f}%" for k, v in owner.items()) + ".",
        "q17_availability": "Availability is split almost evenly: " + ", ".join(f"{k.replace('_', ' ')} {v:.0f}%" for k, v in avail.items()) + ".",
        "q18_parking_vs_price": f"Parking changes average price by only {gap(parking):.1f}%.",
        "q19_amenities_vs_pps": f"Going from 1 to 5 amenities changes average ₹/sqft by {(amen.iloc[-1] / amen.iloc[0] - 1) * 100:+.1f}%, a very small effect.",
        "q20_transport_vs_pps": f"Transport access shifts ₹/sqft by only {gap(transport):.1f}%. Under our growth model, Good Investment share is {good.max():.0f}% for {good.idxmax()} vs {good.min():.0f}% for {good.idxmin()}: that comes from the model's assumption, not from raw prices.",
    }


def filter_data(df):
    with st.expander("Filters (apply to every chart)", expanded=False):
        a, b, c = st.columns(3)
        states = a.multiselect("State", sorted(df["State"].unique()))
        bhks = b.multiselect("BHK", sorted(df["BHK"].unique()))
        low, high = c.slider("Price (₹ lakhs)", 10, 500, (10, 500))
    out = df[df["Price_in_Lakhs"].between(low, high)]
    if states:
        out = out[out["State"].isin(states)]
    if bhks:
        out = out[out["BHK"].isin(bhks)]
    return out


def render(df):
    st.title("EDA Explorer")
    st.caption("All 20 exploratory questions. Insights under each chart are calculated from the filtered data.")
    data = filter_data(df)
    if len(data) < 100:
        st.warning("Too few properties match these filters. Please widen them.")
        return
    st.write(f"Properties analysed: **{len(data):,}**")

    group = st.radio("Question group", list(GROUPS), horizontal=True, label_visibility="collapsed")
    notes = build_insights(data)
    names = GROUPS[group]
    for i in range(0, len(names), 2):
        cols = st.columns(2)
        for col, name in zip(cols, names[i:i + 2]):
            fig = eda.FIGURES[name](data)
            title = fig.layout.title.text
            fig.update_layout(title=None)
            with col.container(border=True):
                st.markdown(f"**{title}**")
                st.plotly_chart(style_fig(fig, 340), width="stretch")
                st.markdown(f'<div style="border-left:3px solid #f472b6;padding:6px 10px;'
                            f'background:rgba(244,114,182,.07);font-size:13px;color:#c9d6ee">'
                            f'💡 {notes[name]}</div>', unsafe_allow_html=True)