# IDX Exchange - MLS Data Analyst Internship

A 12-week data analytics pipeline focused on transforming raw real estate MLS transaction data into interactive market intelligence dashboards and reports.

* **Primary Tools:** Python (Pandas), Tableau Desktop Public Edition, FileZilla (FTP)
* **Data Source:** CoreLogic Trestle API via IDX Exchange pipeline

---

## Environment Setup
* **IDE:** Spyder & Jupyter Notebook
* **Tableau:** Tableau Desktop Public Edition
* **Data Retrieval:** FileZilla Client connected to the IDX Exchange FTP server

---

## Week 1: Monthly Dataset Aggregation
Loaded all monthly CSVs with `glob`, concatenated them, filtered to `PropertyType == 'Residential'`, and saved combined CSVs.

| | Sold | Listing |
|---|---|---|
| Files found | 31 | 27 |
| Rows before filter | 681,599 | 866,140 |
| Rows after filter | 458,336 | 550,542 |

---

## Week 2: Dataset Structuring and Validation
Inspected structure, flagged high-null columns, answered EDA questions, and added date consistency flags.

**Columns >90% null (flagged for dropping):** 15 in Sold, 13 in Listing — includes `TaxAnnualAmount`, `TaxYear`, `ElementarySchoolDistrict`, `FireplacesTotal`, `AboveGradeFinishedArea`, `CoveredSpaces`, and others that are fully empty across all files.

**EDA answers (Sold):**
- Median ClosePrice: $820,000 | Mean: $1,186,149
- DOM: Median 18 days | 20.9% sold in under 7 days | 19.1% took 60+ days
- 40.7% sold above list price, 42.0% below, 17.3% at asking
- Date flags all under 0.05% of rows — within acceptable range

**EDA answers (Listing):**
- Median ListPrice: $849,000
- MlsStatus: Active 286,430 | Closed 127,140 | Pending 90,913 | ActiveUnderContract 44,248
- Active listing median DOM: 10 days — healthy demand signal
- Top counties by median list price: San Mateo ($1.65M), Santa Clara ($1.5M), Marin ($1.3M)

---

## Week 3: Numeric Distributions + Mortgage Rate Enrichment
Generated percentile tables and histogram/boxplot charts for key numeric fields. Fetched 30-year fixed mortgage rate from FRED (MORTGAGE30US), resampled weekly → monthly, and merged onto both datasets by year-month.

**Notable distribution findings:**
- ClosePrice max: $989M | LivingArea max: 17M sq ft | DOM max: 12,430 days — all clear data errors, preserved for now and will be removed in Week 7 IQR filtering
- BathroomsTotalInteger max: 175 (Sold), 2,208 (Listing) — implausible outliers flagged
- Recent mortgage rates: 6.05% (Feb 2026) → 6.46% (Jul 2026)

**Merge result:**
- Listing: 0 null rates after merge ✅
- Sold: 108,157 null rates (23.6%) — records with missing CloseDates could not be matched to a month; under investigation

---

## Weeks 4–5: Data Cleaning and Preparation
Converted dates to datetime, enforced numeric types, flagged invalid values, and ran coordinate checks. Saved two versions: `*_flagged.csv` (all rows + all flag columns) and `*_clean.csv` (core invalid records removed).

**Sold:** 458,336 → 457,796 rows (540 removed, 0.12%) | Median ClosePrice unchanged at $820,000
**Listing:** flagged file saved; clean file removes records with invalid ListPrice, LivingArea ≤ 0, negative DOM, or bad coordinates

**Key flags added:**

| Flag | Sold | Listing |
|---|---|---|
| Invalid price (≤0 or null) | 3 | 0 |
| Invalid living area (≤0 or null) | 414 | 926 |
| Negative DOM | 63 | 20 |
| Missing coordinates | 16,027 (3.5%) | 76,280 (13.9%) |
| Positive longitude (wrong for CA) | 33 | 76 |


---
## Week 6 – Feature Engineering and Market Metrics
Created calculated columns that don't exist in the raw data but are needed for the dashboards.

**Metrics added (Sold):**
| Column | Formula | What it tells you |
|---|---|---|
| `price_ratio` | `ClosePrice / OriginalListPrice` | >1.0 = sold over asking, <1.0 = came down |
| `price_per_sqft` | `ClosePrice / LivingArea` | Normalizes price so a 900 sq ft condo and 2,500 sq ft house are comparable |
| `listing_to_contract_days` | `PurchaseContractDate - ListingContractDate` | How long until an offer was accepted |
| `contract_to_close_days` | `CloseDate - PurchaseContractDate` | Escrow duration |
| `close_year` / `close_month` / `close_yrmo` | Derived from `CloseDate` | Time series grouping keys for Tableau trend lines |

**Listing:** Added `list_year`, `list_month`, `list_yrmo` from `ListingContractDate` for supply trend analysis.

**School district join:** Matched each property's lat/lon against the California Department of Education 2025-26 school district boundary map using a spatial join (`geopandas`). Added `school_district` and `school_district_type` columns. Records missing coordinates (13.9% of Listing, 3.5% of Sold) do not receive a district assignment.

**Segment summaries saved:** `sold_segment_by_subtype.csv`, `sold_segment_by_county.csv` — median close price, median PPSF, median DOM, and median price ratio grouped by property subtype and county.

**Output files:** `sold_features.csv`, `listing_features.csv`

---

## Week 7 – Outlier Detection and Removal (IQR Method)
Applied the **Interquartile Range (IQR)** method to flag statistical outliers on four key fields before loading into Tableau.

**How IQR works:** Q1 is the 25th percentile, Q3 is the 75th. The IQR is the distance between them — the middle 50% of the data. Any value more than 1.5× the IQR above Q3 or below Q1 is flagged as an outlier. The bounds are calculated from the data itself, so they adjust automatically as new months are added.

**IQR bounds applied (Sold):**
| Field | Lower Bound | Upper Bound | Records Flagged |
|---|---|---|---|
| `ClosePrice` | ~-$557K (effectively $0) | ~$2.48M | ~7.7% |
| `LivingArea` | ~0 sq ft | ~3,747 sq ft | ~4.1% |
| `DaysOnMarket` | 0 days | ~100 days | ~10.5% |
| `price_per_sqft` | ~$0 | ~$1,285/sq ft | ~4.4% |

Records flagged on **any** of these fields are excluded from the Tableau-ready file. The full flagged file is also saved so nothing is permanently lost.

**Results:**
- Sold: `sold_features.csv` → `sold_tableau_ready.csv`
- Listing: `listing_features.csv` → `listing_tableau_ready.csv`
- Median ClosePrice is essentially unchanged after filtering — confirms only true extremes were removed, not real market transactions.

**Output files:** `sold_w7_flagged.csv`, `sold_tableau_ready.csv`, `listing_w7_flagged.csv`, `listing_tableau_ready.csv`
## Week 8 Tableau Export: Build Combined Dataset
Combined `sold_tableau_ready.csv` and `listing_tableau_ready.csv` into a single file (`combined_tableau_ready.csv`) so Tableau only needs one data source.

Two columns added:
- `source`: ”`'Sold'` or `'Listing'` on every row, used as a sheet-level filter in Tableau
- `date` : "`CloseDate` for Sold rows, `ListingContractDate` for Listing rows â€” one consistent time axis
- `yrmo` : ” year-month string (e.g. `2024-06`) derived from `date`, used on the columns shelf for all trend charts

Columns that only exist in Sold (`PoolPrivateYN`, `ViewYN`, `Flooring`, etc.) are null for Listing rows â€” expected behavior since those fields were never in the Listing export.

**Output:** `combined_tableau_ready.csv` â€” this is the only file loaded into Tableau for all dashboards.

**In Tableau:** filter any sheet to `source = Sold` or `source = Listing` as needed. Use `yrmo` on the time axis. One filter pill set to "Apply to All Worksheets" controls every chart on a dashboard simultaneously.

---
## Up Next
- **Weeks 9–10** – Tableau dashboard development
- **Weeks 11–12** – Market intelligence report and final presentation
