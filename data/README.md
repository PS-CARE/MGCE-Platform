# MGCE Platform - Data Templates

## File Descriptions

### 1. `load_profiles.csv`
Time-series electrical demand data.

| Column | Required | Format | Notes |
|--------|----------|--------|-------|
| Timestamp | Yes | YYYY-MM-DD HH:MM | 15-min or hourly intervals |
| Load_kW | Yes | Numeric | Active power demand |
| Power_Factor | No | 0.0-1.0 | Default: 0.9 |
| Load_Type | Yes | Text | Critical/Essential/Non-Essential |

**Ideal**: 1 year of 15-minute data (35,040 rows)  
**Minimum**: Typical day profiles for each season (96 rows × 4 seasons)

---

### 2. `component_costs.csv`
Equipment pricing database.

| Column | Required | Notes |
|--------|----------|-------|
| Component | Yes | Equipment name |
| Category | Yes | Generation/Storage/BOS |
| Unit_Cost | Yes | Cost per unit |
| Unit | Yes | $/W, $/kWh, $/kW, $/unit, $/ft |
| Installation_Cost_Per_Unit | Yes | Labor + materials |
| Lifespan_Years | Yes | Expected lifetime |
| Efficiency_Percent | No | Operating efficiency |
| Notes | No | Additional details |

---

### 3. `utility_rates.csv`
Electricity tariff structure.

| Column | Required | Notes |
|--------|----------|-------|
| Rate_Type | Yes | Energy/Demand/Fixed |
| Season | Yes | Summer/Winter/All |
| Period | Yes | Peak/Off-Peak/All |
| Start_Hour | Yes | 0-23 |
| End_Hour | Yes | 1-24 |
| Cost | Yes | Rate value |
| Unit | Yes | $/kWh, $/kW, $/month |
| Days_Applicable | Yes | Weekdays/Weekends/All |

---

### 4. `financial_parameters.csv`
Economic assumptions for analysis.

| Column | Required | Notes |
|--------|----------|-------|
| Parameter | Yes | Parameter name |
| Value | Yes | Numeric value |
| Unit | Yes | %, years, $/unit |
| Description | No | Explanation |

**Key parameters**: ITC rate, discount rate, project lifetime, O&M costs, fuel costs

---

### 5. `site_info.csv`
Project location and infrastructure details.

| Column | Required | Notes |
|--------|----------|-------|
| Parameter | Yes | Parameter name |
| Value | Yes | Value |
| Unit | Yes | Unit of measure |
| Description | No | Explanation |

**Critical**: Latitude/Longitude (for solar resource), available space, service voltage

---

### 6. `reliability_requirements.csv`
Backup power requirements by load type.

| Column | Required | Notes |
|--------|----------|-------|
| Load_Type | Yes | Must match load_profiles.csv |
| Priority | Yes | 1 = highest priority |
| Backup_Hours | Yes | Hours of backup required |
| Coverage_Percent | Yes | % of load to cover |
| Islanding_Required | Yes | Yes/No |
| Description | No | Load description |

---

## Instructions

1. Open each CSV in Excel
2. Replace example data with your project data
3. Save as .xlsx or keep as .csv
4. Ensure column headers remain unchanged

## Notes

- All files use CSV format (comma-separated)
- Can be opened/edited in Excel and saved as .xlsx
- Example data provided for reference - replace with actual values
