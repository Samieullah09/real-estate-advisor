import pandas as pd

def main():
    # Load the raw dataset
    df = pd.read_csv("data/raw/india_housing_prices.csv")

    print("Shape:", df.shape)
    print("\nColumn types:\n", df.dtypes)

    # Missing values and duplicates
    print("\nMissing values per column:\n", df.isna().sum())
    print("Duplicate rows:", df.duplicated().sum())
    print("Duplicate IDs:", df["ID"].duplicated().sum())

    # Numeric summary: look at min, max and mean for odd values
    print("\nNumeric summary:\n", df.describe().T)

    # Logical checks
    print("\nFloor_No > Total_Floors:", (df["Floor_No"] > df["Total_Floors"]).sum())
    print("Age mismatch (2025 - Year_Built):",
          ((2025 - df["Year_Built"]) != df["Age_of_Property"]).sum())

    # Categorical columns: check spelling and spaces
    for col in ["Property_Type", "Furnished_Status", "Facing", "Owner_Type",
                "Availability_Status", "Public_Transport_Accessibility"]:
        print(f"\n{col}:", df[col].unique())

if __name__ == "__main__":
    main()