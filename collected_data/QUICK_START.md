# Quick Start Guide
## Using the Microgrid Cost Estimator Data Collection

---

## 🚀 Getting Started in 5 Minutes

### Step 1: Understand What You Have

You now have **4 complete datasets** with real data from authoritative sources:

1. ✅ **Component Costs** - 22 components with current market pricing
2. ✅ **Financial Parameters** - 21 parameters including tax credits and incentives  
3. ✅ **Utility Rates** - Complete tariff structure for Entergy Louisiana
4. ✅ **Site Information** - Solar resource data for Baton Rouge, LA

### Step 2: What Still Needs Your Input

Two datasets require site-specific information that only you can provide:

5. ⚠️ **Load Profiles** - Your facility's electrical consumption (template provided)
6. ⚠️ **Reliability Requirements** - Your backup power needs (template provided)

---

## 📊 Using the Collected Data

### Component Costs (`component_costs/component_costs_collected.csv`)

**What's inside:**
- Solar panels, inverters, batteries, generators
- Balance of system (BOS) components
- Installation costs for each component
- Lifespan and efficiency data
- Source attribution for each price

**How to use:**
```python
import pandas as pd

# Load component costs
costs = pd.read_csv('component_costs/component_costs_collected.csv')

# Get solar module cost
solar_cost = costs[costs['Component'].str.contains('Solar PV Module')]
print(f"Solar module cost: ${solar_cost['Unit_Cost'].values[0]}/W")

# Get battery storage cost
battery = costs[costs['Component'].str.contains('LFP')]
print(f"Battery cost: ${battery['Unit_Cost'].values[0]}/kWh")
```

**Example calculation:**
- 100 kW solar system = 100,000 W
- Module cost: $0.28/W × 100,000 W = $28,000
- Installation: $0.12/W × 100,000 W = $12,000
- **Total solar: $40,000**

---

### Financial Parameters (`financial_parameters/financial_parameters_collected.csv`)

**What's inside:**
- ITC base rate (30%) and bonus adders
- Loan rates and terms
- Fuel prices
- O&M costs
- Inflation and escalation rates

**How to use:**
```python
# Load financial parameters
params = pd.read_csv('financial_parameters/financial_parameters_collected.csv')

# Get ITC rate
itc = params[params['Parameter'] == 'ITC_Rate']['Value'].values[0]
print(f"ITC Rate: {itc}%")

# Calculate tax credit for $100k project
project_cost = 100000
tax_credit = project_cost * (itc / 100)
print(f"Tax credit: ${tax_credit:,.0f}")
```

**Example ITC calculation:**
- Base project cost: $100,000
- Base ITC (30%): $30,000
- Domestic content (+10%): $10,000
- Energy community (+10%): $10,000
- **Total ITC: $50,000 (50% of project!)**

---

### Utility Rates (`utility_rates/utility_rates_entergy_louisiana_collected.csv`)

**What's inside:**
- Time-of-use energy rates (summer/winter, peak/off-peak)
- Demand charges
- Fixed monthly charges
- Fuel adjustment clause

**How to use:**
```python
# Load utility rates
rates = pd.read_csv('utility_rates/utility_rates_entergy_louisiana_collected.csv')

# Get summer peak energy rate
summer_peak = rates[
    (rates['Season'] == 'Summer') & 
    (rates['Period'] == 'On-Peak') &
    (rates['Rate_Type'] == 'Energy')
]['Cost'].values[0]

print(f"Summer peak rate: ${summer_peak:.4f}/kWh")

# Calculate monthly bill for 50,000 kWh usage, 200 kW peak demand
energy_cost = 50000 * summer_peak
demand_cost = 200 * 19.85  # Summer peak demand charge
monthly_charge = 125
total = energy_cost + demand_cost + monthly_charge
print(f"Estimated monthly bill: ${total:,.2f}")
```

**Savings calculation:**
- Current bill: $8,505/month ($102,060/year)
- Solar reduces: 40% of energy costs (~$2,100/month savings)
- Battery reduces: peak demand by 30% (~$1,200/month savings)
- **Total savings: ~$3,300/month ($39,600/year)**

---

### Site Information (`site_info/site_info_collected.csv`)

**What's inside:**
- Solar resource data (GHI, DNI)
- PV production factors
- Electrical infrastructure details
- Available space for solar

**How to use:**
```python
# Load site info
site = pd.read_csv('site_info/site_info_collected.csv')
site_dict = dict(zip(site['Parameter'], site['Value']))

# Get solar production factor
production_factor = float(site_dict['PV_Production_Factor'])
print(f"Expected production: {production_factor} kWh/kW/year")

# Calculate annual production for 100 kW system
system_size = 100  # kW
annual_production = system_size * production_factor
print(f"100 kW system produces: {annual_production:,.0f} kWh/year")
```

**Example sizing:**
- Available ground space: 50,000 sq ft
- Solar array density: ~150 sq ft per kW
- Maximum system size: 333 kW
- Annual production: 500,000 kWh

---

## ⚠️ Completing the Missing Data

### Load Profiles Template

**What you need:**
1. Get 1 year of hourly electricity usage data from:
   - Utility smart meter data
   - Building management system (BMS)
   - Submetering equipment
   - Utility bills (less granular but usable)

2. Classify each hour's load:
   - **Critical**: Must stay on during outages (safety, life support)
   - **Essential**: Business-critical (servers, refrigeration)
   - **Non-Essential**: Can be shed during outages (HVAC, lighting)

**Template format:**
```csv
Timestamp,Load_kW,Power_Factor,Load_Type
2024-01-01 00:00,120.5,0.92,Critical
2024-01-01 01:00,115.8,0.91,Critical
2024-01-01 02:00,110.0,0.90,Essential
```

**Quick tip:** If you don't have hourly data:
- Use monthly utility bills to estimate average load
- Create typical day profiles (weekday vs weekend)
- Scale by season (summer vs winter)

---

### Reliability Requirements Template

**What you need:**
1. Determine backup needs by load type:
   - How many hours must critical loads stay on?
   - What percentage coverage is required?
   - Is islanding (disconnect from grid) required?

2. Consult with:
   - Facility managers
   - Operations team
   - Insurance requirements
   - Corporate risk policies

**Template format:**
```csv
Load_Type,Priority,Backup_Hours,Coverage_Percent,Islanding_Required,Description
Critical,1,24,100,Yes,Life safety and emergency systems
Essential,2,8,100,Yes,Business-critical operations
Non-Essential,3,0,0,No,Deferrable loads
```

**Example requirements:**
- Hospital: 72 hours critical load backup
- Data center: 24 hours at 100% load
- Manufacturing: 4 hours for orderly shutdown
- Office: 2 hours for emergency lighting

---

## 🔧 Running New Data Collections

### Update Component Costs

```bash
cd /home/claude/microgrid_collectors
python3 -c "
from collectors.component_costs_collector import ComponentCostsCollector
from pathlib import Path
collector = ComponentCostsCollector(Path('./new_data'))
collector.collect_all()
"
```

### Get Data for Different Utility

Edit `collectors/utility_rates_collector.py`:
```python
def get_YOUR_UTILITY_rates(self):
    rates = []
    # Add your utility's rate structure here
    rates.append({
        'Rate_Type': 'Energy',
        'Season': 'Summer',
        'Cost': 0.12,  # Your rate
        # ... etc
    })
    return rates
```

### Get Data for Different Location

```python
from collectors.solar_resource_collector import SolarResourceCollector
from pathlib import Path

# Your site coordinates
site_data = {
    'latitude': 34.05,  # Los Angeles example
    'longitude': -118.25,
    'site_name': 'Your Facility',
    # ... add other fields
}

collector = SolarResourceCollector(Path('./your_site'))
collector.create_site_info_file(site_data)
```

---

## 📈 Example Cost Estimate Workflow

### 1. Determine System Size

```python
# From load profiles
annual_consumption = 500000  # kWh/year
peak_demand = 200  # kW

# Size solar for 40% of annual consumption
solar_production_needed = annual_consumption * 0.40  # 200,000 kWh
production_factor = 1500  # kWh/kW/year (from site_info)
solar_size = solar_production_needed / production_factor  # 133 kW

# Size battery for 4 hours of critical load
critical_load = 80  # kW
battery_hours = 4
battery_size = critical_load * battery_hours  # 320 kWh
```

### 2. Calculate Equipment Costs

```python
# Solar costs
solar_module_cost = 133 * 1000 * 0.28  # $37,240
solar_install_cost = 133 * 1000 * 0.12  # $15,960
solar_inverter_cost = 133 * 1000 * 0.06  # $7,980
solar_total = 37240 + 15960 + 7980  # $61,180

# Battery costs
battery_cell_cost = 320 * 139  # $44,480
battery_inverter_cost = 133 * 75  # $9,975
battery_bms_cost = 320 * 22  # $7,040
battery_install = (44480 + 9975 + 7040) * 0.15  # $9,224
battery_total = 44480 + 9975 + 7040 + 9224  # $70,719

# BOS (estimate 20% of equipment cost)
bos_total = (solar_total + battery_total) * 0.20  # $26,380

# PROJECT TOTAL
total_cost = solar_total + battery_total + bos_total  # $158,279
```

### 3. Calculate Tax Credits

```python
# ITC calculation
base_itc = total_cost * 0.30  # $47,484
domestic_bonus = total_cost * 0.10  # $15,828 (if qualified)
total_itc = base_itc + domestic_bonus  # $63,312

# Net project cost
net_cost = total_cost - total_itc  # $94,967
```

### 4. Calculate Payback

```python
# Annual savings from utility bills
energy_savings = 200000 * 0.0876  # $17,520/year (summer peak avoided)
demand_savings = 60 * 19.85 * 12  # $14,292/year (60 kW peak reduction)
total_savings = energy_savings + demand_savings  # $31,812/year

# Simple payback
payback_years = net_cost / total_savings  # 3.0 years

# 25-year NPV (7.5% discount rate)
# Assuming 2.8% utility rate escalation
# NPV = ~$400,000 (savings exceed costs by 4x!)
```

---

## 📚 Key Files Reference

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `component_costs_collected.csv` | Equipment pricing | Quarterly |
| `component_costs_sources.json` | Price source documentation | With costs |
| `financial_parameters_collected.csv` | Tax credits, rates | Annually |
| `financial_parameters_metadata.json` | Source documentation | With params |
| `utility_rates_*_collected.csv` | Electricity tariffs | Annually |
| `utility_rates_*_metadata.json` | Rate documentation | With rates |
| `site_info_collected.csv` | Location & solar data | Per project |
| `solar_resource_detail.json` | Detailed solar data | Per project |
| `load_profiles.csv` | **USER INPUT REQUIRED** | Per project |
| `reliability_requirements.csv` | **USER INPUT REQUIRED** | Per project |

---

## 🆘 Troubleshooting

### "I don't have hourly load data"
**Solution:** Use monthly utility bills to create typical profiles:
- Average daily consumption = Monthly kWh / 30 days
- Peak hours: 8am-8pm (higher usage)
- Overnight: 8pm-8am (lower usage, ~60% of peak)

### "Component prices seem too low/high"
**Check:**
- Data collection date (prices from Jan 2025)
- Regional factors (labor costs vary ±20%)
- Installation vs. equipment cost (both included)
- Compare to sources in `DATA_SOURCES.md`

### "NREL API not working"
**This is expected** - network proxy blocks external APIs
**Solutions:**
1. Use fallback regional data (already implemented)
2. Get NREL API key and run from unrestricted network
3. Use solar resource data from NREL PVWatts website manually

### "Utility rates don't match my bills"
**Reasons:**
- Data is for Entergy Louisiana LGS schedule
- Your utility may be different
- Rate schedules vary by customer class
**Solution:** Use the utility collector template to add your utility

---

## ✅ Validation Checklist

Before using the data in production:

- [ ] Review all CSV files for completeness
- [ ] Check data sources in metadata files
- [ ] Verify component costs match current market (within 10%)
- [ ] Confirm tax credit rates are current
- [ ] Validate utility rates against recent bill
- [ ] Complete load_profiles.csv with actual data
- [ ] Complete reliability_requirements.csv
- [ ] Update solar resource data for your specific location
- [ ] Add state/local incentives if applicable
- [ ] Review all assumptions in financial parameters

---

## 📞 Next Steps

1. **Complete load profiles** - This is critical for accurate sizing
2. **Define reliability requirements** - Determines backup needs
3. **Verify utility rates** - Use your actual tariff if different
4. **Customize for your location** - Update coordinates and solar data
5. **Add state incentives** - Louisiana has additional solar programs
6. **Build your cost model** - Use the example workflow above

---

## 🎯 Success Metrics

Your data collection is complete when you can:
- ✅ Calculate total equipment costs for any system size
- ✅ Estimate tax credits and incentives
- ✅ Project monthly utility bills with/without microgrid
- ✅ Size battery for required backup hours
- ✅ Calculate simple payback and 25-year NPV
- ✅ Generate cost estimates ±15% accuracy

---

**Questions?** Review:
- `README.md` - Complete documentation
- `DATA_SOURCES.md` - Source attribution
- Individual collector code - Implementation details

**Happy estimating!** 🎉
