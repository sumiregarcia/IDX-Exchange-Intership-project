import pandas as pd
import os
import glob
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

BASE_PATH = "/Users/sumiregarcia/Desktop/INTERSHIP/IDX/CVS/LISTING"
OUTPUT_PATH = os.path.join(BASE_PATH, "output")
os.makedirs(OUTPUT_PATH, exist_ok=True)


# WEEK 1 – Monthly Dataset Aggregation (Listing)
# Goal: Find all CRMLSListing CSVs, concatenate them, 
# drop duplicate columns from the export artifact (.1 suffix), filter to Residential,
# print row counts before/after, and save a combined CSV.


print("=" * 65)
print("WEEK 1 – Monthly Dataset Aggregation  (listing_analysis.py)")
print("=" * 65)

# Discover all Listing monthly files
listing_files = sorted(glob.glob(os.path.join(BASE_PATH, "CRMLSListing*.csv")))

print(f"\nFound {len(listing_files)} Listing files:")
for f in listing_files:
    print(f"  {os.path.basename(f)}")

if len(listing_files) == 0:
    raise FileNotFoundError(
        f"No CRMLSListing*.csv files found in {BASE_PATH}\n"
        "Double-check BASE_PATH at the top of this script."
    )

frames = []
for f in listing_files:
    df = pd.read_csv(f, low_memory=False)

    # Drop duplicate columns 
    dupe_cols = [c for c in df.columns if c.endswith(".1")]
    df = df.drop(columns=dupe_cols)

    frames.append(df)

listing_raw = pd.concat(frames, ignore_index=True)
print(f"\nRow count BEFORE Residential filter : {len(listing_raw):,}")
print(f"Column count (after dedup cleanup)  : {listing_raw.shape[1]}")

# Show all unique PropertyType values found
print(f"\nPropertyType values in raw data:")
print(listing_raw["PropertyType"].value_counts().to_string())

# Filter to Residential only
listing = listing_raw[listing_raw["PropertyType"] == "Residential"].copy()

print(f"\nRow count AFTER  Residential filter : {len(listing):,}")
print(f"Rows removed (non-residential)      : {len(listing_raw) - len(listing):,}")

# Save
out_path = os.path.join(OUTPUT_PATH, "listing_residential_combined.csv")
listing.to_csv(out_path, index=False)
print(f"\nSaved → {out_path}")
