import numpy as np
import pandas as pd

IN_PATH = "data/processed/housing_clean.csv"
OUT_PATH = "data/processed/housing_ml_ready.csv"

# Growth model assumptions (write these in the project report)
BASE_RATE = 0.04
GOOD_THRESHOLD_PCT = 35      # Good Investment if 5-year appreciation > 35%
NOISE_STD = 0.005            # unknown market factors
SEED = 42

def main():
    df = pd.read_csv(IN_PATH)

    # --- Feature engineering ---
    df["Amenity_Count"] = df["Amenities"].str.count(",") + 1
    transport = df["Public_Transport_Accessibility"].map({"Low": 0, "Medium": 0.5, "High": 1})
    df["Infra_Score"] = (df["Nearby_Schools"] / 10 + df["Nearby_Hospitals"] / 10 + transport) / 3
    df["Floor_Ratio"] = df["Floor_No"] / df["Total_Floors"]
    city_median = df.groupby("City")["Price_per_SqFt_Rs"].transform("median")
    df["Price_vs_City_Median"] = df["Price_per_SqFt_Rs"] / city_median

    # --- Yearly growth rate model ---
    under_construction = (df["Availability_Status"] == "Under_Construction").astype(float)
    value_gap = (1 - df["Price_vs_City_Median"]).clip(-0.5, 0.5)   # cheaper than city = positive
    rng = np.random.default_rng(SEED)
    df["Growth_Rate"] = (
        BASE_RATE
        + 0.030 * df["Infra_Score"]
        + 0.010 * df["Amenity_Count"] / 5
        - 0.0004 * df["Age_of_Property"]
        + 0.010 * under_construction
        + 0.030 * value_gap
        + rng.normal(0, NOISE_STD, len(df))
    )

    # --- Targets ---
    df["Future_Price_5Y"] = df["Price_in_Lakhs"] * (1 + df["Growth_Rate"]) ** 5
    df["Appreciation_5Y_Pct"] = ((1 + df["Growth_Rate"]) ** 5 - 1) * 100
    df["Investment_Label"] = (df["Appreciation_5Y_Pct"] > GOOD_THRESHOLD_PCT).astype(int)
    df["Investment_Label_Name"] = df["Investment_Label"].map(
        {1: "Good Investment", 0: "Needs Further Review"}
    )

    df.to_csv(OUT_PATH, index=False)
    print("Saved:", OUT_PATH, df.shape)
    print("Good Investment share: %.1f%%" % (df["Investment_Label"].mean() * 100))
    print(df[["Growth_Rate", "Appreciation_5Y_Pct", "Future_Price_5Y"]].describe().round(3))

if __name__ == "__main__":
    main()