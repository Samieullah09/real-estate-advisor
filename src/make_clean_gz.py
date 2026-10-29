import pandas as pd

SRC = "data/processed/housing_clean.csv"
DST = "data/processed/housing_clean.csv.gz"

df = pd.read_csv(SRC)
df.to_csv(DST, index=False, compression="gzip")
print("saved", DST, df.shape)