import pandas as pd
import os
import glob
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

BASE_PATH   = "/Users/sumiregarcia/Desktop/INTERSHIP/IDX/CVS/SOLD"   
OUTPUT_PATH = os.path.join(BASE_PATH, "output")
os.makedirs(OUTPUT_PATH, exist_ok=True)


# WEEK 1 – Monthly Dataset Aggregation (Sold)
# Goal: Find all CRMLSSold CSVs, concatenate them, filter to Residential,
#       print row counts before/after, and save a combined CSV.

print("=" * 65)
print("WEEK 1 – Monthly Dataset Aggregation  (sold_analysis.py)")
print("=" * 65)

# Discover all Sold monthly files 
sold_files = sorted(glob.glob(os.path.join(BASE_PATH, "CRMLSSold*.csv")))

print(f"\nFound {len(sold_files)} Sold files:")
for f in sold_files:
    print(f"  {os.path.basename(f)}")

if len(sold_files) == 0:
    raise FileNotFoundError(
        f"No CRMLSSold*.csv files found in {BASE_PATH}\n"
        "Double-check BASE_PATH at the top of this script."
    )

# Load and concatenate 
frames = []
for f in sold_files:
    df = pd.read_csv(f, low_memory=False)
    frames.append(df)

sold_raw = pd.concat(frames, ignore_index=True)
print(f"\nRow count BEFORE Residential filter : {len(sold_raw):,}")
print(f"Column count                        : {sold_raw.shape[1]}")

# Show all unique PropertyType values found 
print(f"\nPropertyType values in raw data:")
print(sold_raw["PropertyType"].value_counts().to_string())

# Filter to Residential only
sold = sold_raw[sold_raw["PropertyType"] == "Residential"].copy()

print(f"\nRow count AFTER  Residential filter : {len(sold):,}")
print(f"Rows removed (non-residential)      : {len(sold_raw) - len(sold):,}")

# Save 
out_path = os.path.join(OUTPUT_PATH, "sold_residential_combined.csv")
sold.to_csv(out_path, index=False)
print(f"\nSaved → {out_path}")

