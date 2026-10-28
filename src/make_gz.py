import pandas as pd

SRC = "data/processed/housing_ml_ready.csv"
DST = "data/processed/housing_ml_ready.csv.gz"

df = pd.read_csv(SRC)
df = df.round(4)                       # shorter decimals make the file much smaller
df.to_csv(DST, index=False, compression="gzip")
print("saved", DST, df.shape)