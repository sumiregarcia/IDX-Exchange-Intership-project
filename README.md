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

> **Note:** Several Sold months have both a base file and a `_filled` variant (e.g. `CRMLSSold202401.csv` + `CRMLSSold202401_filled.csv`). Both were loaded — duplicates will be removed by `ListingKey` before Week 6.
> Listing coverage starts February 2024 — January 2024 file was not available.

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

> **Note – Listing missing coordinates:** 76,280 records (13.9%) have no lat/lon — likely Active/Pending listings where agents haven't entered coordinates yet. Usable for price/supply analysis; will show gaps in map visualizations in Weeks 8–10.

---

## Up Next
- **Week 6** – Feature engineering: price ratio, price per sq ft, listing-to-contract days, contract-to-close days, YrMo
- **Week 7** – IQR outlier removal, final analysis-ready datasets
- **Weeks 8–10** – Tableau dashboards
- **Weeks 11–12** – Market intelligence report and presentation
