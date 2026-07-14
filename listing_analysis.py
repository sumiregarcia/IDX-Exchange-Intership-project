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

 WEEK 3 – Numeric Distribution Review + Mortgage Rate Enrichment (Listing)
# Goal: Distribution stats and charts for key listing numeric fields, then
#       fetch 30-yr mortgage rates from FRED and merge by year-month.
print("\n" + "=" * 65)
print("WEEK 3 – Numeric Distributions + Mortgage Rate Enrichment  (listing_analysis.py)")
print("=" * 65)

print("\n Numeric Distribution Summary")
# ClosePrice intentionally excluded – mostly null in listings (only Closed records have it)
numeric_fields = [
    "ListPrice", "OriginalListPrice",
    "LivingArea", "LotSizeAcres", "BedroomsTotal",
    "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt"
]
numeric_fields = [c for c in numeric_fields if c in listing.columns]
dist_stats = listing[numeric_fields].describe(
    percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
)
print(dist_stats.to_string())
dist_stats.to_csv(os.path.join(OUTPUT_PATH, "listing_numeric_distribution.csv"))
print("\nSaved → output/listing_numeric_distribution.csv")

print("\n Generating distribution charts")
chart_fields = [
    ("ListPrice",   0.99, "$"),
    ("LivingArea",  0.99, "sq ft"),
    ("DaysOnMarket",0.95, "days"),
]
chart_fields = [(f, p, u) for f, p, u in chart_fields if f in listing.columns]

fig, axes = plt.subplots(1, len(chart_fields), figsize=(6 * len(chart_fields), 5))
if len(chart_fields) == 1:
    axes = [axes]
fig.suptitle("Listing Dataset – Key Field Distributions (Residential)", fontsize=13)
for ax, (field, cap_pct, unit) in zip(axes, chart_fields):
    series = listing[field].dropna()
    cap    = series.quantile(cap_pct)
    series = series[series <= cap]
    ax.hist(series, bins=60, color="#e07b39", edgecolor="white", linewidth=0.3)
    ax.set_title(field)
    ax.set_xlabel(f"{unit}  (capped at {int(cap_pct*100)}th percentile)")
    ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "listing_histograms.png"), dpi=150)
plt.close()
print("Saved → output/listing_histograms.png")

fig, axes = plt.subplots(1, len(chart_fields), figsize=(6 * len(chart_fields), 5))
if len(chart_fields) == 1:
    axes = [axes]
fig.suptitle("Listing Dataset – Boxplots (outliers visible)", fontsize=13)
for ax, (field, cap_pct, unit) in zip(axes, chart_fields):
    series = listing[field].dropna()
    ax.boxplot(series, vert=True, patch_artist=True,
               boxprops=dict(facecolor="#e07b39", color="#e07b39"),
               medianprops=dict(color="white", linewidth=2))
    ax.set_title(field)
    ax.set_ylabel(unit)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_PATH, "listing_boxplots.png"), dpi=150)
plt.close()
print("Saved → output/listing_boxplots.png")

print("\n--- 3C: Mortgage Rate Enrichment from FRED ---")
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

    listing["year_month"] = pd.to_datetime(
        listing["ListingContractDate"], errors="coerce").dt.to_period("M")
    listing = listing.merge(mortgage_monthly, on="year_month", how="left")

    null_rate = listing["rate_30yr_fixed"].isnull().sum()
    print(f"\nNull rate_30yr_fixed after merge: {null_rate:,}")
    if null_rate > 0:
        print("  NOTE: Records with nulls likely have missing ListingContractDates.")

    preview_cols = [c for c in
                    ["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]
                    if c in listing.columns]
    print("\nPreview (first 5 rows after merge):")
    print(listing[preview_cols].head(5).to_string(index=False))

    listing.to_csv(os.path.join(OUTPUT_PATH, "listing_enriched.csv"), index=False)
    print("\nSaved → output/listing_enriched.csv")

except Exception as e:
    print(f"\nWARNING: Could not fetch FRED data – {e}")
    listing.to_csv(os.path.join(OUTPUT_PATH, "listing_enriched.csv"), index=False)

print("\n Week 3 complete. Check output/ for charts and listing_enriched.csv")

# ----------
print("\n" + "=" * 65)
print("WEEKS 4–5 – Data Cleaning and Preparation  (listing_analysis.py)")
print("=" * 65)

listing = pd.read_csv(os.path.join(OUTPUT_PATH, "listing_enriched.csv"), low_memory=False)
rows_start = len(listing)
print(f"\nLoaded listing_enriched.csv  →  {rows_start:,} rows  x  {listing.shape[1]} columns")

# Convert date columns to datetime
print("\n Date Field Conversion")
date_cols = ["CloseDate", "PurchaseContractDate",
             "ListingContractDate", "ContractStatusChangeDate"]

for col in date_cols:
    if col in listing.columns:
        before_nulls  = listing[col].isnull().sum()
        listing[col]  = pd.to_datetime(listing[col], errors="coerce")
        after_nulls   = listing[col].isnull().sum()
        new_nulls     = after_nulls - before_nulls
        print(f"  {col}: converted to datetime  "
              f"(new unparseable nulls introduced: {new_nulls})")

# Enforce numeric types
print("\n Numeric Type Enforcement")
numeric_cols = [
    "ListPrice", "OriginalListPrice", "ClosePrice",
    "LivingArea", "LotSizeAcres", "BedroomsTotal",
    "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt",
    "Latitude", "Longitude"
]
for col in numeric_cols:
    if col in listing.columns:
        listing[col] = pd.to_numeric(listing[col], errors="coerce")
        print(f"  {col}: enforced as numeric")

# Flag invalid numeric values
print("\n Invalid Numeric Value Flags")

# ListPrice <= 0  (an active listing must have a positive asking price)
listing["flag_invalid_list_price"] = listing["ListPrice"].le(0) | listing["ListPrice"].isnull()
n = listing["flag_invalid_list_price"].sum()
print(f"  flag_invalid_list_price   (ListPrice <= 0 or null)   : {n:,} records")

# LivingArea <= 0
listing["flag_invalid_living_area"] = listing["LivingArea"].le(0) | listing["LivingArea"].isnull()
n = listing["flag_invalid_living_area"].sum()
print(f"  flag_invalid_living_area  (LivingArea <= 0 or null)  : {n:,} records")

# DaysOnMarket < 0  (DOM cannot be negative)
if "DaysOnMarket" in listing.columns:
    listing["flag_negative_dom"] = listing["DaysOnMarket"] < 0
    n = listing["flag_negative_dom"].sum()
    print(f"  flag_negative_dom         (DaysOnMarket < 0)          : {n:,} records")

# BedroomsTotal <= 0
if "BedroomsTotal" in listing.columns:
    listing["flag_invalid_bedrooms"] = (
        listing["BedroomsTotal"].le(0) | listing["BedroomsTotal"].isnull()
    )
    n = listing["flag_invalid_bedrooms"].sum()
    print(f"  flag_invalid_bedrooms     (BedroomsTotal <= 0 or null) : {n:,} records")

# BathroomsTotalInteger <= 0
if "BathroomsTotalInteger" in listing.columns:
    listing["flag_invalid_bathrooms"] = (
        listing["BathroomsTotalInteger"].le(0) | listing["BathroomsTotalInteger"].isnull()
    )
    n = listing["flag_invalid_bathrooms"].sum()
    print(f"  flag_invalid_bathrooms    (Bathrooms <= 0 or null)     : {n:,} records")

# YearBuilt sanity check
if "YearBuilt" in listing.columns:
    listing["flag_invalid_year_built"] = (
        listing["YearBuilt"].lt(1800) | listing["YearBuilt"].gt(2026)
    )
    n = listing["flag_invalid_year_built"].sum()
    print(f"  flag_invalid_year_built   (YearBuilt < 1800 or > 2026) : {n:,} records")

# Date consistency re-flags (now on proper datetime columns)
print("\n Date Consistency Flags")

if "ListingContractDate" in listing.columns and "CloseDate" in listing.columns:
    listing["listing_after_close_flag"] = listing["ListingContractDate"] > listing["CloseDate"]
    n = listing["listing_after_close_flag"].sum()
    print(f"  listing_after_close_flag  : {n:,} records  ({n/len(listing)*100:.2f}%)")

if "PurchaseContractDate" in listing.columns and "CloseDate" in listing.columns:
    listing["purchase_after_close_flag"] = listing["PurchaseContractDate"] > listing["CloseDate"]
    n = listing["purchase_after_close_flag"].sum()
    print(f"  purchase_after_close_flag : {n:,} records  ({n/len(listing)*100:.2f}%)")

if "ListingContractDate" in listing.columns and "PurchaseContractDate" in listing.columns:
    listing["negative_timeline_flag"] = listing["ListingContractDate"] > listing["PurchaseContractDate"]
    n = listing["negative_timeline_flag"].sum()
    print(f"  negative_timeline_flag    : {n:,} records  ({n/len(listing)*100:.2f}%)")

# Geographic Data Quality Checks
print("\n Geographic Data Quality")

if "Latitude" in listing.columns:
    listing["flag_missing_lat"] = listing["Latitude"].isnull()
    listing["flag_zero_lat"]    = listing["Latitude"] == 0
    listing["flag_out_of_range_lat"] = (
        listing["Latitude"].notna() &
        ((listing["Latitude"] < 32.5) | (listing["Latitude"] > 42.0))
    )
    print(f"  flag_missing_lat          : {listing['flag_missing_lat'].sum():,} records")
    print(f"  flag_zero_lat             : {listing['flag_zero_lat'].sum():,} records")
    print(f"  flag_out_of_range_lat     : {listing['flag_out_of_range_lat'].sum():,} records")

if "Longitude" in listing.columns:
    listing["flag_missing_lon"] = listing["Longitude"].isnull()
    listing["flag_zero_lon"]    = listing["Longitude"] == 0
    listing["flag_positive_lon"] = listing["Longitude"].notna() & (listing["Longitude"] > 0)
    listing["flag_out_of_range_lon"] = (
        listing["Longitude"].notna() &
        (listing["Longitude"] < -124.5) | listing["Longitude"].notna() &
        (listing["Longitude"] > -114.1)
    )
    print(f"  flag_missing_lon          : {listing['flag_missing_lon'].sum():,} records")
    print(f"  flag_zero_lon             : {listing['flag_zero_lon'].sum():,} records")
    print(f"  flag_positive_lon         : {listing['flag_positive_lon'].sum():,} records  "
          f"← Longitude should always be negative for CA")
    print(f"  flag_out_of_range_lon     : {listing['flag_out_of_range_lon'].sum():,} records")

coord_flag_cols = [c for c in listing.columns if c.startswith("flag_") and
                   ("lat" in c or "lon" in c)]
if coord_flag_cols:
    any_coord_issue = listing[coord_flag_cols].any(axis=1).sum()
    print(f"\n  Records with ANY coordinate flag : {any_coord_issue:,}  "
          f"({any_coord_issue/len(listing)*100:.2f}%)")

# Build the clean analysis-ready dataset
print("\n Build Clean Dataset")

# For listings the core invalid filter uses ListPrice instead of ClosePrice
# (ClosePrice is legitimately null for Active/Pending/Expired/Withdrawn records)
core_invalid_flags = ["flag_invalid_list_price", "flag_invalid_living_area"]
if "flag_negative_dom"  in listing.columns: core_invalid_flags.append("flag_negative_dom")
if "flag_positive_lon"  in listing.columns: core_invalid_flags.append("flag_positive_lon")
if "flag_zero_lon"      in listing.columns: core_invalid_flags.append("flag_zero_lon")
if "flag_zero_lat"      in listing.columns: core_invalid_flags.append("flag_zero_lat")

# Save full flagged dataset
flagged_path = os.path.join(OUTPUT_PATH, "listing_flagged.csv")
listing.to_csv(flagged_path, index=False)
print(f"\nFull flagged dataset saved → output/listing_flagged.csv  ({len(listing):,} rows)")

# Build clean version
clean_mask    = ~listing[core_invalid_flags].any(axis=1)
listing_clean = listing[clean_mask].copy()
rows_removed  = len(listing) - len(listing_clean)

print(f"\nRows in flagged dataset : {len(listing):,}")
print(f"Rows removed by filter  : {rows_removed:,}  ({rows_removed/len(listing)*100:.2f}%)")
print(f"Rows in clean dataset   : {len(listing_clean):,}")

# Median ListPrice before vs. after (sanity check)
if "ListPrice" in listing.columns and "ListPrice" in listing_clean.columns:
    print(f"\nMedian ListPrice – before cleaning : ${listing['ListPrice'].median():,.0f}")
    print(f"Median ListPrice – after  cleaning : ${listing_clean['ListPrice'].median():,.0f}")

# MlsStatus breakdown in clean dataset
if "MlsStatus" in listing_clean.columns:
    print(f"\nMlsStatus in clean dataset:")
    print(listing_clean["MlsStatus"].value_counts().to_string())

clean_path = os.path.join(OUTPUT_PATH, "listing_clean.csv")
listing_clean.to_csv(clean_path, index=False)
print(f"\nClean dataset saved → output/listing_clean.csv  ({len(listing_clean):,} rows)")

# Cleaning Summary Report

print("\n Cleaning Summary")
all_flag_cols = [c for c in listing.columns if c.startswith("flag_")]
print(f"\n{'Flag Column':<38} {'Count':>8}  {'% of Total':>10}")
print("-" * 61)
for col in all_flag_cols:
    n   = listing[col].sum()
    pct = n / len(listing) * 100
    print(f"  {col:<36} {n:>8,}  {pct:>9.2f}%")

print(f"\nTotal rows start  : {rows_start:,}")
print(f"Total rows clean  : {len(listing_clean):,}")
print(f"Total rows removed: {rows_start - len(listing_clean):,}")


print("\n Weeks 4–5 complete. Check listing_flagged.csv and listing_clean.csv in output/")

print("\n" + "=" * 65)
print("ALL WEEKS COMPLETE  –  listing_analysis.py")
print(f"Output files saved to: {OUTPUT_PATH}")
print("=" * 65)
