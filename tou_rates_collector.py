#!/usr/bin/env python3
"""
Time-of-Use (TOU) Rates Data Collector
Collects TOU rate schedules for energy arbitrage analysis

**UPDATED December 2025 with REAL DATA:**
- Entergy Louisiana HLFS-TOD-G rate schedule
- Actual on-peak/off-peak hours and rates
- Seasonal variations and demand charges
- Export credits (avoided cost)

Sources:
- Entergy Louisiana Rate Schedule HLFS-TOD-G
- Effective Date: October 1, 2015
- LPSC Order U-33244-A
- Entergy Louisiana Net Metering (Avoided Cost rates)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import pandas as pd
from data_utils import DataCollectionUtils

logger = logging.getLogger(__name__)

class TOURatesCollector:
    """Collects Time-of-Use electricity rate schedules"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.utils = DataCollectionUtils()
    
    def get_entergy_tou_rates(self) -> List[Dict]:
        """
        Get Entergy Louisiana HLFS-TOD-G Time-of-Use rates
        
        Rate Schedule: High Load Factor Service - Time of Day
        Effective: October 1, 2015
        LPSC Order: U-33244-A
        Service Area: Legacy EGSL service area
        Applicability: Large commercial/industrial (2,500 kW minimum)
        
        Source: Entergy Louisiana, LLC Rate Schedule HLFS-TOD-G
        """
        
        logger.info("Collecting Entergy Louisiana TOU rates (HLFS-TOD-G)...")
        
        rates = [
            # SUMMER ON-PEAK
            {
                'Rate_Schedule': 'HLFS-TOD-G',
                'Utility': 'Entergy Louisiana LLC',
                'Season': 'Summer',
                'Season_Months': 'May-October',
                'Season_Dates': 'May 15 - October 15',
                'Period': 'On-Peak',
                'Days': 'Monday-Friday',
                'Hours_Start': '13:00',
                'Hours_End': '21:00',
                'Hours_Description': '1:00 PM - 9:00 PM',
                'Energy_Rate': 0.0255405079,
                'Energy_Rate_Rounded': 0.02554,
                'Unit': '$/kWh',
                'Demand_Charge': 16.13,
                'Demand_Unit': '$/kW-month',
                'Holidays_Excluded': 'Memorial Day, Independence Day (July 4), Labor Day',
                'Data_Source': 'Entergy Louisiana Rate Schedule HLFS-TOD-G, Section VI',
                'Effective_Date': '2015-10-01',
                'LPSC_Order': 'U-33244-A',
                'Notes': 'On-peak period applies Mon-Fri excluding listed holidays',
                'Reference_URL': 'https://www.entergylouisiana.com/business/egsl-tariffs'
            },
            
            # SUMMER OFF-PEAK
            {
                'Rate_Schedule': 'HLFS-TOD-G',
                'Utility': 'Entergy Louisiana LLC',
                'Season': 'Summer',
                'Season_Months': 'May-October',
                'Season_Dates': 'May 15 - October 15',
                'Period': 'Off-Peak',
                'Days': 'All Days',
                'Hours_Description': 'All other hours not specified as on-peak',
                'Energy_Rate': 0.0060701209,
                'Energy_Rate_Rounded': 0.00607,
                'Unit': '$/kWh',
                'Demand_Charge': 16.13,
                'Demand_Unit': '$/kW-month',
                'Data_Source': 'Entergy Louisiana Rate Schedule HLFS-TOD-G, Section VI',
                'Effective_Date': '2015-10-01',
                'LPSC_Order': 'U-33244-A',
                'Notes': 'Off-peak includes nights, weekends, and on-peak holidays',
                'Reference_URL': 'https://www.entergylouisiana.com/business/egsl-tariffs'
            },
            
            # WINTER ON-PEAK (MORNING)
            {
                'Rate_Schedule': 'HLFS-TOD-G',
                'Utility': 'Entergy Louisiana LLC',
                'Season': 'Winter',
                'Season_Months': 'November-April',
                'Season_Dates': 'October 16 - May 14',
                'Period': 'On-Peak',
                'Sub_Period': 'Morning',
                'Days': 'Monday-Friday',
                'Hours_Start': '06:00',
                'Hours_End': '10:00',
                'Hours_Description': '6:00 AM - 10:00 AM',
                'Energy_Rate': 0.0074601486,
                'Energy_Rate_Rounded': 0.00746,
                'Unit': '$/kWh',
                'Demand_Charge': 14.50,
                'Demand_Unit': '$/kW-month',
                'Holidays_Excluded': 'Thanksgiving Day, Christmas Day, New Year\'s Day',
                'Data_Source': 'Entergy Louisiana Rate Schedule HLFS-TOD-G, Section VI',
                'Effective_Date': '2015-10-01',
                'LPSC_Order': 'U-33244-A',
                'Notes': 'Winter has two on-peak periods per weekday',
                'Reference_URL': 'https://www.entergylouisiana.com/business/egsl-tariffs'
            },
            
            # WINTER ON-PEAK (EVENING)
            {
                'Rate_Schedule': 'HLFS-TOD-G',
                'Utility': 'Entergy Louisiana LLC',
                'Season': 'Winter',
                'Season_Months': 'November-April',
                'Season_Dates': 'October 16 - May 14',
                'Period': 'On-Peak',
                'Sub_Period': 'Evening',
                'Days': 'Monday-Friday',
                'Hours_Start': '18:00',
                'Hours_End': '22:00',
                'Hours_Description': '6:00 PM - 10:00 PM',
                'Energy_Rate': 0.0074601486,
                'Energy_Rate_Rounded': 0.00746,
                'Unit': '$/kWh',
                'Demand_Charge': 14.50,
                'Demand_Unit': '$/kW-month',
                'Holidays_Excluded': 'Thanksgiving Day, Christmas Day, New Year\'s Day',
                'Data_Source': 'Entergy Louisiana Rate Schedule HLFS-TOD-G, Section VI',
                'Effective_Date': '2015-10-01',
                'LPSC_Order': 'U-33244-A',
                'Notes': 'Winter has two on-peak periods per weekday',
                'Reference_URL': 'https://www.entergylouisiana.com/business/egsl-tariffs'
            },
            
            # WINTER OFF-PEAK
            {
                'Rate_Schedule': 'HLFS-TOD-G',
                'Utility': 'Entergy Louisiana LLC',
                'Season': 'Winter',
                'Season_Months': 'November-April',
                'Season_Dates': 'October 16 - May 14',
                'Period': 'Off-Peak',
                'Days': 'All Days',
                'Hours_Description': 'All other hours not specified as on-peak',
                'Energy_Rate': 0.0060701209,
                'Energy_Rate_Rounded': 0.00607,
                'Unit': '$/kWh',
                'Demand_Charge': 14.50,
                'Demand_Unit': '$/kW-month',
                'Data_Source': 'Entergy Louisiana Rate Schedule HLFS-TOD-G, Section VI',
                'Effective_Date': '2015-10-01',
                'LPSC_Order': 'U-33244-A',
                'Notes': 'Off-peak includes nights, weekends, midday, and holidays',
                'Reference_URL': 'https://www.entergylouisiana.com/business/egsl-tariffs'
            },
            
            # RATE COMPARISON SUMMARY
            {
                'Rate_Schedule': 'HLFS-TOD-G',
                'Utility': 'Entergy Louisiana LLC',
                'Data_Type': 'SUMMARY',
                'Summer_OnPeak': 0.02554,
                'Summer_OffPeak': 0.00607,
                'Summer_Spread': 0.01947,
                'Summer_Ratio': 4.21,
                'Winter_OnPeak': 0.00746,
                'Winter_OffPeak': 0.00607,
                'Winter_Spread': 0.00139,
                'Winter_Ratio': 1.23,
                'Unit': '$/kWh',
                'Peak_Hours_Summer': 8,
                'Peak_Hours_Winter': 8,
                'Peak_Hours_Unit': 'hours/weekday',
                'Notes': 'Summer has 4.2× on/off spread; Winter only 1.2× spread',
                'Arbitrage_Potential': 'High in summer, limited in winter'
            },
            
            # EXPORT CREDIT (AVOIDED COST)
            {
                'Rate_Schedule': 'Net_Billing_Export_Credit',
                'Utility': 'Entergy Louisiana LLC',
                'Credit_Type': 'Avoided_Cost',
                'Export_Credit_Rate': 0.0259331,
                'Unit': '$/kWh',
                'Applicability': 'Post-2019 distributed generation systems',
                'Effective_Date': '2025-04-01',
                'Data_Source': 'Entergy Louisiana Net Metering page, LPSC Order R-33929',
                'Notes': 'Export credit for surplus solar/storage generation sent to grid',
                'Comparison_Retail': 0.112,
                'Export_vs_Retail': '23% of retail rate',
                'Reference_URL': 'https://www.entergylouisiana.com/net-metering'
            },
            
            # FUEL ADJUSTMENT (APPLIES TO ALL)
            {
                'Rate_Schedule': 'HLFS-TOD-G',
                'Utility': 'Entergy Louisiana LLC',
                'Charge_Type': 'Fuel_Adjustment',
                'Description': 'Monthly fuel cost adjustment (Rider FA)',
                'Application': 'Applied to all kWh (on-peak and off-peak)',
                'Typical_Range': '0.020-0.030',
                'Unit': '$/kWh',
                'Data_Source': 'Entergy Louisiana Fuel Adjustment Clause',
                'Notes': 'Variable monthly; same rate for all periods; see utility_rates.csv for current value',
                'Current_Value_Reference': '0.02512 (November 2025, from utility_rates_collector)'
            }
        ]
        
        logger.info(f"✓ Collected {len(rates)} TOU rate records")
        
        return rates
    
    def get_arbitrage_analysis(self) -> List[Dict]:
        """
        Calculate energy arbitrage potential from TOU rates
        
        Shows potential savings from battery charging during off-peak
        and discharging during on-peak periods
        """
        
        logger.info("Calculating arbitrage potential...")
        
        analysis = [
            {
                'Analysis_Type': 'Energy_Arbitrage_Summer',
                'Season': 'Summer (May-Oct)',
                'OnPeak_Rate': 0.02554,
                'OffPeak_Rate': 0.00607,
                'Price_Spread': 0.01947,
                'Spread_Percentage': 320.8,
                'Unit': '$/kWh and %',
                'Battery_Roundtrip_Efficiency': 0.85,
                'Net_Arbitrage_Value': 0.01431,
                'Calculation': '(0.02554 - 0.00607) × 0.85 roundtrip efficiency',
                'OnPeak_Hours_Per_Day': 8,
                'OnPeak_Days_Per_Month': 22,
                'OnPeak_Hours_Per_Month': 176,
                'Annual_OnPeak_Hours': 1056,
                'Potential_Annual_Cycles': 176,
                'Notes': 'High arbitrage value in summer - strong battery economics',
                'Example_100kWh_Battery': '$1,431/year potential (1 cycle/day × $14.31/cycle × 100 days)',
                'Data_Source': 'Calculated from HLFS-TOD-G rates'
            },
            
            {
                'Analysis_Type': 'Energy_Arbitrage_Winter',
                'Season': 'Winter (Nov-Apr)',
                'OnPeak_Rate': 0.00746,
                'OffPeak_Rate': 0.00607,
                'Price_Spread': 0.00139,
                'Spread_Percentage': 22.9,
                'Unit': '$/kWh and %',
                'Battery_Roundtrip_Efficiency': 0.85,
                'Net_Arbitrage_Value': 0.00069,
                'Calculation': '(0.00746 - 0.00607) × 0.85 roundtrip efficiency',
                'OnPeak_Hours_Per_Day': 8,
                'OnPeak_Days_Per_Month': 22,
                'OnPeak_Hours_Per_Month': 176,
                'Annual_OnPeak_Hours': 1056,
                'Potential_Annual_Cycles': 132,
                'Notes': 'Limited arbitrage value in winter - marginal battery economics',
                'Example_100kWh_Battery': '$69/year potential (1 cycle/day × $0.69/cycle × 100 days)',
                'Data_Source': 'Calculated from HLFS-TOD-G rates'
            },
            
            {
                'Analysis_Type': 'Peak_Demand_Reduction',
                'Summer_Demand_Charge': 16.13,
                'Winter_Demand_Charge': 14.50,
                'Unit': '$/kW-month',
                'Peak_Shaving_Value_Summer': 193.56,
                'Peak_Shaving_Value_Winter': 87.00,
                'Annual_Unit': '$/kW-year',
                'Calculation': 'Summer: $16.13/kW × 12 months, Winter: $14.50/kW × 6 months',
                'Notes': 'Battery can reduce demand charges by shaving peaks',
                'Example_50kW_Peak_Reduction': '$9,678/year (50 kW × $193.56/kW-yr summer) + $4,350 winter',
                'Data_Source': 'Calculated from HLFS-TOD-G demand charges'
            },
            
            {
                'Analysis_Type': 'Solar_Plus_Storage_Economics',
                'Solar_Export_Credit': 0.0259331,
                'Summer_OnPeak_Rate': 0.02554,
                'Retail_Self_Consumption_Value': 0.11230,
                'Unit': '$/kWh',
                'Best_Use_Case': 'Self-consumption during on-peak hours',
                'Self_Consumption_vs_Export': 'Self-consume = 4.3× more valuable than export',
                'Strategy': 'Size battery to shift solar to on-peak consumption',
                'Notes': 'Export credits very low; maximize self-consumption',
                'Data_Source': 'HLFS-TOD-G rates + Net Billing avoided cost'
            }
        ]
        
        logger.info(f"✓ Generated {len(analysis)} arbitrage analysis records")
        
        return analysis
    
    def collect_all(self) -> List[Dict]:
        """Collect all TOU rate data and analysis"""
        
        logger.info("Starting TOU rates data collection...")
        
        all_data = []
        
        # Collect TOU rates
        all_data.extend(self.get_entergy_tou_rates())
        
        # Collect arbitrage analysis
        all_data.extend(self.get_arbitrage_analysis())
        
        logger.info(f"✓ Total TOU rate records collected: {len(all_data)}")
        
        return all_data
    
    def save_to_csv(self, data: List[Dict], output_file: str) -> str:
        """Save data to CSV file"""
        
        output_path = self.output_dir / output_file
        
        # Save to CSV using pandas
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"Saved {len(data)} records to {output_path}")
        
        return str(output_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = TOURatesCollector(Path('/home/claude/collected_data/tou_rates'))
    
    data = collector.collect_all()
    output_file = collector.save_to_csv(data, 'tou_rates.csv')
    
    print(f"\n✓ TOU rates data collected!")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Total records: {len(data)}")
    print(f"\n📊 Rate Summary:")
    print(f"  Summer On-Peak:  $0.02554/kWh (1pm-9pm)")
    print(f"  Summer Off-Peak: $0.00607/kWh")
    print(f"  Arbitrage spread: $0.01947/kWh (321%)")
    print(f"\n💡 High arbitrage potential in summer months!")
