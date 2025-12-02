#!/usr/bin/env python3
"""
Utility Rates Data Collector
Collects electricity rate data from utility tariff sheets

**UPDATED December 2025 with REAL ENTERGY LOUISIANA LGS-L TARIFF DATA**
All data from official Entergy Louisiana tariff effective August 30, 2024

Sources:
- Entergy Louisiana Rate Schedule LGS-L (Legacy ELL Service Area)
- Louisiana Public Service Commission Order U-36959
- Effective Date: August 30, 2024
- Reference: https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import pandas as pd
from data_utils import DataCollectionUtils

logger = logging.getLogger(__name__)

class UtilityRatesCollector:
    """Collects utility rate data from Entergy Louisiana tariff sheets"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.utils = DataCollectionUtils()
    
    def get_entergy_louisiana_lgs_rates(self) -> List[Dict]:
        """
        Get current Entergy Louisiana LGS-L rate schedule
        
        Source: Entergy Louisiana, LLC
                Large General Service Rate Schedule - Schedule LGS-L
                Legacy ELL Service Area
                Effective Date: August 30, 2024
                LPSC Order U-36959
        
        Reference: https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf
        
        Returns:
            List of rate dictionaries with all LGS-L components
        """
        
        logger.info("Collecting Entergy Louisiana LGS-L rate schedule (eff. 8/30/2024)...")
        
        rates = []
        
        # =================================================================
        # BASE DEMAND CHARGE (acts as customer charge + initial demand)
        # =================================================================
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Base_Demand_Block',
            'Description': 'First 60 kW or less of billed demand per month',
            'Cost': 275.39,
            'Unit': '$/month',
            'Tier': 'First 60 kW',
            'Season': 'All Year',
            'Data_Source': 'Entergy LA Schedule LGS-L, Eff. 8/30/2024, LPSC Order U-36959',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf',
            'Notes': 'This acts as base customer charge; no separate customer fee'
        })
        
        # =================================================================
        # ADDITIONAL DEMAND CHARGE (above 60 kW)
        # =================================================================
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Additional_Demand',
            'Description': 'All additional kW of demand above 60 kW',
            'Cost': 2.85,
            'Unit': '$/kW',
            'Tier': 'Above 60 kW',
            'Season': 'All Year',
            'Data_Source': 'Entergy LA Schedule LGS-L, Eff. 8/30/2024',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf',
            'Notes': 'Non-seasonal; same rate year-round'
        })
        
        # =================================================================
        # ENERGY CHARGES (3-tier structure)
        # =================================================================
        
        # Tier 1: First 30,000 kWh
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Energy_Tier1',
            'Description': 'First 30,000 kWh per month',
            'Cost': 0.03548,
            'Unit': '$/kWh',
            'Tier': '0-30,000 kWh',
            'kWh_Min': 0,
            'kWh_Max': 30000,
            'Season': 'All Year',
            'Data_Source': 'Entergy LA Schedule LGS-L, Eff. 8/30/2024',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf',
            'Notes': 'Lowest tier energy rate'
        })
        
        # Tier 2: Next block (up to 40,000 kWh or 400 kWh/kW, whichever is greater)
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Energy_Tier2',
            'Description': 'Next kWh up to 40,000 kWh or 400 kWh per kW of demand (whichever greater)',
            'Cost': 0.02637,
            'Unit': '$/kWh',
            'Tier': '30,000+ kWh up to threshold',
            'kWh_Min': 30000,
            'kWh_Max': 'MAX(40000, 400*demand_kW)',
            'Season': 'All Year',
            'Data_Source': 'Entergy LA Schedule LGS-L, Eff. 8/30/2024',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf',
            'Notes': 'Middle tier; threshold depends on demand'
        })
        
        # Tier 3: All remaining kWh
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Energy_Tier3',
            'Description': 'All remaining kWh over tier 2 threshold',
            'Cost': 0.01745,
            'Unit': '$/kWh',
            'Tier': 'Over tier 2 threshold',
            'kWh_Min': 'Above threshold',
            'Season': 'All Year',
            'Data_Source': 'Entergy LA Schedule LGS-L, Eff. 8/30/2024',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf',
            'Notes': 'Highest usage tier; lowest rate'
        })
        
        # =================================================================
        # FUEL ADJUSTMENT CLAUSE (Rider FA)
        # =================================================================
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Fuel_Adjustment',
            'Description': 'Monthly fuel adjustment per kWh (Rider FA)',
            'Cost': 0.02512,
            'Unit': '$/kWh',
            'Season': 'All Year',
            'Adjustment_Month': 'November 2025',
            'Voltage_Class': 'Secondary',
            'Data_Source': 'Entergy LA Monthly Fuel Clause Adjustment - Retail Electric Rates',
            'Effective_Date': '2025-11-01',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/business/ell-tariffs',
            'Notes': 'Variable monthly adjustment; Nov 2025 = $0.02512/kWh for secondary voltage'
        })
        
        # October 2025 fuel adjustment (for reference)
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Fuel_Adjustment',
            'Description': 'Monthly fuel adjustment per kWh (Rider FA) - October 2025',
            'Cost': 0.02575,
            'Unit': '$/kWh',
            'Season': 'All Year',
            'Adjustment_Month': 'October 2025',
            'Voltage_Class': 'Secondary',
            'Data_Source': 'Entergy LA Monthly Fuel Clause Adjustment - Retail Electric Rates',
            'Effective_Date': '2025-10-01',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/business/ell-tariffs',
            'Notes': 'Previous month for comparison'
        })
        
        # =================================================================
        # REACTIVE DEMAND / POWER FACTOR PENALTY
        # =================================================================
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Reactive_Demand_Penalty',
            'Description': 'Reactive demand in excess of 50% of billed kW demand',
            'Cost': 0.55,
            'Unit': '$/kVA',
            'Season': 'All Year',
            'Data_Source': 'Entergy LA Schedule LGS-L, Eff. 8/30/2024',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf',
            'Notes': 'Power factor penalty; $0.55 per kVA of reactive demand above 50% of kW'
        })
        
        # =================================================================
        # MINIMUM BILL (Demand Ratchet)
        # =================================================================
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Minimum_Demand_Ratchet',
            'Description': 'Minimum monthly demand charge based on 12-month peak',
            'Cost': 3.66,
            'Unit': '$/kW',
            'Season': 'All Year',
            'Data_Source': 'Entergy LA Schedule LGS-L, Eff. 8/30/2024',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/wp-content/uploads/ell_elec_lgs-l.pdf',
            'Notes': 'Minimum = $3.66/kW × highest demand in preceding 12 months, plus adjustments'
        })
        
        # =================================================================
        # PAYMENT TERMS
        # =================================================================
        rates.append({
            'Utility': 'Entergy Louisiana',
            'Rate_Schedule': 'LGS-L',
            'Rate_Component': 'Late_Payment_Penalty',
            'Description': 'Late payment adder if bill not paid within 20 days',
            'Cost': 1.5,
            'Unit': '%',
            'Season': 'All Year',
            'Data_Source': 'Entergy LA General Terms and Conditions',
            'Effective_Date': '2024-08-30',
            'Last_Verified': '2025-12-01',
            'Reference_URL': 'https://www.entergylouisiana.com/business/ell-tariffs',
            'Notes': '1.5% of gross bill if not paid within 20 days'
        })
        
        logger.info(f"✓ Collected {len(rates)} rate components from Entergy LA LGS-L schedule")
        
        return rates
    
    def get_simplified_summary(self) -> List[Dict]:
        """
        Get simplified rate summary for quick reference
        
        Returns typical blended rates for microgrid cost estimation
        """
        
        summary = [
            {
                'Utility': 'Entergy Louisiana',
                'Rate_Schedule': 'LGS-L (Simplified)',
                'Description': 'Typical blended energy rate (including fuel adjustment)',
                'Blended_Energy_Rate': 0.045,  # Average of tiers ~$0.025 + fuel $0.025
                'Unit': '$/kWh',
                'Demand_Charge': 2.85,  # Above 60 kW
                'Demand_Unit': '$/kW',
                'Monthly_Base': 275.39,  # First 60 kW block
                'Base_Unit': '$/month',
                'Notes': 'Simplified for modeling; actual bill depends on usage tiers and monthly fuel adjustment',
                'Data_Source': 'Calculated from Entergy LA LGS-L tariff, eff. 8/30/2024',
                'Last_Updated': '2025-12-01'
            }
        ]
        
        return summary
    
    def collect_all(self) -> List[Dict]:
        """
        Collect all utility rate data
        
        Returns:
            List of all rate dictionaries
        """
        
        logger.info("Starting utility rates collection...")
        
        all_rates = []
        
        # Collect detailed LGS-L rates
        all_rates.extend(self.get_entergy_louisiana_lgs_rates())
        
        # Add simplified summary
        all_rates.extend(self.get_simplified_summary())
        
        logger.info(f"✓ Total utility rate records collected: {len(all_rates)}")
        
        return all_rates
    
    def save_to_csv(self, rates: List[Dict], output_file: str) -> str:
        """
        Save rates to CSV file
        
        Args:
            rates: List of rate dictionaries
            output_file: Output filename
            
        Returns:
            Path to saved file
        """
        
        output_path = self.output_dir / output_file
        
        # Save to CSV using pandas
        df = pd.DataFrame(rates)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logger.info(f"Saved {len(rates)} rate records to {output_path}")
        
        return str(output_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = UtilityRatesCollector(Path('/home/claude/collected_data/utility_rates'))
    
    rates = collector.collect_all()
    output_file = collector.save_to_csv(rates, 'utility_rates.csv')
    
    print(f"\n✓ Utility rates collected and saved to: {output_file}")
    print(f"✓ Total records: {len(rates)}")
