import streamlit as st

from app_pages.theme import CYAN, GREEN, ORANGE, PURPLE, kpi

SORTS = {
    "Price: low to high": ("Price_in_Lakhs", True),
    "Price: high to low": ("Price_in_Lakhs", False),
    "Price per sq ft: low to high": ("Price_per_SqFt_Rs", True),
    "Size: large to small": ("Size_in_SqFt", False),
    "Newest first": ("Age_of_Property", True),
    "Best 5-year growth": ("Appreciation_5Y_Pct", False),
}
SHOW = ["State", "City", "Locality", "Property_Type", "BHK", "Size_in_SqFt", "Price_in_Lakhs",
        "Price_per_SqFt_Rs", "Age_of_Property", "Availability_Status", "Investment_Label_Name"]
MAX_ROWS = 500


def render(df):
    st.title("Property Explorer")
    st.caption("Filter the listings by area, price, BHK and more, then look at the matching properties.")

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        states = c1.multiselect("State", sorted(df["State"].unique()))
        pool = df[df["State"].isin(states)] if states else df
        cities = c2.multiselect("City", sorted(pool["City"].unique()))
        types = c3.multiselect("Property type", sorted(df["Property_Type"].unique()))
        c4, c5, c6 = st.columns(3)
        bhk = c4.multiselect("BHK", sorted(df["BHK"].unique()))
        price = c5.slider("Price (₹ lakhs)", 10, 500, (10, 500))
        size = c6.slider("Size (sq ft)", 500, 5000, (500, 5000), step=50)
        c7, c8, c9 = st.columns(3)
        status = c7.multiselect("Availability", sorted(df["Availability_Status"].unique()))
        sort_name = c8.selectbox("Sort by", list(SORTS))
        only_good = c9.checkbox("Only Good Investments")

    # Build one mask from all active filters (empty selection means "all")
    mask = df["Price_in_Lakhs"].between(*price) & df["Size_in_SqFt"].between(*size)
    for col, picked in [("State", states), ("City", cities), ("Property_Type", types),
                        ("BHK", bhk), ("Availability_Status", status)]:
        if picked:
            mask &= df[col].isin(picked)
    if only_good:
        mask &= df["Investment_Label"] == 1
    found = df[mask]

    if found.empty:
        st.warning("No properties match these filters. Try widening the price or size range.")
        return

    cols = st.columns(4)
    cards = [("MATCHING PROPERTIES", f"{len(found):,}", f"of {len(df):,} listings", CYAN),
             ("AVG PRICE", f"₹{found['Price_in_Lakhs'].mean():.1f} L", "mean listed price", GREEN),
             ("AVG PRICE PER SQFT", f"₹{found['Price_per_SqFt_Rs'].mean():,.0f}", "mean of price ÷ size", PURPLE),
             ("GOOD INVESTMENTS", f"{found['Investment_Label'].mean() * 100:.1f}%", "5-yr growth above 35%", ORANGE)]
    for col, (label, value, sub, color) in zip(cols, cards):
        col.markdown(kpi(label, value, sub, color), unsafe_allow_html=True)
    st.write("")

    sort_col, ascending = SORTS[sort_name]
    view = found.sort_values(sort_col, ascending=ascending).head(MAX_ROWS)[SHOW]
    st.markdown(f"**Showing the first {len(view):,} of {len(found):,} matching properties**")
    st.dataframe(view, hide_index=True, width="stretch", height=460, column_config={
        "Price_in_Lakhs": st.column_config.NumberColumn("Price (₹ L)", format="%.1f"),
        "Price_per_SqFt_Rs": st.column_config.NumberColumn("₹ / sq ft", format="%,.0f"),
        "Size_in_SqFt": st.column_config.NumberColumn("Size (sq ft)", format="%d"),
        "Age_of_Property": st.column_config.NumberColumn("Age (yrs)", format="%d"),
        "Investment_Label_Name": "Verdict",
    })
    st.download_button("Download these rows (CSV)", view.to_csv(index=False).encode("utf-8"),
                       file_name="filtered_properties.csv", mime="text/csv")
