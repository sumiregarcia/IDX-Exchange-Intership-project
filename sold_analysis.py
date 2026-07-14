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

if "ListingContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["listing_after_close_flag"] = sold["ListingContractDate"] > sold["CloseDate"]
    n = sold["listing_after_close_flag"].sum()
    print(f"listing_after_close_flag  : {n:,} records  ({n/len(sold)*100:.2f}%)")

if "PurchaseContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["purchase_after_close_flag"] = sold["PurchaseContractDate"] > sold["CloseDate"]
    n = sold["purchase_after_close_flag"].sum()
    print(f"purchase_after_close_flag : {n:,} records  ({n/len(sold)*100:.2f}%)")

if "ListingContractDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["negative_timeline_flag"] = sold["ListingContractDate"] > sold["PurchaseContractDate"]
    n = sold["negative_timeline_flag"].sum()
    print(f"negative_timeline_flag    : {n:,} records  ({n/len(sold)*100:.2f}%)")

out_path = os.path.join(OUTPUT_PATH, "sold_validated.csv")
sold.to_csv(out_path, index=False)
print(f"\nSaved (with date flags) → {out_path}")
print("\n Week 2 complete. Check console output, sold_missing_report.csv, sold_validated.csv")

----
print("\n" + "=" * 65)
print("WEEK 3 – Numeric Distributions + Mortgage Rate Enrichment  (sold_analysis.py)")
print("=" * 65)

print("\n Numeric Distribution Summary")
numeric_fields = [
    "ClosePrice", "ListPrice", "OriginalListPrice",
    "LivingArea", "LotSizeAcres", "BedroomsTotal",
    "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt"
]
numeric_fields = [c for c in numeric_fields if c in sold.columns]
dist_stats = sold[numeric_fields].describe(
    percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
)
print(dist_stats.to_string())
dist_stats.to_csv(os.path.join(OUTPUT_PATH, "sold_numeric_distribution.csv"))
print("\nSaved -> output/sold_numeric_distribution.csv")

print("\n Generating distribution charts")
chart_fields = [
    ("ClosePrice",   0.99, "$"),
    ("LivingArea",   0.99, "sq ft"),
    ("DaysOnMarket", 0.95, "days"),
]
chart_fields = [(f, p, u) for f, p, u in chart_fields if f in sold.columns]

fig, axes = plt.subplots(1, len(chart_fields), figsize=(6 * len(chart_fields), 5))
if len(chart_fields) == 1:
    axes = [axes]
fig.suptitle("Sold Dataset – Key Field Distributions (Residential)", fontsize=13)
for ax, (field, cap_pct, unit) in zip(axes, chart_fields):
    series = sold[field].dropna()
    cap    = series.quantile(cap_pct)
    series = series[series <= cap]
    ax.hist(series, bins=60, color="#1f6aa5", edgecolor="white", linewidth=0.3)
    ax.set_title(field)
    ax.set_xlabel(f"{unit}  (capped at {int(cap_pct*100)}th percentile)")
    ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "sold_histograms.png"), dpi=150)
plt.close()
print("Saved -> output/sold_histograms.png")

fig, axes = plt.subplots(1, len(chart_fields), figsize=(6 * len(chart_fields), 5))
if len(chart_fields) == 1:
    axes = [axes]
fig.suptitle("Sold Dataset – Boxplots (outliers visible)", fontsize=13)
for ax, (field, cap_pct, unit) in zip(axes, chart_fields):
    series = sold[field].dropna()
    ax.boxplot(series, vert=True, patch_artist=True,
               boxprops=dict(facecolor="#1f6aa5", color="#1f6aa5"),
               medianprops=dict(color="white", linewidth=2))
    ax.set_title(field)
    ax.set_ylabel(unit)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "sold_boxplots.png"), dpi=150)
plt.close()
print("Saved -> output/sold_boxplots.png")

print("\n Mortgage Rate Enrichment from FRED")
try:
    fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
    mortgage = pd.read_csv(fred_url, parse_dates=["observation_date"])
    mortgage.columns = ["date", "rate_30yr_fixed"]
    print(f"Fetched {len(mortgage)} weekly observations from FRED")
    mortgage["year_month"] = mortgage["date"].dt.to_period("M")
    mortgage_monthly = (mortgage.groupby("year_month")["rate_30yr_fixed"]
                        .mean().reset_index())
    print(f"Resampled to {len(mortgage_monthly)} monthly averages")
    print("\nMost recent 6 months of mortgage rates:")
    print(mortgage_monthly.tail(6).to_string(index=False))

    sold["year_month"] = pd.to_datetime(
        sold["CloseDate"], errors="coerce").dt.to_period("M")
    sold = sold.merge(mortgage_monthly, on="year_month", how="left")

    null_rate = sold["rate_30yr_fixed"].isnull().sum()
    print(f"\nNull rate_30yr_fixed after merge: {null_rate:,}")
    if null_rate > 0:
        print("  NOTE: Records with nulls have missing or out-of-range CloseDates.")

    preview_cols = [c for c in ["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]
                    if c in sold.columns]
    print("\nPreview (first 5 rows after merge):")
    print(sold[preview_cols].head(5).to_string(index=False))

    sold.to_csv(os.path.join(OUTPUT_PATH, "sold_enriched.csv"), index=False)
    print("\nSaved -> output/sold_enriched.csv")

except Exception as e:
    print(f"\nWARNING: Could not fetch FRED data – {e}")
    sold.to_csv(os.path.join(OUTPUT_PATH, "sold_enriched.csv"), index=False)

-----
#week 4 and 5 
print("\n" + "=" * 65)
print("WEEKS 4–5 - Data Cleaning and Preparation  (sold_analysis.py)")
print("=" * 65)

# Load from the Week 3 enriched output so cleaning builds on prior work
sold = pd.read_csv(os.path.join(OUTPUT_PATH, "sold_enriched.csv"), low_memory=False)
rows_start = len(sold)
print(f"\nLoaded sold_enriched.csv -> {rows_start:,} rows  x  {sold.shape[1]} columns")

# Convert date columns to datetime
print("\n Date Field Conversion")
date_cols = ["CloseDate", "PurchaseContractDate",
             "ListingContractDate", "ContractStatusChangeDate"]

for col in date_cols:
    if col in sold.columns:
        before_nulls = sold[col].isnull().sum()
        sold[col]    = pd.to_datetime(sold[col], errors="coerce")
        after_nulls  = sold[col].isnull().sum()
        new_nulls    = after_nulls - before_nulls
        print(f"  {col}: converted to datetime  "
              f"(new unparseable nulls introduced: {new_nulls})")

# Enforce numeric types
print("\n Numeric Type Enforcement")
numeric_cols = [
    "ClosePrice", "ListPrice", "OriginalListPrice",
    "LivingArea", "LotSizeAcres", "BedroomsTotal",
    "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt",
    "Latitude", "Longitude"
]
for col in numeric_cols:
    if col in sold.columns:
        sold[col] = pd.to_numeric(sold[col], errors="coerce")
        print(f"  {col}: enforced as numeric")

# Flag and remove invalid numeric values
print("\n Invalid Numeric Value Flags")

# ClosePrice <= 0  (always invalid – a home cannot sell for zero or negative)
sold["flag_invalid_close_price"] = sold["ClosePrice"].le(0) | sold["ClosePrice"].isnull()
n = sold["flag_invalid_close_price"].sum()
print(f"  flag_invalid_close_price  (ClosePrice <= 0 or null) : {n:,} records")

# LivingArea <= 0  (a property must have interior square footage)
sold["flag_invalid_living_area"] = sold["LivingArea"].le(0) | sold["LivingArea"].isnull()
n = sold["flag_invalid_living_area"].sum()
print(f"  flag_invalid_living_area  (LivingArea <= 0 or null) : {n:,} records")

# DaysOnMarket < 0  (negative DOM is a data entry error)
if "DaysOnMarket" in sold.columns:
    sold["flag_negative_dom"] = sold["DaysOnMarket"] < 0
    n = sold["flag_negative_dom"].sum()
    print(f"  flag_negative_dom         (DaysOnMarket < 0)        : {n:,} records")

# BedroomsTotal <= 0  (a residential listing must have at least 1 bedroom)
if "BedroomsTotal" in sold.columns:
    sold["flag_invalid_bedrooms"] = sold["BedroomsTotal"].le(0) | sold["BedroomsTotal"].isnull()
    n = sold["flag_invalid_bedrooms"].sum()
    print(f"  flag_invalid_bedrooms     (BedroomsTotal <= 0 or null): {n:,} records")

# BathroomsTotalInteger <= 0
if "BathroomsTotalInteger" in sold.columns:
    sold["flag_invalid_bathrooms"] = (
        sold["BathroomsTotalInteger"].le(0) | sold["BathroomsTotalInteger"].isnull()
    )
    n = sold["flag_invalid_bathrooms"].sum()
    print(f"  flag_invalid_bathrooms    (Bathrooms <= 0 or null)   : {n:,} records")

# YearBuilt sanity check  (before 1800 or after current year is implausible)
if "YearBuilt" in sold.columns:
    sold["flag_invalid_year_built"] = (
        sold["YearBuilt"].lt(1800) | sold["YearBuilt"].gt(2026)
    )
    n = sold["flag_invalid_year_built"].sum()
    print(f"  flag_invalid_year_built   (YearBuilt < 1800 or > 2026): {n:,} records")

# Date consistency re-flags (now on proper datetime columns)
print("\n Date Consistency Flags")

if "ListingContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["listing_after_close_flag"] = sold["ListingContractDate"] > sold["CloseDate"]
    n = sold["listing_after_close_flag"].sum()
    print(f"  listing_after_close_flag  : {n:,} records  ({n/len(sold)*100:.2f}%)")

if "PurchaseContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["purchase_after_close_flag"] = sold["PurchaseContractDate"] > sold["CloseDate"]
    n = sold["purchase_after_close_flag"].sum()
    print(f"  purchase_after_close_flag : {n:,} records  ({n/len(sold)*100:.2f}%)")

if "ListingContractDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["negative_timeline_flag"] = sold["ListingContractDate"] > sold["PurchaseContractDate"]
    n = sold["negative_timeline_flag"].sum()
    print(f"  negative_timeline_flag    : {n:,} records  ({n/len(sold)*100:.2f}%)")

#Geographic Data Quality Checks

print("\n Geographic Data Quality")

# California Latitude range: roughly 32.5° to 42.0° N
# California Longitude range: roughly -124.5° to -114.1° (all NEGATIVE)

if "Latitude" in sold.columns:
    sold["flag_missing_lat"] = sold["Latitude"].isnull()
    sold["flag_zero_lat"]    = sold["Latitude"] == 0
    sold["flag_out_of_range_lat"] = (
        sold["Latitude"].notna() &
        ((sold["Latitude"] < 32.5) | (sold["Latitude"] > 42.0))
    )
    print(f"  flag_missing_lat          : {sold['flag_missing_lat'].sum():,} records")
    print(f"  flag_zero_lat             : {sold['flag_zero_lat'].sum():,} records")
    print(f"  flag_out_of_range_lat     : {sold['flag_out_of_range_lat'].sum():,} records")

if "Longitude" in sold.columns:
    sold["flag_missing_lon"] = sold["Longitude"].isnull()
    sold["flag_zero_lon"]    = sold["Longitude"] == 0
    # Longitude > 0 means it's in the Eastern Hemisphere — wrong for California
    sold["flag_positive_lon"] = sold["Longitude"].notna() & (sold["Longitude"] > 0)
    sold["flag_out_of_range_lon"] = (
        sold["Longitude"].notna() &
        (sold["Longitude"] < -124.5) | sold["Longitude"].notna() &
        (sold["Longitude"] > -114.1)
    )
    print(f"  flag_missing_lon          : {sold['flag_missing_lon'].sum():,} records")
    print(f"  flag_zero_lon             : {sold['flag_zero_lon'].sum():,} records")
    print(f"  flag_positive_lon         : {sold['flag_positive_lon'].sum():,} records  "
          f"← Longitude should always be negative for CA")
    print(f"  flag_out_of_range_lon     : {sold['flag_out_of_range_lon'].sum():,} records")

# Summary: total records with any coordinate issue
coord_flag_cols = [c for c in sold.columns if c.startswith("flag_") and
                   ("lat" in c or "lon" in c)]
if coord_flag_cols:
    any_coord_issue = sold[coord_flag_cols].any(axis=1).sum()
    print(f"\n  Records with ANY coordinate flag : {any_coord_issue:,}  "
          f"({any_coord_issue/len(sold)*100:.2f}%)")

# -----------------------------------
# Build the clean analysis-ready dataset
#      Strategy: flag don't delete. Save two versions:
#        (1) sold_flagged.csv  – full dataset with all flag columns
#        (2) sold_clean.csv    – records passing all core validity checks

print("\n Build Clean Dataset")

# Core validity filter – remove records that are fundamentally unusable:
# invalid price, invalid area, positive/zero longitude (can't map), negative DOM
core_invalid_flags = [
    "flag_invalid_close_price",
    "flag_invalid_living_area",
]
# Add optional flags only if the columns were created above
if "flag_negative_dom"   in sold.columns: core_invalid_flags.append("flag_negative_dom")
if "flag_positive_lon"   in sold.columns: core_invalid_flags.append("flag_positive_lon")
if "flag_zero_lon"       in sold.columns: core_invalid_flags.append("flag_zero_lon")
if "flag_zero_lat"       in sold.columns: core_invalid_flags.append("flag_zero_lat")

# Save full flagged dataset first
flagged_path = os.path.join(OUTPUT_PATH, "sold_flagged.csv")
sold.to_csv(flagged_path, index=False)
print(f"\nFull flagged dataset saved → output/sold_flagged.csv  ({len(sold):,} rows)")

# Build clean version: keep rows where NONE of the core flags are True
clean_mask = ~sold[core_invalid_flags].any(axis=1)
sold_clean = sold[clean_mask].copy()
rows_removed = len(sold) - len(sold_clean)

print(f"\nRows in flagged dataset : {len(sold):,}")
print(f"Rows removed by filter  : {rows_removed:,}  ({rows_removed/len(sold)*100:.2f}%)")
print(f"Rows in clean dataset   : {len(sold_clean):,}")

# Median ClosePrice before vs. after cleaning (sanity check)
if "ClosePrice" in sold.columns and "ClosePrice" in sold_clean.columns:
    print(f"\nMedian ClosePrice – before cleaning : ${sold['ClosePrice'].median():,.0f}")
    print(f"Median ClosePrice – after  cleaning : ${sold_clean['ClosePrice'].median():,.0f}")

clean_path = os.path.join(OUTPUT_PATH, "sold_clean.csv")
sold_clean.to_csv(clean_path, index=False)
print(f"\nClean dataset saved -> output/sold_clean.csv  ({len(sold_clean):,} rows)")

# leaning Summary Report
print("\n Cleaning Summary")
all_flag_cols = [c for c in sold.columns if c.startswith("flag_")]
print(f"\n{'Flag Column':<35} {'Count':>8}  {'% of Total':>10}")
print("-" * 58)
for col in all_flag_cols:
    n   = sold[col].sum()
    pct = n / len(sold) * 100
    print(f"  {col:<33} {n:>8,}  {pct:>9.2f}%")

print(f"\nTotal rows start  : {rows_start:,}")
print(f"Total rows clean  : {len(sold_clean):,}")
print(f"Total rows removed: {rows_start - len(sold_clean):,}")

print("\n Weeks 4–5 complete. Check sold_flagged.csv and sold_clean.csv in output/")



