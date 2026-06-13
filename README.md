# CivicFlow

Data pipeline that ingests NYC 311 service request data from the NYC Open Data API, transforms it through a medallion architecture, and serves analysis-ready data to a Power BI dashboard.

The Jupyter notebook was just part of exploratory data analysis to understand how the data was structured. I kept it here as part of a portfolio.

> !AI Usage: I used Claude Code to check my written code, assist with writing README, handle menial tasks like writing 40+ 'row.get()' for each row, and just as a springboard for ideas and nudging me through problems/tutoring. 

## Overview

CivicFlow runs on a 24-hour schedule, pulling new and updated 311 complaints from the NYC Open Data API and moving them through three layers of a PostgreSQL data warehouse:

- **Bronze** - raw data, all columns stored as VARCHAR to absorb API changes without breaking ingestion
- **Silver** - typed and cleaned data, dates cast to TIMESTAMP and coordinates to NUMERIC
- **Gold** - analysis-ready data with complaint and resolution categories mapped from the verbose raw values

## Architecture

```
NYC Open Data API
      │
      ▼
  [ Extract ]  ── paginated API calls, incremental by loaded_at
      │
      ▼
  [ Bronze ]   ── raw VARCHAR storage, upsert on unique_key
      │
      ▼
  [ Silver ]   ── type casting, data validation
      │
      ▼
  [ Gold ]     ── feature engineering, derived data like complaint_category &       resolution_category
      │
      ▼
  Power BI Dashboard
```

## Tech Stack

- **Python** - pipeline orchestration
- **PostgreSQL** - medallion data warehouse (bronze / silver / gold schemas)
- **psycopg2** - database driver
- **schedule** - 24-hour run cadence
- **NYC Open Data API** - 311 service request data
- **Power BI** - dashboard and geospatial visualisation

## Key Features

- Incremental ingestion — only fetches records created or updated since the last load
- Paginated API extraction using a generator to avoid loading large datasets into memory
- Upsert logic so updated complaints (status changes, resolutions) are reflected without duplicates
- Load tracking across all three layers via `load_log` tables, allowing each layer to pick up only unprocessed data on each run
- Complaint type mapped to 14 broad categories (Noise, Infrastructure, Sanitation, etc.)
- Resolution description mapped to 10 outcome categories (Resolved, Violation Issued, No Access, etc.) using pattern matching

## Setup

1. Clone the repo
2. Create a `.env` file with your PostgreSQL credentials:
```
db_name=
user=
password=
host=
port=
```
3. Create the bronze, silver, and gold schemas in PostgreSQL:
```sql
CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold;
```
4. Install dependencies:
```
pip install -r requirements.txt
```
5. Run the pipeline:
```
python main.py
```
