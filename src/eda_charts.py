import os

import pandas as pd
import plotly.express as px

DATA_PATH = "data/processed/housing_ml_ready.csv"
OUT_DIR = "reports/eda"
TEMPLATE = "plotly_dark"


def q1_price_distribution(df):
    # Q1: distribution of property prices
    return px.histogram(df, x="Price_in_Lakhs", nbins=50, template=TEMPLATE,
                        title="Q1: Distribution of property prices (lakhs)")


def q2_size_distribution(df):
    # Q2: distribution of property sizes
    return px.histogram(df, x="Size_in_SqFt", nbins=50, template=TEMPLATE,
                        title="Q2: Distribution of property sizes (sq ft)")


def q3_pps_by_type(df):
    # Q3: price per sq ft by property type
    g = df.groupby("Property_Type")["Price_per_SqFt_Rs"].mean().reset_index()
    return px.bar(g, x="Property_Type", y="Price_per_SqFt_Rs", text_auto=".0f",
                  template=TEMPLATE, title="Q3: Avg price per sq ft by property type (Rs)")


def q4_size_vs_price(df):
    # Q4: relationship between size and price (sampled for speed)
    sample = df.sample(min(5000, len(df)), random_state=42)
    return px.scatter(sample, x="Size_in_SqFt", y="Price_in_Lakhs", opacity=0.5,
                      template=TEMPLATE, title="Q4: Size vs price (5,000 sampled properties)")


def q5_outliers(df):
    # Q5: outliers in price per sq ft
    return px.box(df, x="Property_Type", y="Price_per_SqFt_Rs", template=TEMPLATE,
                  title="Q5: Price per sq ft outliers by property type (Rs)")

def q6_pps_by_state(df):
    # Q6: average price per sq ft by state
    g = (df.groupby("State")["Price_per_SqFt_Rs"].mean()
         .sort_values().reset_index())
    return px.bar(g, x="Price_per_SqFt_Rs", y="State", orientation="h", text_auto=".0f",
                  template=TEMPLATE, title="Q6: Avg price per sq ft by state (Rs)")


def q7_price_by_city(df):
    # Q7: average property price by city (top 15 shown)
    g = (df.groupby("City")["Price_in_Lakhs"].mean()
         .sort_values().tail(15).reset_index())
    return px.bar(g, x="Price_in_Lakhs", y="City", orientation="h", text_auto=".1f",
                  template=TEMPLATE, title="Q7: Top 15 cities by average price (lakhs)")


def q8_age_by_locality(df):
    # Q8: median age of properties by locality (locality names repeat across cities)
    g = df.groupby("Locality")["Age_of_Property"].median().reset_index()
    return px.histogram(g, x="Age_of_Property", nbins=20, template=TEMPLATE,
                        title="Q8: Median property age across 500 localities (years)")


def q9_bhk_by_city(df):
    # Q9: BHK distribution across cities (share in %)
    g = df.groupby(["City", "BHK"]).size().reset_index(name="Count")
    g["Share_Pct"] = g["Count"] / g.groupby("City")["Count"].transform("sum") * 100
    return px.bar(g, x="City", y="Share_Pct", color=g["BHK"].astype(str), template=TEMPLATE,
                  title="Q9: BHK mix by city (%)", labels={"color": "BHK"})


def q10_top_locality_trend(df):
    # Q10: no date column exists, so Year_Built is used as the time axis
    top5 = df.groupby("Locality")["Price_in_Lakhs"].mean().nlargest(5).index
    g = (df[df["Locality"].isin(top5)]
         .groupby(["Year_Built", "Locality"])["Price_in_Lakhs"].mean().reset_index())
    return px.line(g, x="Year_Built", y="Price_in_Lakhs", color="Locality", template=TEMPLATE,
                   title="Q10: Avg price by year built, top 5 most expensive localities")

def q11_correlation(df):
    # Q11: correlation between numeric features
    cols = ["BHK", "Size_in_SqFt", "Price_in_Lakhs", "Price_per_SqFt_Rs", "Age_of_Property",
            "Nearby_Schools", "Nearby_Hospitals", "Floor_No", "Amenity_Count", "Infra_Score"]
    return px.imshow(df[cols].corr().round(2), text_auto=True, zmin=-1, zmax=1,
                     color_continuous_scale="RdBu_r", template=TEMPLATE,
                     title="Q11: Correlation matrix of numeric features")


def q12_schools_vs_pps(df):
    # Q12: nearby schools vs price per sq ft
    g = df.groupby("Nearby_Schools")["Price_per_SqFt_Rs"].mean().reset_index()
    return px.bar(g, x="Nearby_Schools", y="Price_per_SqFt_Rs", text_auto=".0f",
                  template=TEMPLATE, title="Q12: Avg price per sq ft by nearby schools (Rs)")


def q13_hospitals_vs_pps(df):
    # Q13: nearby hospitals vs price per sq ft
    g = df.groupby("Nearby_Hospitals")["Price_per_SqFt_Rs"].mean().reset_index()
    return px.bar(g, x="Nearby_Hospitals", y="Price_per_SqFt_Rs", text_auto=".0f",
                  template=TEMPLATE, title="Q13: Avg price per sq ft by nearby hospitals (Rs)")


def q14_price_by_furnishing(df):
    # Q14: price by furnished status
    g = df.groupby("Furnished_Status")["Price_in_Lakhs"].mean().reset_index()
    return px.bar(g, x="Furnished_Status", y="Price_in_Lakhs", text_auto=".1f",
                  template=TEMPLATE, title="Q14: Avg price by furnished status (lakhs)")


def q15_pps_by_facing(df):
    # Q15: price per sq ft by facing direction
    g = df.groupby("Facing")["Price_per_SqFt_Rs"].mean().reset_index()
    return px.bar(g, x="Facing", y="Price_per_SqFt_Rs", text_auto=".0f",
                  template=TEMPLATE, title="Q15: Avg price per sq ft by facing (Rs)")

def q16_owner_type(df):
    # Q16: number of properties per owner type
    g = df["Owner_Type"].value_counts().reset_index()
    return px.bar(g, x="Owner_Type", y="count", text_auto=",", template=TEMPLATE,
                  title="Q16: Properties by owner type")


def q17_availability(df):
    # Q17: number of properties per availability status
    g = df["Availability_Status"].value_counts().reset_index()
    return px.pie(g, names="Availability_Status", values="count", hole=0.5,
                  template=TEMPLATE, title="Q17: Properties by availability status")


def q18_parking_vs_price(df):
    # Q18: does parking space affect price?
    g = df.groupby("Parking_Space")["Price_in_Lakhs"].mean().reset_index()
    return px.bar(g, x="Parking_Space", y="Price_in_Lakhs", text_auto=".1f",
                  template=TEMPLATE, title="Q18: Avg price by parking space (lakhs)")


def q19_amenities_vs_pps(df):
    # Q19: amenity count vs price per sq ft
    g = df.groupby("Amenity_Count")["Price_per_SqFt_Rs"].mean().reset_index()
    return px.bar(g, x="Amenity_Count", y="Price_per_SqFt_Rs", text_auto=".0f",
                  template=TEMPLATE, title="Q19: Avg price per sq ft by number of amenities (Rs)")


def q20_transport_vs_pps(df):
    # Q20: public transport accessibility vs price per sq ft
    order = ["Low", "Medium", "High"]
    g = df.groupby("Public_Transport_Accessibility")["Price_per_SqFt_Rs"].mean().reindex(order).reset_index()
    return px.bar(g, x="Public_Transport_Accessibility", y="Price_per_SqFt_Rs", text_auto=".0f",
                  template=TEMPLATE, title="Q20: Avg price per sq ft by transport accessibility (Rs)")


FIGURES = {
    "q1_price_distribution": q1_price_distribution,
    "q2_size_distribution": q2_size_distribution,
    "q3_pps_by_type": q3_pps_by_type,
    "q4_size_vs_price": q4_size_vs_price,
    "q5_outliers": q5_outliers,
    "q6_pps_by_state": q6_pps_by_state,
    "q7_price_by_city": q7_price_by_city,
    "q8_age_by_locality": q8_age_by_locality,
    "q9_bhk_by_city": q9_bhk_by_city,
    "q10_top_locality_trend": q10_top_locality_trend,
    "q11_correlation": q11_correlation,
    "q12_schools_vs_pps": q12_schools_vs_pps,
    "q13_hospitals_vs_pps": q13_hospitals_vs_pps,
    "q14_price_by_furnishing": q14_price_by_furnishing,
    "q15_pps_by_facing": q15_pps_by_facing,
    "q16_owner_type": q16_owner_type,
    "q17_availability": q17_availability,
    "q18_parking_vs_price": q18_parking_vs_price,
    "q19_amenities_vs_pps": q19_amenities_vs_pps,
    "q20_transport_vs_pps": q20_transport_vs_pps,
}


def main():
    df = pd.read_csv(DATA_PATH)
    os.makedirs(OUT_DIR, exist_ok=True)

    # Save every chart as an HTML file you can open in the browser
    for name, func in FIGURES.items():
        func(df).write_html(f"{OUT_DIR}/{name}.html")

    # Print the numeric answers (use these as insight text in the report)
    print("Q1 price (lakhs): mean %.1f | median %.1f | min %.0f | max %.0f" % (
        df["Price_in_Lakhs"].mean(), df["Price_in_Lakhs"].median(),
        df["Price_in_Lakhs"].min(), df["Price_in_Lakhs"].max()))
    print("Q2 size (sqft): mean %.0f | median %.0f | min %d | max %d" % (
        df["Size_in_SqFt"].mean(), df["Size_in_SqFt"].median(),
        df["Size_in_SqFt"].min(), df["Size_in_SqFt"].max()))
    print("Q3 avg Rs/sqft by type:")
    print(df.groupby("Property_Type")["Price_per_SqFt_Rs"].mean().round(0))
    print("Q4 correlation size vs price: %.3f" % df["Size_in_SqFt"].corr(df["Price_in_Lakhs"]))
    print("Q5 Rs/sqft outliers: %d (%.1f%% of rows)" % (
        df["Is_PPS_Outlier"].sum(), df["Is_PPS_Outlier"].mean() * 100))
    state_pps = df.groupby("State")["Price_per_SqFt_Rs"].mean().sort_values()
    print("Q6 lowest state: %s (%.0f) | highest: %s (%.0f)" % (
        state_pps.index[0], state_pps.iloc[0], state_pps.index[-1], state_pps.iloc[-1]))
    city_price = df.groupby("City")["Price_in_Lakhs"].mean().sort_values()
    print("Q7 lowest city: %s (%.1f) | highest: %s (%.1f)" % (
        city_price.index[0], city_price.iloc[0], city_price.index[-1], city_price.iloc[-1]))
    loc_age = df.groupby("Locality")["Age_of_Property"].median()
    print("Q8 locality median age: min %.1f | max %.1f | overall %.1f" % (
        loc_age.min(), loc_age.max(), df["Age_of_Property"].median()))
    bhk_share = df.groupby("City")["BHK"].value_counts(normalize=True).unstack() * 100
    print("Q9 BHK share (%) range across cities:")
    print(bhk_share.agg(["min", "max"]).round(1))
    top5 = df.groupby("Locality")["Price_in_Lakhs"].mean().nlargest(5)
    print("Q10 top 5 localities by avg price:")
    print(top5.round(1))
    corr = df[["Size_in_SqFt", "Price_in_Lakhs", "Price_per_SqFt_Rs", "Age_of_Property",
               "Nearby_Schools", "Nearby_Hospitals"]].corr()
    print("Q11 key correlations:")
    print("  Price vs Size: %.3f | Price vs Rs/sqft: %.3f | Size vs Rs/sqft: %.3f" % (
        corr.loc["Price_in_Lakhs", "Size_in_SqFt"], corr.loc["Price_in_Lakhs", "Price_per_SqFt_Rs"],
        corr.loc["Size_in_SqFt", "Price_per_SqFt_Rs"]))
    print("  Schools vs Rs/sqft: %.3f | Hospitals vs Rs/sqft: %.3f" % (
        corr.loc["Nearby_Schools", "Price_per_SqFt_Rs"], corr.loc["Nearby_Hospitals", "Price_per_SqFt_Rs"]))
    for col, name in [("Nearby_Schools", "Q12"), ("Nearby_Hospitals", "Q13")]:
        g = df.groupby(col)["Price_per_SqFt_Rs"].mean()
        print("%s Rs/sqft by %s: min %.0f | max %.0f" % (name, col, g.min(), g.max()))
    print("Q14 avg price (lakhs) by furnishing:")
    print(df.groupby("Furnished_Status")["Price_in_Lakhs"].mean().round(1))
    print("Q15 avg Rs/sqft by facing:")
    print(df.groupby("Facing")["Price_per_SqFt_Rs"].mean().round(0))
    print("Q16 owner type counts:")
    print(df["Owner_Type"].value_counts())
    print("Q17 availability counts:")
    print(df["Availability_Status"].value_counts())
    print("Q18 avg price (lakhs) by parking:")
    print(df.groupby("Parking_Space")["Price_in_Lakhs"].mean().round(1))
    print("Q19 avg Rs/sqft by amenity count:")
    print(df.groupby("Amenity_Count")["Price_per_SqFt_Rs"].mean().round(0))
    print("Q20 avg Rs/sqft and Good Investment % by transport:")
    print(df.groupby("Public_Transport_Accessibility").agg(
        Rs_per_sqft=("Price_per_SqFt_Rs", "mean"), Good_Pct=("Investment_Label", "mean")).round(3))


if __name__ == "__main__":
    main()