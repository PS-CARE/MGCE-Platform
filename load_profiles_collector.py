#!/usr/bin/env python3
"""
Load Profiles Data Collector
Collects Louisiana-specific energy consumption patterns for microgrid sizing

**UPDATED December 2025 with REAL LOUISIANA ENERGYPLUS DATA**
All load profiles from EnergyPlus simulations using Louisiana TMY3 weather data

Sources:
- EnergyPlus Commercial Reference Buildings (DOE)
- EnergyPlus Residential Prototype Buildings
- Louisiana TMY3 Weather Data (17 locations)
- Climate Zone 2A (Hot-Humid)

Data Files:
- RESIDENTIAL_LOAD_DATA_E_PLUS_OUTPUT/ (BASE, HIGH, LOW scenarios)
- COMMERCIAL_LOAD_DATA_E_PLUS_OUTPUT.part4/ (16 building types)

Reference: https://www.energy.gov/eere/buildings/commercial-reference-buildings
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Data paths
RESIDENTIAL_DATA_PATH = Path(__file__).parent / 'RESIDENTIAL_LOAD_DATA_E_PLUS_OUTPUT'
COMMERCIAL_DATA_PATH = Path(__file__).parent / 'COMMERCIAL_LOAD_DATA_E_PLUS_OUTPUT.part4'

class LoadProfilesCollector:
    """
    Collects Louisiana-specific energy load profile data for microgrid design
    
    Uses real EnergyPlus simulation data for Louisiana locations:
    - 17 Louisiana weather stations (TMY3 data)
    - 16 commercial building types
    - 3 residential scenarios (BASE, HIGH, LOW)
    - 8,760 hourly data points per file (1 year)
    """
    
    # Louisiana locations with TMY3 weather data
    LA_LOCATIONS = {
        'baton_rouge': 'USA_LA_Baton.Rouge-Ryan.AP.722317_TMY3',
        'new_orleans': 'USA_LA_New.Orleans.Intl.AP.722310_TMY3',
        'lafayette': 'USA_LA_Lafayette.RgnlAP.722405_TMY3',
        'shreveport': 'USA_LA_Shreveport.Rgnl.AP.722480_TMY3',
        'lake_charles': 'USA_LA_Lake.Charles.Rgnl.AP.722400_TMY3',
        'monroe': 'USA_LA_Monroe.Rgnl.AP.722486_TMY3',
        'houma': 'USA_LA_Houma-Terrebonne.AP.722406_TMY3',
        'alexandria': 'USA_LA_Alexandria-Esler.Rgnl.AP.722487_TMY3',
        'new_iberia': 'USA_LA_New.Iberia.722314_TMY3',
    }
    
    # Commercial building types from DOE Reference Buildings
    BUILDING_TYPES = {
        'small_office': ('RefBldgSmallOfficeNew2004', 'Small Office', 5500),
        'medium_office': ('RefBldgMediumOfficeNew2004', 'Medium Office', 53600),
        'large_office': ('RefBldgLargeOfficeNew2004', 'Large Office', 498600),
        'retail': ('RefBldgStand-aloneRetailNew2004', 'Standalone Retail', 24690),
        'strip_mall': ('RefBldgStripMallNew2004', 'Strip Mall', 22500),
        'supermarket': ('RefBldgSuperMarketNew2004', 'Supermarket', 45000),
        'primary_school': ('RefBldgPrimarySchoolNew2004', 'Primary School', 73960),
        'secondary_school': ('RefBldgSecondarySchoolNew2004', 'Secondary School', 210900),
        'hospital': ('RefBldgHospitalNew2004', 'Hospital', 241350),
        'outpatient': ('RefBldgOutPatientNew2004', 'Outpatient Clinic', 40950),
        'small_hotel': ('RefBldgSmallHotelNew2004', 'Small Hotel', 43200),
        'large_hotel': ('RefBldgLargeHotelNew2004', 'Large Hotel', 122100),
        'warehouse': ('RefBldgWarehouseNew2004', 'Warehouse', 52050),
        'quick_restaurant': ('RefBldgQuickServiceRestaurantNew2004', 'Quick Service Restaurant', 2500),
        'full_restaurant': ('RefBldgFullServiceRestaurantNew2004', 'Full Service Restaurant', 5500),
        'apartment': ('RefBldgMidriseApartmentNew2004', 'Midrise Apartment', 33700),
    }
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / 'collected_data'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.residential_path = RESIDENTIAL_DATA_PATH
        self.commercial_path = COMMERCIAL_DATA_PATH
    
    def _load_csv(self, filepath: Path) -> Optional[pd.DataFrame]:
        """Load CSV file and return DataFrame"""
        try:
            df = pd.read_csv(filepath)
            return df
        except Exception as e:
            logger.warning(f"Could not load {filepath}: {e}")
            return None
    
    def get_residential_profile(self, location: str = 'baton_rouge', 
                                 scenario: str = 'BASE') -> List[Dict]:
        """
        Get residential load profile from EnergyPlus data
        
        Args:
            location: Louisiana location key (e.g., 'baton_rouge')
            scenario: Load scenario ('BASE', 'HIGH', 'LOW')
            
        Returns:
            List of monthly summary dictionaries
        """
        
        logger.info(f"Loading residential profile: {location}, {scenario} scenario...")
        
        loc_code = self.LA_LOCATIONS.get(location, self.LA_LOCATIONS['baton_rouge'])
        filename = f"{loc_code}_{scenario}.csv"
        filepath = self.residential_path / scenario / filename
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return self._get_residential_fallback(location, scenario)
        
        df = self._load_csv(filepath)
        if df is None:
            return self._get_residential_fallback(location, scenario)
        
        # Parse date/time and extract month
        # Handle 24:00:00 timestamps by converting to next day 00:00:00
        def parse_datetime(dt_str):
            dt_str = dt_str.strip()
            if '24:00:00' in dt_str:
                dt_str = dt_str.replace('24:00:00', '00:00:00')
            try:
                return pd.to_datetime(dt_str, format='%m/%d  %H:%M:%S')
            except:
                return pd.NaT
        
        df['DateTime'] = df['Date/Time'].apply(parse_datetime)
        df = df.dropna(subset=['DateTime'])
        df['Month'] = df['DateTime'].dt.month
        df['Hour'] = df['DateTime'].dt.hour
        
        elec_col = 'Electricity:Facility [kW](Hourly)'
        
        # Monthly aggregation
        monthly_data = []
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        for month in range(1, 13):
            month_df = df[df['Month'] == month]
            if len(month_df) == 0:
                continue
                
            monthly_kwh = month_df[elec_col].sum()
            peak_kw = month_df[elec_col].max()
            avg_kw = month_df[elec_col].mean()
            days_in_month = len(month_df) / 24
            
            monthly_data.append({
                'Profile_Type': 'Residential',
                'Scenario': scenario,
                'Location': location.replace('_', ' ').title(),
                'Month': month_names[month - 1],
                'Month_Number': month,
                'Energy_Consumption_kWh': round(monthly_kwh, 1),
                'Peak_Demand_kW': round(peak_kw, 2),
                'Average_Demand_kW': round(avg_kw, 2),
                'Load_Factor': round(avg_kw / peak_kw, 3) if peak_kw > 0 else 0,
                'Days_in_Month': int(days_in_month),
                'Data_Source': 'EnergyPlus Residential Prototype, Louisiana TMY3',
                'Weather_Station': loc_code,
                'Climate_Zone': '2A (Hot-Humid)',
            })
        
        # Add annual summary
        annual_kwh = df[elec_col].sum()
        annual_peak = df[elec_col].max()
        annual_avg = df[elec_col].mean()
        
        monthly_data.append({
            'Profile_Type': 'Residential',
            'Scenario': scenario,
            'Location': location.replace('_', ' ').title(),
            'Month': 'ANNUAL',
            'Month_Number': 0,
            'Energy_Consumption_kWh': round(annual_kwh, 0),
            'Peak_Demand_kW': round(annual_peak, 2),
            'Average_Demand_kW': round(annual_avg, 2),
            'Load_Factor': round(annual_avg / annual_peak, 3) if annual_peak > 0 else 0,
            'Days_in_Month': 365,
            'Data_Source': 'EnergyPlus Residential Prototype, Louisiana TMY3',
            'Weather_Station': loc_code,
            'Climate_Zone': '2A (Hot-Humid)',
        })
        
        logger.info(f"✓ Loaded residential profile: {annual_kwh:,.0f} kWh/year, {annual_peak:.1f} kW peak")
        
        return monthly_data
    
    def _get_residential_fallback(self, location: str, scenario: str) -> List[Dict]:
        """Fallback residential data based on actual EnergyPlus results"""
        
        # Real data from Baton Rouge EnergyPlus simulations
        scenarios = {
            'BASE': {'annual_kwh': 14936, 'peak_kw': 7.32, 'avg_kw': 1.71},
            'HIGH': {'annual_kwh': 27066, 'peak_kw': 10.96, 'avg_kw': 3.09},
            'LOW': {'annual_kwh': 7093, 'peak_kw': 2.96, 'avg_kw': 0.81},
        }
        
        data = scenarios.get(scenario, scenarios['BASE'])
        
        return [{
            'Profile_Type': 'Residential',
            'Scenario': scenario,
            'Location': location.replace('_', ' ').title(),
            'Month': 'ANNUAL',
            'Month_Number': 0,
            'Energy_Consumption_kWh': data['annual_kwh'],
            'Peak_Demand_kW': data['peak_kw'],
            'Average_Demand_kW': data['avg_kw'],
            'Load_Factor': round(data['avg_kw'] / data['peak_kw'], 3),
            'Days_in_Month': 365,
            'Data_Source': 'EnergyPlus Residential Prototype (Fallback)',
            'Weather_Station': 'USA_LA_Baton.Rouge-Ryan.AP.722317_TMY3',
            'Climate_Zone': '2A (Hot-Humid)',
        }]
    
    def get_commercial_profile(self, building_type: str = 'medium_office',
                                location: str = 'baton_rouge') -> List[Dict]:
        """
        Get commercial building load profile from EnergyPlus data
        
        Args:
            building_type: Building type key (e.g., 'medium_office', 'hospital')
            location: Louisiana location key
            
        Returns:
            List of monthly summary dictionaries
        """
        
        logger.info(f"Loading commercial profile: {building_type}, {location}...")
        
        if building_type not in self.BUILDING_TYPES:
            logger.warning(f"Unknown building type: {building_type}")
            building_type = 'medium_office'
        
        bldg_prefix, bldg_name, sq_ft = self.BUILDING_TYPES[building_type]
        loc_code = self.LA_LOCATIONS.get(location, self.LA_LOCATIONS['baton_rouge'])
        
        # Find the CSV file
        loc_dir = self.commercial_path / loc_code
        if not loc_dir.exists():
            logger.warning(f"Location directory not found: {loc_dir}")
            return self._get_commercial_fallback(building_type, location)
        
        # Find matching file
        matching_files = list(loc_dir.glob(f"{bldg_prefix}*.csv"))
        if not matching_files:
            logger.warning(f"No files found for {bldg_prefix} in {loc_dir}")
            return self._get_commercial_fallback(building_type, location)
        
        filepath = matching_files[0]
        df = self._load_csv(filepath)
        if df is None:
            return self._get_commercial_fallback(building_type, location)
        
        # Parse date/time - handle 24:00:00 timestamps
        def parse_datetime(dt_str):
            dt_str = dt_str.strip()
            if '24:00:00' in dt_str:
                dt_str = dt_str.replace('24:00:00', '00:00:00')
            try:
                return pd.to_datetime(dt_str, format='%m/%d  %H:%M:%S')
            except:
                return pd.NaT
        
        df['DateTime'] = df['Date/Time'].apply(parse_datetime)
        df = df.dropna(subset=['DateTime'])
        df['Month'] = df['DateTime'].dt.month
        
        elec_col = 'Electricity:Facility [kW](Hourly)'
        
        # Monthly aggregation
        monthly_data = []
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        for month in range(1, 13):
            month_df = df[df['Month'] == month]
            if len(month_df) == 0:
                continue
                
            monthly_kwh = month_df[elec_col].sum()
            peak_kw = month_df[elec_col].max()
            avg_kw = month_df[elec_col].mean()
            days_in_month = len(month_df) / 24
            
            monthly_data.append({
                'Profile_Type': 'Commercial',
                'Building_Type': bldg_name,
                'Building_SqFt': sq_ft,
                'Location': location.replace('_', ' ').title(),
                'Month': month_names[month - 1],
                'Month_Number': month,
                'Energy_Consumption_kWh': round(monthly_kwh, 0),
                'Peak_Demand_kW': round(peak_kw, 1),
                'Average_Demand_kW': round(avg_kw, 1),
                'Load_Factor': round(avg_kw / peak_kw, 3) if peak_kw > 0 else 0,
                'EUI_kWh_per_sqft': round(monthly_kwh / sq_ft, 2),
                'Data_Source': 'EnergyPlus DOE Commercial Reference Building',
                'Weather_Station': loc_code,
                'Climate_Zone': '2A (Hot-Humid)',
            })
        
        # Add annual summary
        annual_kwh = df[elec_col].sum()
        annual_peak = df[elec_col].max()
        annual_avg = df[elec_col].mean()
        
        monthly_data.append({
            'Profile_Type': 'Commercial',
            'Building_Type': bldg_name,
            'Building_SqFt': sq_ft,
            'Location': location.replace('_', ' ').title(),
            'Month': 'ANNUAL',
            'Month_Number': 0,
            'Energy_Consumption_kWh': round(annual_kwh, 0),
            'Peak_Demand_kW': round(annual_peak, 1),
            'Average_Demand_kW': round(annual_avg, 1),
            'Load_Factor': round(annual_avg / annual_peak, 3) if annual_peak > 0 else 0,
            'EUI_kWh_per_sqft': round(annual_kwh / sq_ft, 2),
            'Data_Source': 'EnergyPlus DOE Commercial Reference Building',
            'Weather_Station': loc_code,
            'Climate_Zone': '2A (Hot-Humid)',
        })
        
        logger.info(f"✓ Loaded {bldg_name}: {annual_kwh:,.0f} kWh/year, {annual_peak:.1f} kW peak")
        
        return monthly_data
    
    def _get_commercial_fallback(self, building_type: str, location: str) -> List[Dict]:
        """Fallback commercial data based on actual EnergyPlus results for Baton Rouge"""
        
        # Real data from Baton Rouge EnergyPlus simulations
        bldg_data = {
            'small_office': {'annual_kwh': 74745, 'peak_kw': 21.8, 'sq_ft': 5500},
            'medium_office': {'annual_kwh': 778212, 'peak_kw': 270.4, 'sq_ft': 53600},
            'large_office': {'annual_kwh': 7556429, 'peak_kw': 1901.2, 'sq_ft': 498600},
            'retail': {'annual_kwh': 390944, 'peak_kw': 129.2, 'sq_ft': 24690},
            'strip_mall': {'annual_kwh': 340505, 'peak_kw': 109.9, 'sq_ft': 22500},
            'supermarket': {'annual_kwh': 1890154, 'peak_kw': 408.5, 'sq_ft': 45000},
            'primary_school': {'annual_kwh': 1034185, 'peak_kw': 385.6, 'sq_ft': 73960},
            'secondary_school': {'annual_kwh': 4487816, 'peak_kw': 1387.2, 'sq_ft': 210900},
            'hospital': {'annual_kwh': 10459200, 'peak_kw': 1594.0, 'sq_ft': 241350},
            'outpatient': {'annual_kwh': 1459228, 'peak_kw': 340.6, 'sq_ft': 40950},
            'small_hotel': {'annual_kwh': 660331, 'peak_kw': 146.6, 'sq_ft': 43200},
            'large_hotel': {'annual_kwh': 2637460, 'peak_kw': 471.6, 'sq_ft': 122100},
            'warehouse': {'annual_kwh': 272468, 'peak_kw': 106.4, 'sq_ft': 52050},
            'quick_restaurant': {'annual_kwh': 208267, 'peak_kw': 41.8, 'sq_ft': 2500},
            'full_restaurant': {'annual_kwh': 353910, 'peak_kw': 73.5, 'sq_ft': 5500},
            'apartment': {'annual_kwh': 278925, 'peak_kw': 73.6, 'sq_ft': 33700},
        }
        
        data = bldg_data.get(building_type, bldg_data['medium_office'])
        bldg_name = self.BUILDING_TYPES.get(building_type, ('', 'Medium Office', 53600))[1]
        
        return [{
            'Profile_Type': 'Commercial',
            'Building_Type': bldg_name,
            'Building_SqFt': data['sq_ft'],
            'Location': location.replace('_', ' ').title(),
            'Month': 'ANNUAL',
            'Month_Number': 0,
            'Energy_Consumption_kWh': data['annual_kwh'],
            'Peak_Demand_kW': data['peak_kw'],
            'Average_Demand_kW': round(data['annual_kwh'] / 8760, 1),
            'Load_Factor': round((data['annual_kwh'] / 8760) / data['peak_kw'], 3),
            'EUI_kWh_per_sqft': round(data['annual_kwh'] / data['sq_ft'], 2),
            'Data_Source': 'EnergyPlus DOE Commercial Reference Building (Fallback)',
            'Weather_Station': 'USA_LA_Baton.Rouge-Ryan.AP.722317_TMY3',
            'Climate_Zone': '2A (Hot-Humid)',
        }]
    
    def get_hourly_profile(self, building_type: str = 'medium_office',
                           location: str = 'baton_rouge',
                           month: int = 7) -> List[Dict]:
        """
        Get typical hourly load pattern for a specific month
        
        Args:
            building_type: Building type key
            location: Louisiana location key
            month: Month number (1-12), default July (peak summer)
            
        Returns:
            List of 24 hourly load dictionaries
        """
        
        logger.info(f"Loading hourly profile: {building_type}, {location}, month {month}...")
        
        bldg_prefix, bldg_name, sq_ft = self.BUILDING_TYPES.get(
            building_type, self.BUILDING_TYPES['medium_office']
        )
        loc_code = self.LA_LOCATIONS.get(location, self.LA_LOCATIONS['baton_rouge'])
        
        # Find and load the file
        loc_dir = self.commercial_path / loc_code
        matching_files = list(loc_dir.glob(f"{bldg_prefix}*.csv")) if loc_dir.exists() else []
        
        if not matching_files:
            return self._get_hourly_fallback(building_type, month)
        
        df = self._load_csv(matching_files[0])
        if df is None:
            return self._get_hourly_fallback(building_type, month)
        
        # Parse and filter - handle 24:00:00 timestamps
        def parse_datetime(dt_str):
            dt_str = dt_str.strip()
            if '24:00:00' in dt_str:
                dt_str = dt_str.replace('24:00:00', '00:00:00')
            try:
                return pd.to_datetime(dt_str, format='%m/%d  %H:%M:%S')
            except:
                return pd.NaT
        
        df['DateTime'] = df['Date/Time'].apply(parse_datetime)
        df = df.dropna(subset=['DateTime'])
        df['Month'] = df['DateTime'].dt.month
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.dayofweek
        
        month_df = df[df['Month'] == month]
        elec_col = 'Electricity:Facility [kW](Hourly)'
        
        # Calculate average hourly profile for weekdays
        weekday_df = month_df[month_df['DayOfWeek'] < 5]
        hourly_avg = weekday_df.groupby('Hour')[elec_col].mean()
        peak_kw = hourly_avg.max()
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        hourly_data = []
        for hour in range(24):
            avg_kw = hourly_avg.get(hour, 0)
            load_factor = avg_kw / peak_kw if peak_kw > 0 else 0
            
            hourly_data.append({
                'Profile_Type': 'Hourly',
                'Building_Type': bldg_name,
                'Location': location.replace('_', ' ').title(),
                'Month': month_names[month - 1],
                'Hour': hour,
                'Time': f"{hour:02d}:00",
                'Average_Demand_kW': round(avg_kw, 1),
                'Load_Factor': round(load_factor, 3),
                'Period': self._get_hour_description(hour),
                'Day_Type': 'Weekday',
                'Data_Source': 'EnergyPlus DOE Commercial Reference Building',
            })
        
        logger.info(f"✓ Generated 24-hour profile for {bldg_name}, {month_names[month-1]}")
        
        return hourly_data
    
    def _get_hourly_fallback(self, building_type: str, month: int) -> List[Dict]:
        """Fallback hourly pattern based on typical commercial building"""
        
        # Typical office building hourly factors
        hourly_factors = {
            0: 0.40, 1: 0.38, 2: 0.36, 3: 0.36, 4: 0.38, 5: 0.45,
            6: 0.58, 7: 0.75, 8: 0.88, 9: 0.95, 10: 0.98, 11: 1.00,
            12: 0.98, 13: 0.96, 14: 0.97, 15: 0.95, 16: 0.90, 17: 0.80,
            18: 0.65, 19: 0.52, 20: 0.48, 21: 0.45, 22: 0.43, 23: 0.41
        }
        
        bldg_name = self.BUILDING_TYPES.get(building_type, ('', 'Medium Office', 53600))[1]
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        return [{
            'Profile_Type': 'Hourly',
            'Building_Type': bldg_name,
            'Location': 'Baton Rouge',
            'Month': month_names[month - 1],
            'Hour': hour,
            'Time': f"{hour:02d}:00",
            'Average_Demand_kW': 0,  # Placeholder
            'Load_Factor': round(factor, 3),
            'Period': self._get_hour_description(hour),
            'Day_Type': 'Weekday',
            'Data_Source': 'Typical Commercial Pattern (Fallback)',
        } for hour, factor in hourly_factors.items()]
    
    def _get_hour_description(self, hour: int) -> str:
        """Get description for hour of day"""
        if 0 <= hour < 6:
            return "Off-hours (minimal baseload)"
        elif 6 <= hour < 8:
            return "Morning ramp-up (HVAC pre-cooling)"
        elif 8 <= hour < 12:
            return "Morning business hours"
        elif 12 <= hour < 14:
            return "Mid-day peak"
        elif 14 <= hour < 18:
            return "Afternoon business hours"
        elif 18 <= hour < 22:
            return "Evening ramp-down"
        else:
            return "Night (baseload)"
    
    def get_all_commercial_summary(self, location: str = 'baton_rouge') -> List[Dict]:
        """
        Get annual summary for all commercial building types
        
        Args:
            location: Louisiana location key
            
        Returns:
            List of annual summaries for all 16 building types
        """
        
        logger.info(f"Loading all commercial building summaries for {location}...")
        
        summaries = []
        for bldg_key in self.BUILDING_TYPES.keys():
            profile = self.get_commercial_profile(bldg_key, location)
            # Get annual summary (last item)
            annual = [p for p in profile if p.get('Month') == 'ANNUAL']
            if annual:
                summaries.append(annual[0])
        
        logger.info(f"✓ Loaded {len(summaries)} commercial building summaries")
        
        return summaries
    
    def get_all_residential_summary(self, location: str = 'baton_rouge') -> List[Dict]:
        """
        Get annual summary for all residential scenarios
        
        Args:
            location: Louisiana location key
            
        Returns:
            List of annual summaries for BASE, HIGH, LOW scenarios
        """
        
        logger.info(f"Loading all residential scenarios for {location}...")
        
        summaries = []
        for scenario in ['BASE', 'HIGH', 'LOW']:
            profile = self.get_residential_profile(location, scenario)
            # Get annual summary (last item)
            annual = [p for p in profile if p.get('Month') == 'ANNUAL']
            if annual:
                summaries.append(annual[0])
        
        logger.info(f"✓ Loaded {len(summaries)} residential scenario summaries")
        
        return summaries
    
    def collect_all(self, location: str = 'baton_rouge') -> List[Dict]:
        """
        Collect all load profile data for a location
        
        Args:
            location: Louisiana location key
            
        Returns:
            List of all load profile dictionaries
        """
        
        logger.info(f"Starting comprehensive load profiles collection for {location}...")
        
        all_profiles = []
        
        # Collect all residential scenarios
        for scenario in ['BASE', 'HIGH', 'LOW']:
            all_profiles.extend(self.get_residential_profile(location, scenario))
        
        # Collect all commercial building types
        for bldg_key in self.BUILDING_TYPES.keys():
            all_profiles.extend(self.get_commercial_profile(bldg_key, location))
        
        # Add hourly profiles for key building types (summer peak)
        for bldg_key in ['medium_office', 'hospital', 'retail']:
            all_profiles.extend(self.get_hourly_profile(bldg_key, location, month=7))
        
        logger.info(f"✓ Total load profile records collected: {len(all_profiles)}")
        
        return all_profiles
    
    def save_to_csv(self, profiles: List[Dict], output_file: str) -> str:
        """
        Save load profiles to CSV file
        
        Args:
            profiles: List of profile dictionaries
            output_file: Output filename
            
        Returns:
            Path to saved file
        """
        
        output_path = self.output_dir / output_file
        df = pd.DataFrame(profiles)
        df.to_csv(output_path, index=False)
        
        logger.info(f"✓ Saved {len(profiles)} load profile records to {output_path}")
        
        return str(output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    collector = LoadProfilesCollector()
    
    print("="*80)
    print("LOUISIANA LOAD PROFILES COLLECTOR")
    print("="*80)
    
    # Test residential profiles
    print("\n--- Residential Profiles (Baton Rouge) ---")
    for scenario in ['BASE', 'HIGH', 'LOW']:
        profile = collector.get_residential_profile('baton_rouge', scenario)
        annual = [p for p in profile if p.get('Month') == 'ANNUAL'][0]
        print(f"{scenario}: {annual['Energy_Consumption_kWh']:,.0f} kWh/year, "
              f"{annual['Peak_Demand_kW']:.1f} kW peak")
    
    # Test commercial profiles
    print("\n--- Commercial Profiles (Baton Rouge) ---")
    summaries = collector.get_all_commercial_summary('baton_rouge')
    for s in sorted(summaries, key=lambda x: x['Energy_Consumption_kWh'], reverse=True)[:5]:
        print(f"{s['Building_Type']:25} | {s['Energy_Consumption_kWh']:>12,.0f} kWh | "
              f"{s['Peak_Demand_kW']:>8.1f} kW | LF: {s['Load_Factor']:.2f}")
    
    # Collect all and save
    print("\n--- Collecting All Profiles ---")
    all_profiles = collector.collect_all('baton_rouge')
    output_file = collector.save_to_csv(all_profiles, 'louisiana_load_profiles.csv')
    
    print(f"\nSaved to: {output_file}")
    print(f"Total records: {len(all_profiles)}")
