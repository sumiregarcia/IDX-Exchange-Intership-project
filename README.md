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

## Progress Tracker

### ⬜ Week 0: MLS Data Pipeline Orientation
- [x] Established FTP connection via FileZilla and pulled required `CRMLSListing` and `CRMLSSold` CSV datasets.
- [x] Reviewed Trestle Property Metadata document for field definitions and data types.

### ⬜ Week 1: Monthly Dataset Aggregation
- [x] Loaded individual monthly data files from January 2024 to the current month.
- [x] Concatenated datasets using Pandas into unified `listings` and `sold` DataFrames.
- [x] Filtered both datasets down exclusively to `PropertyType == 'Residential'`.
- [x] Saved aggregated files as ready-to-use CSVs and documented row counts before/after filtering.

### 🔵 Weeks 2-3: Dataset Structuring, Validation & Mortgage Enrichment (In Progress)
- [ ] Perform Exploratory Data Analysis (EDA) to evaluate rows, columns, and high-missing fields (>90% null).
- [ ] Generate numeric distribution statistics (min, max, mean, median, percentiles) for `Close Price`, `LivingArea`, and `DaysOnMarket`.
- [ ] Connect to the St. Louis Federal Reserve (FRED) API/URL to fetch live 30-year fixed mortgage rates (`MORTGAGE30US`).
- [ ] Resample weekly FRED data into monthly averages.
- [ ] Perform a time-series left join to merge mortgage rates onto the combined datasets via a `year_month` key.
- [ ] Run validation checks ensuring zero null rate values post-merge.

---

## Key Milestone Metrics

### Week 1 Concatenation & Filter Summary
| Dataset | Pre-Filter Row Count | Post-Residential Filter Row Count | Notes |
| :--- | :--- | :--- | :--- |
| **Sold Transactions** | *[x]* | *[x]* | Successfully filtered out commercial/land rentals |
| **Active Listings** | *[x]* | *[x]* | Successfully filtered out commercial/land rentals |

---

## Data Confidentiality Notice
All raw and processed datasets utilized in this repository are sourced from live MLS transaction records. In compliance with program guidelines, all data files are restricted under strict `.gitignore` rules and are not distributed or made public.
