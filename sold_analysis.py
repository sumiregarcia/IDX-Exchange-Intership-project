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
print("\n Week 1 data loaded and filtered successfully.")

--------
# WEEK 2 – Dataset Structuring and Validation (Sold)
# Goal: Inspect structure, run missing value analysis, answer EDA questions,
#       flag date consistency issues, and save a missing value report.

print("\n" + "=" * 65)
print("WEEK 2 – Dataset Structuring and Validation  (sold_analysis.py)")
print("=" * 65)

# Inspect Structure
print("\n Inspect Structure")
print(f"Shape : {sold.shape[0]:,} rows  x  {sold.shape[1]} columns")

print("\nColumn names and data types:")
print(sold.dtypes.to_string())

# Missing Value Analysis
print("\n Missing Value Analysis")

total_rows  = len(sold)
miss_count  = sold.isnull().sum()
miss_pct    = (miss_count / total_rows * 100).round(2)

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

# Median and average close price
if "ClosePrice" in sold.columns:
    cp = sold["ClosePrice"].dropna()
    print(f"Median ClosePrice : ${cp.median():,.0f}")
    print(f"Mean   ClosePrice : ${cp.mean():,.0f}")

# Days on Market distribution
if "DaysOnMarket" in sold.columns:
    dom = sold["DaysOnMarket"].dropna()
    print(f"\nDaysOnMarket - Median: {dom.median():.0f}  |  "
          f"Mean: {dom.mean():.1f}  |  Max: {dom.max():.0f}")
    dom_bins = {
        "1-7 days (very competitive)": ((dom >= 1)  & (dom <= 7)).sum(),
        "8-30 days (healthy)"        : ((dom >= 8)  & (dom <= 30)).sum(),
        "31-60 days (moderate)"      : ((dom >= 31) & (dom <= 60)).sum(),
        "60+ days (slow)"            : (dom > 60).sum(),
    }
    for label, count in dom_bins.items():
        print(f"  {label}: {count:,}  ({count/len(dom)*100:.1f}%)")

# Sold above vs. below list price
if "ClosePrice" in sold.columns and "ListPrice" in sold.columns:
    both   = sold[["ClosePrice","ListPrice"]].dropna()
    above  = (both["ClosePrice"] > both["ListPrice"]).sum()
    below  = (both["ClosePrice"] < both["ListPrice"]).sum()
    at_ask = (both["ClosePrice"] == both["ListPrice"]).sum()
    n      = len(both)
    print(f"\nSold above list price : {above:,}  ({above/n*100:.1f}%)")
    print(f"Sold at   list price  : {at_ask:,}  ({at_ask/n*100:.1f}%)")
    print(f"Sold below list price : {below:,}  ({below/n*100:.1f}%)")

# Counties with highest median prices
if "CountyOrParish" in sold.columns and "ClosePrice" in sold.columns:
    county_med = (sold.groupby("CountyOrParish")["ClosePrice"]
                  .median()
                  .sort_values(ascending=False)
                  .head(10))
    print(f"\nTop 10 counties by median ClosePrice:")
    print(county_med.to_string())

# Date Consistency Checks
print("\n Date Consistency Checks")

date_cols = ["ListingContractDate", "PurchaseContractDate",
             "CloseDate", "ContractStatusChangeDate"]
for col in date_cols:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], errors="coerce")

# Flag: listing date after close date
if "ListingContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["listing_after_close_flag"] = (
        sold["ListingContractDate"] > sold["CloseDate"]
    )
    n = sold["listing_after_close_flag"].sum()
    print(f"listing_after_close_flag  : {n:,} records  "
          f"({n/len(sold)*100:.2f}%)")

# Flag: purchase contract after close date
if "PurchaseContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["purchase_after_close_flag"] = (
        sold["PurchaseContractDate"] > sold["CloseDate"]
    )
    n = sold["purchase_after_close_flag"].sum()
    print(f"purchase_after_close_flag : {n:,} records  "
          f"({n/len(sold)*100:.2f}%)")

# Flag: listing date after purchase contract date
if "ListingContractDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["negative_timeline_flag"] = (
        sold["ListingContractDate"] > sold["PurchaseContractDate"]
    )
    n = sold["negative_timeline_flag"].sum()
    print(f"negative_timeline_flag    : {n:,} records  "
          f"({n/len(sold)*100:.2f}%)")

# Save the dataset with flag columns added
out_path = os.path.join(OUTPUT_PATH, "sold_validated.csv")
sold.to_csv(out_path, index=False)
print("\n Week 2 data validated. Moving directly to Week 3 analysis.")



