import pandas as pd

RAW_PATH = "data/raw/india_housing_prices.csv"
OUT_PATH = "data/processed/housing_clean.csv"

def main():
    df = pd.read_csv(RAW_PATH)

    # 1. Strip spaces from all text columns (safety step)
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in text_cols:
        df[col] = df[col].str.strip()

    # 2. Floor logic: flag mismatches, then fix Total_Floors
    df["Floor_Mismatch"] = df["Floor_No"] > df["Total_Floors"]
    df["Total_Floors"] = df[["Floor_No", "Total_Floors"]].max(axis=1)

    # 3. Rebuild price per sqft in rupees (original was rounded in lakhs)
    df["Price_per_SqFt_Rs"] = df["Price_in_Lakhs"] * 100000 / df["Size_in_SqFt"]

    # 4. Flag price-per-sqft outliers with the IQR method (do not delete)
    q1, q3 = df["Price_per_SqFt_Rs"].quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    df["Is_PPS_Outlier"] = (df["Price_per_SqFt_Rs"] < low) | (df["Price_per_SqFt_Rs"] > high)

    # 5. Save the cleaned dataset
    df.to_csv(OUT_PATH, index=False)

    print("Saved:", OUT_PATH, df.shape)
    print("Floor mismatches fixed:", df["Floor_Mismatch"].sum())
    print("PPS outliers flagged:", df["Is_PPS_Outlier"].sum())
    print("Remaining Floor_No > Total_Floors:", (df["Floor_No"] > df["Total_Floors"]).sum())

if __name__ == "__main__":
    main()