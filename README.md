# Medication Data Integrity Project

## Overview
This project analyzes hospital medication data to identify:
- Missing usage records
- Inventory discrepancies
- Overused medications
- Purchasing inefficiencies

The goal is to improve data accuracy and support better clinical decision making.

---

## Tools Used
- Python (pandas, sqlite3, openpyxl)
- SQL
- Microsoft Excel
- GitHub

---

## Project Structure

data/       → Raw medication data  
python/     → Data validation scripts  
sql/        → SQL queries  
reports/    → Generated Excel reports  
dashboard/  → Summary visuals  

---

## How to Run

1. Activate environment:
```bash
source venv/bin/activate

2. Install dependencies:
pip install pandas openpyxl

3. Run validation
python python/data_checks.py

4. View report
open reports/validation_report.xlsx


