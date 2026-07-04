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
print("\n Week 1 data loaded and filtered successfully.")

---------------------

WEEK 2 – Dataset Structuring and Validation (Listing)
# Goal: Inspect structure, run missing value analysis, answer EDA questions
#       specific to the listings dataset (supply analysis), and save reports.

print("\n" + "=" * 65)
print("WEEK 2 – Dataset Structuring and Validation  (listing_analysis.py)")
print("=" * 65)

# Basic Structure
print("\n Basic Structure")
print(f"Shape : {listing.shape[0]:,} rows  x  {listing.shape[1]} columns")

print("\nColumn names and data types:")
print(listing.dtypes.to_string())

# Missing Value Analysis
print("\n Missing Value Analysis")

total_rows = len(listing)
miss_count = listing.isnull().sum()
miss_pct   = (miss_count / total_rows * 100).round(2)

missing_report = pd.DataFrame({
    "missing_count" : miss_count,
    "missing_pct"   : miss_pct
})
missing_report = missing_report[missing_report["missing_count"] > 0] \
                    .sort_values("missing_pct", ascending=False)

print(f"\nColumns with at least 1 null value: {len(missing_report)}")
print(missing_report.to_string())

flagged_90 = missing_report[missing_report["missing_pct"] > 90]
print(f"\nColumns >90% null (recommend dropping): {len(flagged_90)}")
if len(flagged_90) > 0:
    print(flagged_90.to_string())
else:
    print("  None – all columns are under 90% null.")

# EDA Questions
print("\n EDA Questions")

# MLS Status breakdown (Active, Pending, Closed, Expired, Withdrawn, etc.)
if "MlsStatus" in listing.columns:
    print("\nMlsStatus breakdown:")
    print(listing["MlsStatus"].value_counts().to_string())

# List price distribution
if "ListPrice" in listing.columns:
    lp = listing["ListPrice"].dropna()
    print(f"\nListPrice — Median: ${lp.median():,.0f}  |  Mean: ${lp.mean():,.0f}")

# Days on Market for active listings
if "DaysOnMarket" in listing.columns:
    dom_active = listing.loc[
        listing.get("MlsStatus", pd.Series([""] * len(listing))) == "Active",
        "DaysOnMarket"
    ].dropna() if "MlsStatus" in listing.columns else listing["DaysOnMarket"].dropna()

    if len(dom_active) > 0:
        print(f"\nDaysOnMarket (Active listings) — "
              f"Median: {dom_active.median():.0f}  |  Mean: {dom_active.mean():.1f}")

# Property subtype breakdown
if "PropertySubType" in listing.columns:
    print(f"\nPropertySubType breakdown:")
    print(listing["PropertySubType"].value_counts().head(10).to_string())

# New construction share
if "NewConstructionYN" in listing.columns:
    nc = listing["NewConstructionYN"].value_counts(normalize=True) * 100
    print(f"\nNewConstructionYN share (%):")
    print(nc.round(1).to_string())

# County distribution
if "CountyOrParish" in listing.columns and "ListPrice" in listing.columns:
    county_med = (listing.groupby("CountyOrParish")["ListPrice"]
                  .median()
                  .sort_values(ascending=False)
                  .head(10))
    print(f"\nTop 10 counties by median ListPrice:")
    print(county_med.to_string())

# Date Consistency Checks
print("\n Date Consistency Checks")

date_cols = ["ListingContractDate", "PurchaseContractDate",
             "CloseDate", "ContractStatusChangeDate"]
for col in date_cols:
    if col in listing.columns:
        listing[col] = pd.to_datetime(listing[col], errors="coerce")

# Flag: listing contract date after close date
if "ListingContractDate" in listing.columns and "CloseDate" in listing.columns:
    listing["listing_after_close_flag"] = (
        listing["ListingContractDate"] > listing["CloseDate"]
    )
    n = listing["listing_after_close_flag"].sum()
    print(f"listing_after_close_flag  : {n:,} records  "
          f"({n/len(listing)*100:.2f}%)")

# Flag: purchase contract after close date
if "PurchaseContractDate" in listing.columns and "CloseDate" in listing.columns:
    listing["purchase_after_close_flag"] = (
        listing["PurchaseContractDate"] > listing["CloseDate"]
    )
    n = listing["purchase_after_close_flag"].sum()
    print(f"purchase_after_close_flag : {n:,} records  "
          f"({n/len(listing)*100:.2f}%)")

# Flag: listing date after purchase contract date
if "ListingContractDate" in listing.columns and "PurchaseContractDate" in listing.columns:
    listing["negative_timeline_flag"] = (
        listing["ListingContractDate"] > listing["PurchaseContractDate"]
    )
    n = listing["negative_timeline_flag"].sum()
    print(f"negative_timeline_flag    : {n:,} records  "
          f"({n/len(listing)*100:.2f}%)")

# Save validated dataset 
print("\n Week 2 complete")
