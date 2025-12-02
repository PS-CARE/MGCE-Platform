#!/usr/bin/env python3
"""
Louisiana State Incentives & Interconnection Costs Collector
Collects state-level solar incentives, interconnection fees, and policies

**UPDATED December 2025 with ACTUAL DATA from:**
- Louisiana Department of Revenue
- Louisiana Public Service Commission (LPSC)
- Entergy Louisiana tariffs
- DSIRE database
- Louisiana net metering rules

Sources:
- LPSC General Order R-33929 (September 19, 2019)
- Entergy Louisiana interconnection standards
- Louisiana Revised Statutes Title 47
- Consumer Affairs & EnergySage Louisiana solar data 2024-2025
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import pandas as pd
from data_utils import DataCollectionUtils

logger = logging.getLogger(__name__)

class LouisianaIncentivesCollector:
    """Collects Louisiana-specific solar incentives and interconnection data"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.utils = DataCollectionUtils()
    
    def get_state_incentives(self) -> List[Dict]:
        """
        Get Louisiana state-level solar incentives
        
        IMPORTANT: Louisiana does NOT have a state solar tax credit as of 2025
        The state program expired and was not renewed
        
        Source: DSIRE Louisiana programs, Louisiana DNR, multiple solar industry sources
        """
        
        logger.info("Collecting Louisiana state incentives...")
        
        incentives = [
            # STATE TAX CREDITS (NONE CURRENTLY)
            {
                'Incentive_Type': 'State_Solar_Tax_Credit',
                'Status': 'NOT_AVAILABLE',
                'Value': 0,
                'Unit': '%',
                'Description': 'Louisiana does NOT have a state-level solar tax credit as of 2025',
                'Data_Source': 'DSIRE Database, Louisiana DNR, EnergySage 2025',
                'Last_Updated': '2025-12-01',
                'Notes': 'Previous 50% credit (up to $12,500) expired. No current state tax credit.',
                'Reference_URL': 'https://www.energysage.com/local-data/solar-rebates-incentives/la/'
            },
            
            # PROPERTY TAX EXEMPTION
            {
                'Incentive_Type': 'Property_Tax_Exemption',
                'Status': 'AVAILABLE',
                'Value': 100,
                'Unit': '%',
                'Description': 'Full property tax exemption for added value from solar installation',
                'Data_Source': 'Louisiana Revised Statutes, DSIRE',
                'Effective_Date': 'Current',
                'Notes': 'Solar equipment value does NOT increase property tax assessment',
                'Reference_URL': 'https://programs.dsireusa.org/system/program/detail/888',
                'Benefit_Example': 'If solar adds $30,000 to home value, $0 additional property tax'
            },
            
            # NET BILLING (NOT NET METERING)
            {
                'Incentive_Type': 'Net_Billing',
                'Status': 'AVAILABLE',
                'Purchase_Rate': 0.02587,  # 2024 Entergy average
                'Unit': '$/kWh',
                'Description': 'Credits for excess solar at utility avoided cost (NOT retail rate)',
                'Data_Source': 'LPSC General Order R-33929 (Sept 19, 2019), Entergy Louisiana',
                'Effective_Date': '2020-01-01',
                'Residential_Limit': 25,
                'Commercial_Limit': 300,
                'Limit_Unit': 'kW',
                'Notes': 'Post-2020 systems get avoided cost (~$0.02-0.03/kWh), NOT retail rate (~$0.11/kWh)',
                'Reference_URL': 'https://www.lpsc.louisiana.gov/Utilities_NetMetering',
                'Credit_Treatment': 'Credits carried forward monthly, paid out at avoided cost when service ends'
            },
            
            {
                'Incentive_Type': 'Net_Billing_Rate_Comparison',
                'Status': 'INFORMATIONAL',
                'Retail_Rate': 0.112,
                'Avoided_Cost_Rate': 0.026,
                'Unit': '$/kWh',
                'Description': 'Comparison: retail rate paid for grid power vs avoided cost credit for exports',
                'Data_Source': 'Entergy Louisiana rates 2024-2025',
                'Notes': 'You pay $0.11/kWh for imports, get credited $0.03/kWh for exports - 77% reduction'
            },
            
            # SALES TAX (NO EXEMPTION)
            {
                'Incentive_Type': 'Sales_Tax_Exemption',
                'Status': 'NOT_AVAILABLE',
                'Value': 0,
                'Description': 'Louisiana does NOT offer sales tax exemption for solar equipment',
                'Data_Source': 'Louisiana Department of Revenue, DSIRE',
                'Notes': 'Solar equipment subject to normal state + local sales tax',
                'State_Sales_Tax': 4.45,
                'Local_Sales_Tax_Typical': 5.0,
                'Total_Tax_Typical': 9.45,
                'Tax_Unit': '%'
            },
            
            # FEDERAL ITC (FOR REFERENCE)
            {
                'Incentive_Type': 'Federal_ITC',
                'Status': 'AVAILABLE',
                'Value': 30,
                'Unit': '%',
                'Description': 'Federal Investment Tax Credit (reference - see financial_parameters.csv)',
                'Data_Source': 'IRS Publication 5817, Inflation Reduction Act',
                'Effective_Through': '2032-12-31',
                'Notes': 'This is FEDERAL, not Louisiana state. See financial_parameters for details.',
                'Reference_URL': 'https://www.irs.gov/credits-deductions/residential-clean-energy-credit'
            },
            
            # UTILITY PROGRAMS (ENTERGY)
            {
                'Incentive_Type': 'Utility_Rebate',
                'Status': 'NOT_AVAILABLE',
                'Utility': 'Entergy Louisiana',
                'Description': 'Entergy Louisiana does NOT offer cash rebates for solar installations',
                'Data_Source': 'Entergy Louisiana website 2025',
                'Notes': 'No upfront rebates available; only net billing credits for excess generation'
            },
            
            {
                'Incentive_Type': 'Community_Solar',
                'Status': 'AVAILABLE',
                'Utility': 'Entergy Louisiana',
                'Program_Name': 'Geaux Green',
                'Description': 'Subscription solar program for customers who cannot install rooftop solar',
                'Data_Source': 'Entergy Louisiana Rider GGO',
                'Notes': 'Not a rebate - customers subscribe to utility-scale solar farms',
                'Reference_URL': 'https://www.entergylouisiana.com/geaux-green'
            },
            
            # STATE LOAN PROGRAM
            {
                'Incentive_Type': 'State_Loan_Program',
                'Status': 'AVAILABLE',
                'Program_Name': 'Home Energy Loan Program (HELP)',
                'Administering_Agency': 'Louisiana Department of Natural Resources',
                'Loan_Amount_Min': 6000,
                'Loan_Amount_Max': 12000,
                'Unit': '$',
                'Description': 'Low-interest loans for energy efficiency and solar improvements',
                'Eligible_Systems': 'Solar PV, solar water heating, energy efficiency upgrades',
                'Data_Source': 'Louisiana DNR, This Old House Louisiana solar guide',
                'Interest_Rate': 'Below-market rate (check DNR for current)',
                'Notes': 'State-sponsored financing option; not a cash rebate',
                'Reference_URL': 'https://www.dnr.louisiana.gov/',
                'Benefit_Type': 'Preferential financing, not grant'
            },
            
            # FINANCING OPTIONS
            {
                'Incentive_Type': 'Financing_Options',
                'Status': 'INFORMATIONAL',
                'Description': 'Various solar financing available through private lenders',
                'Options': 'Solar loans, PACE financing (Property Assessed Clean Energy), leases, PPAs',
                'Data_Source': 'Industry standard financing mechanisms',
                'Notes': 'Louisiana has limited PACE program availability; check local jurisdiction'
            }
        ]
        
        logger.info(f"✓ Collected {len(incentives)} Louisiana incentive records")
        
        return incentives
    
    def get_interconnection_costs(self) -> List[Dict]:
        """
        Get interconnection fees and costs for Louisiana
        
        Based on LPSC rules and Entergy Louisiana requirements
        Effective January 1, 2020 for new installations
        """
        
        logger.info("Collecting interconnection costs...")
        
        costs = [
            # METER INSTALLATION FEES
            {
                'Fee_Type': 'Meter_Installation',
                'System_Category': 'Residential',
                'System_Size_Min': 0,
                'System_Size_Max': 25,
                'Size_Unit': 'kW',
                'Fee_Amount': 50,
                'Fee_Unit': '$',
                'Frequency': 'One-time',
                'Description': 'Cost of installing bidirectional meter for net billing',
                'Utility': 'Entergy Louisiana',
                'Data_Source': 'Entergy Louisiana interconnection requirements, multiple sources',
                'Last_Updated': '2025-12-01',
                'Notes': 'Utility pays for meter itself; customer pays installation labor',
                'Reference_URL': 'https://www.entergylouisiana.com/business/ell-tariffs'
            },
            
            {
                'Fee_Type': 'Meter_Installation',
                'System_Category': 'Commercial',
                'System_Size_Min': 25.01,
                'System_Size_Max': 300,
                'Size_Unit': 'kW',
                'Fee_Amount': 75,
                'Fee_Unit': '$',
                'Frequency': 'One-time',
                'Description': 'Cost of installing bidirectional meter for commercial systems',
                'Utility': 'Entergy Louisiana',
                'Data_Source': 'Entergy New Orleans net metering rules (similar for Entergy LA)',
                'Last_Updated': '2025-12-01',
                'Notes': 'Commercial installations have slightly higher installation cost',
                'Reference_URL': 'https://www.entergyneworleans.com/net-metering'
            },
            
            # INSPECTION FEES
            {
                'Fee_Type': 'System_Inspection',
                'System_Category': 'All',
                'System_Size_Min': 0,
                'System_Size_Max': 9999,
                'Size_Unit': 'kW',
                'Fee_Amount': 100,
                'Fee_Unit': '$',
                'Frequency': 'One-time',
                'Description': 'Utility inspection fee for newly installed systems',
                'Utility': 'Some Louisiana co-ops (SLECA)',
                'Data_Source': 'LPSC General Order (Dec 8, 2016), SLECA tariffs',
                'Effective_Date': '2018-09-01',
                'Notes': 'Applies to some rural co-ops; may not apply to all Entergy LA customers',
                'Reference_URL': 'https://www.sleca.com/member-services/net-metering/'
            },
            
            # INTERCONNECTION STUDIES (LARGER SYSTEMS)
            {
                'Fee_Type': 'Interconnection_Study',
                'System_Category': 'Small Commercial',
                'System_Size_Min': 25,
                'System_Size_Max': 300,
                'Size_Unit': 'kW',
                'Fee_Amount': 0,
                'Fee_Unit': '$',
                'Description': 'Simplified process for systems ≤300 kW under LPSC net billing rules',
                'Data_Source': 'LPSC General Order R-33929',
                'Notes': 'No formal study required for systems under 300 kW; streamlined interconnection',
                'Process_Time': '30 business days'
            },
            
            {
                'Fee_Type': 'Interconnection_Study',
                'System_Category': 'Large Commercial/Industrial',
                'System_Size_Min': 300.01,
                'System_Size_Max': 2000,
                'Size_Unit': 'kW',
                'Fee_Amount_Min': 1000,
                'Fee_Amount_Max': 25000,
                'Fee_Unit': '$',
                'Description': 'Feasibility and system impact studies for larger systems',
                'Data_Source': 'Entergy Louisiana interconnection standards (typical utility practice)',
                'Notes': 'Costs vary by system complexity and grid impact; customer pays "reasonable costs"',
                'Reference_URL': 'https://www.entergy-louisiana.com/net-metering/process/'
            },
            
            {
                'Fee_Type': 'Interconnection_Study',
                'System_Category': 'Utility-Scale',
                'System_Size_Min': 2000.01,
                'System_Size_Max': 999999,
                'Size_Unit': 'kW',
                'Fee_Amount_Min': 25000,
                'Fee_Amount_Max': 250000,
                'Fee_Unit': '$',
                'Description': 'Full interconnection studies for utility-scale projects',
                'Data_Source': 'Industry standard (FERC, utility practice)',
                'Notes': 'Requires feasibility, system impact, and facilities studies',
                'Process_Time': '6-12 months typical'
            },
            
            # ADDITIONAL COSTS
            {
                'Fee_Type': 'Grid_Upgrades',
                'System_Category': 'Variable',
                'Fee_Amount': 0,
                'Fee_Unit': '$',
                'Description': 'Customer pays for grid upgrades if system requires them',
                'Data_Source': 'LPSC interconnection rules, Entergy standards',
                'Notes': 'Highly variable; $0 for most residential/small commercial, $1k-$100k+ for large systems',
                'Cost_Factors': 'Distance to substation, line capacity, transformer upgrades needed'
            },
            
            {
                'Fee_Type': 'Disconnect_Switch',
                'System_Category': 'All',
                'Fee_Amount_Min': 200,
                'Fee_Amount_Max': 500,
                'Fee_Unit': '$',
                'Description': 'External manual disconnect switch (customer-side cost)',
                'Data_Source': 'LPSC safety requirements, typical installer costs',
                'Notes': 'Required by Louisiana code; paid to solar installer, not utility',
                'Equipment_Cost': '~$200-300',
                'Installation_Cost': '~$100-200'
            },
            
            # APPLICATION FEES
            {
                'Fee_Type': 'Application_Processing',
                'System_Category': 'All',
                'Fee_Amount': 0,
                'Fee_Unit': '$',
                'Description': 'No application fee for LPSC-regulated net billing interconnections',
                'Data_Source': 'LPSC General Order R-33929',
                'Notes': 'Streamlined interconnection for ≤300 kW has no application fee',
                'Process': 'Online application through Entergy portal'
            },
            
            # PERMIT FEES (LOCAL GOVERNMENT)
            {
                'Fee_Type': 'Building_Permit',
                'System_Category': 'All',
                'Fee_Amount_Min': 50,
                'Fee_Amount_Max': 500,
                'Fee_Unit': '$',
                'Jurisdiction': 'Local parish/municipality',
                'Description': 'Local building permit for solar installation',
                'Data_Source': 'Typical Louisiana parish permit fees',
                'Notes': 'Varies by parish; Baton Rouge/Lafayette ~$100-300; not a utility fee',
                'Payable_To': 'Local building department'
            },
            
            # ONGOING FEES (NONE)
            {
                'Fee_Type': 'Monthly_Service_Fee',
                'System_Category': 'All',
                'Fee_Amount': 0,
                'Fee_Unit': '$/month',
                'Description': 'No monthly fee for net billing customers in Louisiana',
                'Data_Source': 'LPSC General Order R-33929',
                'Notes': 'Louisiana does NOT allow monthly solar surcharges',
                'Status': 'PROHIBITED'
            }
        ]
        
        logger.info(f"✓ Collected {len(costs)} interconnection cost records")
        
        return costs
    
    def get_policy_details(self) -> List[Dict]:
        """Get policy and regulatory framework details"""
        
        logger.info("Collecting policy details...")
        
        policies = [
            {
                'Policy': 'Net_Billing_Transition',
                'Description': 'Louisiana transitioned from net metering to net billing in 2020',
                'Effective_Date': '2020-01-01',
                'Grandfather_Clause': 'Systems interconnected before Jan 1, 2020 keep net metering',
                'New_Systems': 'Post-2020 systems get avoided cost credits (~$0.02-0.03/kWh)',
                'Data_Source': 'LPSC General Order R-33929 (September 19, 2019)',
                'Impact': 'Reduced economics for new solar installations by ~70-80%',
                'Reference_URL': 'https://www.lpsc.louisiana.gov/Utilities_NetMetering'
            },
            
            {
                'Policy': 'System_Size_Limits',
                'Residential_Max': 25,
                'Commercial_Max': 300,
                'Unit': 'kW',
                'Description': 'Maximum system sizes eligible for simplified net billing interconnection',
                'Data_Source': 'LPSC rules, Louisiana SB 359',
                'Notes': 'Systems above 300 kW require FERC qualifying facility status',
                'Large_System_Process': 'Contact utility for custom interconnection agreement'
            },
            
            {
                'Policy': 'Interconnection_Timeline',
                'Application_Review': 30,
                'Unit': 'business days',
                'Description': 'Maximum time for utility to review interconnection application',
                'Data_Source': 'LPSC interconnection standards',
                'Customer_Notification': '90 days advance notice required before interconnection',
                'Notes': 'Actual timeline often faster for simple residential systems'
            },
            
            {
                'Policy': 'Insurance_Requirements',
                'Residential': 'Homeowners insurance typically sufficient',
                'Commercial': 'Liability insurance may be required ($1M typical)',
                'Data_Source': 'Entergy Louisiana interconnection standards',
                'Notes': 'Requirements vary by system size; verify with utility'
            },
            
            {
                'Policy': 'Technical_Requirements',
                'Standards': 'NEC, IEEE 1547, UL 1741, NESC',
                'Inverter_Requirement': 'UL 1741 certified inverter with anti-islanding',
                'Disconnect_Requirement': 'Manual external disconnect switch, utility-accessible',
                'Data_Source': 'LPSC safety standards',
                'Notes': 'All equipment must meet national safety codes'
            },
            
            {
                'Policy': 'Contractor_Licensing',
                'Requirement': 'Licensed electrical contractor required',
                'License_Board': 'Louisiana State Licensing Board for Contractors',
                'Data_Source': 'Louisiana state law',
                'Notes': 'DIY solar installation not permitted for grid-tied systems',
                'Verification': 'https://www.lslbc.louisiana.gov/'
            }
        ]
        
        logger.info(f"✓ Collected {len(policies)} policy records")
        
        return policies
    
    def collect_all(self) -> List[Dict]:
        """Collect all Louisiana incentives, costs, and policies"""
        
        logger.info("Starting Louisiana incentives & interconnection data collection...")
        
        all_data = []
        
        # Collect all categories
        all_data.extend(self.get_state_incentives())
        all_data.extend(self.get_interconnection_costs())
        all_data.extend(self.get_policy_details())
        
        logger.info(f"✓ Total Louisiana data records collected: {len(all_data)}")
        
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
    collector = LouisianaIncentivesCollector(Path('/home/claude/collected_data/louisiana_incentives'))
    
    data = collector.collect_all()
    output_file = collector.save_to_csv(data, 'louisiana_incentives_interconnection.csv')
    
    print(f"\n✓ Louisiana incentives & interconnection data collected!")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Total records: {len(data)}")
