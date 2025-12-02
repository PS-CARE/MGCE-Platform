"""
MGCE Platform - FastAPI Backend
Microgrid Cost Estimator API

Provides endpoints for:
- Load analysis and system sizing
- Component cost estimation
- Financial analysis (LCOE, NPV, payback)
- Reliability assessment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from pathlib import Path
import json

app = FastAPI(
    title="MGCE Platform API",
    description="Microgrid Cost Estimator - Louisiana Focused",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
DATA_DIR = Path(__file__).parent.parent / "collected_data"

# Load data files
def load_data():
    """Load all collected data files"""
    data = {}
    
    try:
        data['component_costs'] = pd.read_csv(DATA_DIR / "component_costs_collected.csv", encoding='utf-8')
        data['solar_resource'] = pd.read_csv(DATA_DIR / "site_info_collected.csv", encoding='utf-8')
        data['financial_params'] = pd.read_csv(DATA_DIR / "financial_parameters_collected.csv", encoding='utf-8')
        data['utility_rates'] = pd.read_csv(DATA_DIR / "utility_rates.csv", encoding='utf-8')
        data['load_profiles'] = pd.read_csv(DATA_DIR / "load_profiles.csv", encoding='utf-8')
        data['reliability'] = pd.read_csv(DATA_DIR / "reliability_requirements.csv", encoding='utf-8')
        data['tou_rates'] = pd.read_csv(DATA_DIR / "tou_rates.csv", encoding='utf-8')
        data['la_incentives'] = pd.read_csv(DATA_DIR / "louisiana_incentives_interconnection.csv", encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not load some data files: {e}")
    
    return data

DATA = load_data()

# ============== Pydantic Models ==============

class FacilityInput(BaseModel):
    """User input for facility information"""
    facility_name: str = Field(..., description="Name of the facility")
    facility_type: str = Field(..., description="Type: commercial, industrial, residential, hospital, etc.")
    location: str = Field(default="baton_rouge", description="Louisiana location")
    peak_demand_kw: float = Field(..., gt=0, description="Peak electrical demand in kW")
    annual_consumption_kwh: float = Field(..., gt=0, description="Annual energy consumption in kWh")
    critical_load_percent: float = Field(default=30, ge=0, le=100, description="Percentage of load that is critical")
    essential_load_percent: float = Field(default=40, ge=0, le=100, description="Percentage of load that is essential")
    backup_duration_hours: float = Field(default=24, gt=0, description="Required backup duration in hours")
    grid_connected: bool = Field(default=True, description="Whether microgrid is grid-connected")
    include_solar: bool = Field(default=True, description="Include solar PV in design")
    include_battery: bool = Field(default=True, description="Include battery storage in design")
    include_generator: bool = Field(default=True, description="Include backup generator in design")

class MicrogridDesign(BaseModel):
    """Microgrid system design output"""
    solar_pv_kw: float
    battery_kw: float
    battery_kwh: float
    generator_kw: float
    inverter_kw: float
    total_generation_kw: float
    renewable_fraction: float
    critical_load_coverage: float

class CostEstimate(BaseModel):
    """Cost estimation output"""
    solar_pv_cost: float
    battery_cost: float
    generator_cost: float
    inverter_cost: float
    bos_cost: float
    installation_cost: float
    total_capital_cost: float
    annual_om_cost: float
    cost_per_kw: float

class FinancialAnalysis(BaseModel):
    """Financial analysis output"""
    lcoe: float
    simple_payback_years: float
    npv: float
    irr: float
    annual_savings: float
    federal_itc: float
    total_incentives: float
    net_cost_after_incentives: float

class ReliabilityAssessment(BaseModel):
    """Reliability assessment output"""
    backup_duration_hours: float
    critical_load_coverage_percent: float
    expected_outage_hours_per_year: float
    avoided_outage_cost: float
    reliability_improvement_percent: float

class FullAnalysisResult(BaseModel):
    """Complete analysis result"""
    facility: Dict[str, Any]
    design: MicrogridDesign
    costs: CostEstimate
    financial: FinancialAnalysis
    reliability: ReliabilityAssessment
    recommendations: List[str]

# ============== Calculation Engines ==============

class LoadAnalyzer:
    """Load analysis and system sizing calculations"""
    
    def __init__(self, data: dict):
        self.data = data
    
    def analyze_load(self, facility: FacilityInput) -> dict:
        """Analyze facility load and determine sizing requirements"""
        
        # Calculate load breakdown
        critical_load_kw = facility.peak_demand_kw * (facility.critical_load_percent / 100)
        essential_load_kw = facility.peak_demand_kw * (facility.essential_load_percent / 100)
        non_critical_load_kw = facility.peak_demand_kw - critical_load_kw - essential_load_kw
        
        # Calculate load factor
        hours_per_year = 8760
        load_factor = facility.annual_consumption_kwh / (facility.peak_demand_kw * hours_per_year)
        
        # Average demand
        avg_demand_kw = facility.annual_consumption_kwh / hours_per_year
        
        # Backup load (critical + essential)
        backup_load_kw = critical_load_kw + essential_load_kw
        
        return {
            'peak_demand_kw': facility.peak_demand_kw,
            'average_demand_kw': round(avg_demand_kw, 2),
            'critical_load_kw': round(critical_load_kw, 2),
            'essential_load_kw': round(essential_load_kw, 2),
            'non_critical_load_kw': round(non_critical_load_kw, 2),
            'backup_load_kw': round(backup_load_kw, 2),
            'load_factor': round(load_factor, 3),
            'annual_consumption_kwh': facility.annual_consumption_kwh,
        }


class SystemSizer:
    """Microgrid component sizing calculations"""
    
    def __init__(self, data: dict):
        self.data = data
        # Louisiana solar capacity factor from collected data
        self.solar_capacity_factor = 0.269  # 26.9% from NREL ATB 2024
        self.battery_round_trip_efficiency = 0.85
        self.generator_efficiency = 0.35
    
    def size_system(self, facility: FacilityInput, load_analysis: dict) -> MicrogridDesign:
        """Size microgrid components based on load analysis"""
        
        backup_load_kw = load_analysis['backup_load_kw']
        critical_load_kw = load_analysis['critical_load_kw']
        
        # Solar PV sizing
        if facility.include_solar:
            # Size PV to cover average demand with 1.3x factor for battery charging
            solar_pv_kw = round(load_analysis['average_demand_kw'] * 1.3 / self.solar_capacity_factor, 1)
            # Cap at reasonable size relative to peak demand
            solar_pv_kw = min(solar_pv_kw, facility.peak_demand_kw * 1.5)
        else:
            solar_pv_kw = 0
        
        # Battery sizing
        if facility.include_battery:
            # Size battery for 4 hours of backup load (typical for commercial)
            battery_hours = min(4, facility.backup_duration_hours)
            battery_kwh = round(backup_load_kw * battery_hours / self.battery_round_trip_efficiency, 1)
            battery_kw = round(backup_load_kw * 1.1, 1)  # 10% margin
        else:
            battery_kw = 0
            battery_kwh = 0
        
        # Generator sizing (for extended outages)
        if facility.include_generator:
            # Size generator to cover critical + essential loads
            generator_kw = round(backup_load_kw * 1.2, 1)  # 20% margin
        else:
            generator_kw = 0
        
        # Inverter sizing
        inverter_kw = round(max(solar_pv_kw, battery_kw, backup_load_kw) * 1.1, 1)
        
        # Total generation capacity
        total_generation_kw = solar_pv_kw + generator_kw
        
        # Renewable fraction
        if total_generation_kw > 0:
            renewable_fraction = round(solar_pv_kw / total_generation_kw, 3)
        else:
            renewable_fraction = 0
        
        # Critical load coverage
        critical_load_coverage = min(1.0, (battery_kw + generator_kw) / critical_load_kw) if critical_load_kw > 0 else 1.0
        
        return MicrogridDesign(
            solar_pv_kw=solar_pv_kw,
            battery_kw=battery_kw,
            battery_kwh=battery_kwh,
            generator_kw=generator_kw,
            inverter_kw=inverter_kw,
            total_generation_kw=round(total_generation_kw, 1),
            renewable_fraction=round(renewable_fraction, 3),
            critical_load_coverage=round(critical_load_coverage, 3)
        )


class CostEstimator:
    """Component cost estimation using NREL ATB 2024 data"""
    
    def __init__(self, data: dict):
        self.data = data
        self.load_cost_data()
    
    def load_cost_data(self):
        """Load cost data from collected files"""
        try:
            costs_df = self.data.get('component_costs', pd.DataFrame())
            self.costs = {}
            for _, row in costs_df.iterrows():
                component = row.get('Component', '')
                self.costs[component] = {
                    'unit_cost': row.get('Unit_Cost', 0),
                    'installation_cost': row.get('Installation_Cost_Per_Unit', 0),
                    'lifespan': row.get('Lifespan_Years', 25)
                }
        except Exception as e:
            print(f"Error loading cost data: {e}")
            self.costs = {}
        
        # Default costs from NREL ATB 2024 if not loaded
        self.default_costs = {
            'solar_pv_per_kw': 1551,  # $/kW AC (NREL ATB 2024)
            'battery_per_kwh': 485,   # $/kWh (4-hour system)
            'battery_per_kw': 1938,   # $/kW
            'generator_per_kw': 800,  # $/kW (diesel)
            'inverter_per_kw': 150,   # $/kW
            'bos_percent': 0.15,      # 15% of equipment cost
            'installation_percent': 0.20,  # 20% of equipment cost
            'om_percent': 0.015,      # 1.5% of capital annually
        }
    
    def estimate_costs(self, design: MicrogridDesign) -> CostEstimate:
        """Estimate costs for microgrid design"""
        
        # Component costs
        solar_pv_cost = design.solar_pv_kw * self.default_costs['solar_pv_per_kw']
        battery_cost = design.battery_kwh * self.default_costs['battery_per_kwh']
        generator_cost = design.generator_kw * self.default_costs['generator_per_kw']
        inverter_cost = design.inverter_kw * self.default_costs['inverter_per_kw']
        
        # Equipment subtotal
        equipment_cost = solar_pv_cost + battery_cost + generator_cost + inverter_cost
        
        # BOS and installation
        bos_cost = equipment_cost * self.default_costs['bos_percent']
        installation_cost = equipment_cost * self.default_costs['installation_percent']
        
        # Total capital cost
        total_capital_cost = equipment_cost + bos_cost + installation_cost
        
        # Annual O&M
        annual_om_cost = total_capital_cost * self.default_costs['om_percent']
        
        # Cost per kW
        total_capacity = design.solar_pv_kw + design.generator_kw
        cost_per_kw = total_capital_cost / total_capacity if total_capacity > 0 else 0
        
        return CostEstimate(
            solar_pv_cost=round(solar_pv_cost, 2),
            battery_cost=round(battery_cost, 2),
            generator_cost=round(generator_cost, 2),
            inverter_cost=round(inverter_cost, 2),
            bos_cost=round(bos_cost, 2),
            installation_cost=round(installation_cost, 2),
            total_capital_cost=round(total_capital_cost, 2),
            annual_om_cost=round(annual_om_cost, 2),
            cost_per_kw=round(cost_per_kw, 2)
        )


class FinancialAnalyzer:
    """Financial analysis including LCOE, NPV, payback, TOU arbitrage"""
    
    def __init__(self, data: dict):
        self.data = data
        self.load_financial_params()
        self.load_tou_rates()
        self.load_la_incentives()
    
    def load_financial_params(self):
        """Load financial parameters from collected data"""
        try:
            params_df = self.data.get('financial_params', pd.DataFrame())
            self.params = {}
            for _, row in params_df.iterrows():
                param = row.get('Parameter', '')
                self.params[param] = row.get('Value', 0)
        except Exception as e:
            print(f"Error loading financial params: {e}")
            self.params = {}
        
        # Default financial parameters
        self.default_params = {
            'federal_itc_rate': 0.30,  # 30% ITC
            'discount_rate': 0.06,     # 6% discount rate
            'inflation_rate': 0.025,   # 2.5% inflation
            'electricity_rate': 0.0945,  # $/kWh (Entergy LA)
            'electricity_escalation': 0.02,  # 2% annual increase
            'project_lifetime': 25,    # years
        }
    
    def load_tou_rates(self):
        """Load TOU rates from collected data"""
        # TOU rates from Entergy Louisiana HLFS-TOD-G
        self.tou_rates = {
            'summer_on_peak': 0.02554,   # $/kWh (1pm-9pm M-F, May-Oct)
            'summer_off_peak': 0.00607,  # $/kWh
            'winter_on_peak': 0.00746,   # $/kWh (6am-10am, 6pm-10pm M-F, Nov-Apr)
            'winter_off_peak': 0.00607,  # $/kWh
            'summer_demand': 16.13,      # $/kW-month
            'winter_demand': 14.50,      # $/kW-month
            'export_credit': 0.0259,     # $/kWh (avoided cost)
            'summer_peak_hours': 8,      # hours/weekday
            'winter_peak_hours': 8,      # hours/weekday
            'peak_days_per_month': 22,   # weekdays
        }
    
    def load_la_incentives(self):
        """Load Louisiana incentives from collected data"""
        # Louisiana incentives (as of 2025)
        self.la_incentives = {
            'state_tax_credit': 0.0,     # No state tax credit
            'property_tax_exempt': True,  # 100% property tax exemption
            'sales_tax_exempt': False,    # No sales tax exemption
            'sales_tax_rate': 0.0945,     # 9.45% total sales tax
            'net_billing_rate': 0.026,    # $/kWh export credit
            'interconnection_fee_residential': 50,  # $
            'interconnection_fee_commercial': 75,   # $
            'permit_fee_min': 50,         # $
            'permit_fee_max': 500,        # $
        }
    
    def calculate_arbitrage_savings(self, design: MicrogridDesign) -> float:
        """Calculate annual TOU arbitrage savings from battery"""
        if design.battery_kwh <= 0:
            return 0
        
        # Summer arbitrage (6 months, May-Oct)
        summer_spread = self.tou_rates['summer_on_peak'] - self.tou_rates['summer_off_peak']
        battery_efficiency = 0.85  # Round-trip efficiency
        summer_cycles = self.tou_rates['peak_days_per_month'] * 6  # ~132 cycles
        summer_arbitrage = design.battery_kwh * summer_spread * battery_efficiency * summer_cycles
        
        # Winter arbitrage (6 months, Nov-Apr) - much lower spread
        winter_spread = self.tou_rates['winter_on_peak'] - self.tou_rates['winter_off_peak']
        winter_cycles = self.tou_rates['peak_days_per_month'] * 6  # ~132 cycles
        winter_arbitrage = design.battery_kwh * winter_spread * battery_efficiency * winter_cycles
        
        return summer_arbitrage + winter_arbitrage
    
    def calculate_demand_charge_savings(self, design: MicrogridDesign) -> float:
        """Calculate annual demand charge savings from battery peak shaving"""
        if design.battery_kw <= 0:
            return 0
        
        # Assume battery can reduce peak by 80% of its capacity
        peak_reduction_kw = design.battery_kw * 0.8
        
        # Summer demand savings (6 months)
        summer_savings = peak_reduction_kw * self.tou_rates['summer_demand'] * 6
        
        # Winter demand savings (6 months)
        winter_savings = peak_reduction_kw * self.tou_rates['winter_demand'] * 6
        
        return summer_savings + winter_savings
    
    def analyze_financials(self, facility: FacilityInput, design: MicrogridDesign, 
                          costs: CostEstimate) -> FinancialAnalysis:
        """Perform financial analysis with TOU arbitrage"""
        
        # Federal ITC (30% for solar + storage)
        eligible_cost = costs.solar_pv_cost + costs.battery_cost
        federal_itc = eligible_cost * self.default_params['federal_itc_rate']
        
        # Louisiana has no state tax credit (add interconnection/permit costs)
        interconnection_cost = self.la_incentives['interconnection_fee_commercial']
        permit_cost = (self.la_incentives['permit_fee_min'] + self.la_incentives['permit_fee_max']) / 2
        
        # Total incentives (federal only for Louisiana)
        total_incentives = federal_itc
        
        # Net cost after incentives (add LA fees)
        net_cost = costs.total_capital_cost - total_incentives + interconnection_cost + permit_cost
        
        # Annual energy production (solar)
        solar_production_kwh = design.solar_pv_kw * 8760 * 0.269  # 26.9% capacity factor
        
        # Self-consumption savings (valued at retail rate)
        self_consumption_rate = 0.80  # Assume 80% self-consumption
        electricity_rate = self.default_params['electricity_rate']
        self_consumption_savings = solar_production_kwh * self_consumption_rate * electricity_rate
        
        # Export credits (valued at avoided cost - much lower)
        export_kwh = solar_production_kwh * (1 - self_consumption_rate)
        export_savings = export_kwh * self.tou_rates['export_credit']
        
        # TOU arbitrage savings from battery
        arbitrage_savings = self.calculate_arbitrage_savings(design)
        
        # Demand charge savings from battery peak shaving
        demand_savings = self.calculate_demand_charge_savings(design)
        
        # Total annual savings
        annual_savings = self_consumption_savings + export_savings + arbitrage_savings + demand_savings
        
        # Subtract O&M costs
        net_annual_savings = annual_savings - costs.annual_om_cost
        
        # Simple payback
        if net_annual_savings > 0:
            simple_payback = net_cost / net_annual_savings
        else:
            simple_payback = 999
        
        # LCOE calculation
        lifetime = self.default_params['project_lifetime']
        discount_rate = self.default_params['discount_rate']
        
        # Total lifetime energy
        total_energy = solar_production_kwh * lifetime
        
        # NPV of costs
        npv_costs = net_cost
        for year in range(1, lifetime + 1):
            npv_costs += costs.annual_om_cost / ((1 + discount_rate) ** year)
        
        # LCOE
        lcoe = npv_costs / total_energy if total_energy > 0 else 0
        
        # NPV calculation
        npv = -net_cost
        for year in range(1, lifetime + 1):
            annual_benefit = net_annual_savings * ((1 + self.default_params['electricity_escalation']) ** year)
            npv += annual_benefit / ((1 + discount_rate) ** year)
        
        # IRR approximation (simplified)
        irr = net_annual_savings / net_cost if net_cost > 0 else 0
        
        return FinancialAnalysis(
            lcoe=round(lcoe, 4),
            simple_payback_years=round(simple_payback, 1),
            npv=round(npv, 2),
            irr=round(irr * 100, 2),  # As percentage
            annual_savings=round(annual_savings, 2),
            federal_itc=round(federal_itc, 2),
            total_incentives=round(total_incentives, 2),
            net_cost_after_incentives=round(net_cost, 2)
        )


class ReliabilityAnalyzer:
    """Reliability and backup power assessment"""
    
    def __init__(self, data: dict):
        self.data = data
        self.load_reliability_data()
    
    def load_reliability_data(self):
        """Load reliability data from collected files"""
        # Louisiana reliability metrics from EIA Form 861
        self.la_metrics = {
            'saidi_with_med': 652.5,  # minutes/year
            'saifi_with_med': 2.495,  # interruptions/year
            'caidi_with_med': 261.5,  # minutes/interruption
            'saidi_without_med': 212.9,
            'caidi_without_med': 126.1,
        }
        
        # Interruption cost per kWh (DOE ICE Calculator)
        self.interruption_costs = {
            'commercial': 25.0,  # $/kWh
            'industrial': 15.0,
            'residential': 5.0,
            'hospital': 100.0,
        }
    
    def assess_reliability(self, facility: FacilityInput, design: MicrogridDesign,
                          load_analysis: dict) -> ReliabilityAssessment:
        """Assess reliability improvement from microgrid"""
        
        # Current expected outage hours
        expected_outage_hours = self.la_metrics['saidi_with_med'] / 60  # Convert to hours
        
        # Backup duration from battery + generator
        battery_hours = design.battery_kwh / load_analysis['backup_load_kw'] if load_analysis['backup_load_kw'] > 0 else 0
        generator_hours = 72 if design.generator_kw > 0 else 0  # Assume 72 hours fuel
        
        total_backup_hours = battery_hours + generator_hours
        
        # Critical load coverage
        critical_coverage = design.critical_load_coverage * 100
        
        # Avoided outage cost
        facility_type = facility.facility_type.lower()
        cost_per_kwh = self.interruption_costs.get(facility_type, 25.0)
        
        # Annual avoided outage cost
        avoided_energy = load_analysis['critical_load_kw'] * expected_outage_hours
        avoided_outage_cost = avoided_energy * cost_per_kwh * (critical_coverage / 100)
        
        # Reliability improvement
        if total_backup_hours >= expected_outage_hours:
            reliability_improvement = 95.0  # Near-complete coverage
        else:
            reliability_improvement = (total_backup_hours / expected_outage_hours) * 100
        
        return ReliabilityAssessment(
            backup_duration_hours=round(total_backup_hours, 1),
            critical_load_coverage_percent=round(critical_coverage, 1),
            expected_outage_hours_per_year=round(expected_outage_hours, 1),
            avoided_outage_cost=round(avoided_outage_cost, 2),
            reliability_improvement_percent=round(min(reliability_improvement, 99), 1)
        )


def generate_recommendations(facility: FacilityInput, design: MicrogridDesign,
                            costs: CostEstimate, financial: FinancialAnalysis,
                            reliability: ReliabilityAssessment) -> List[str]:
    """Generate recommendations based on analysis"""
    
    recommendations = []
    
    # Solar recommendations
    if design.solar_pv_kw > 0:
        recommendations.append(
            f"Install {design.solar_pv_kw:.0f} kW solar PV system to offset {design.renewable_fraction*100:.0f}% of generation with clean energy."
        )
    
    # Battery recommendations
    if design.battery_kwh > 0:
        recommendations.append(
            f"Deploy {design.battery_kwh:.0f} kWh battery storage for {design.battery_kwh/design.battery_kw:.1f} hours of backup power and demand charge management."
        )
    
    # Generator recommendations
    if design.generator_kw > 0:
        recommendations.append(
            f"Include {design.generator_kw:.0f} kW backup generator for extended outages during hurricane season (72+ hours)."
        )
    
    # Financial recommendations
    if financial.simple_payback_years < 10:
        recommendations.append(
            f"Project has attractive {financial.simple_payback_years:.1f}-year payback with ${financial.federal_itc:,.0f} federal tax credit."
        )
    
    if financial.npv > 0:
        recommendations.append(
            f"Positive NPV of ${financial.npv:,.0f} indicates strong financial viability over 25-year project life."
        )
    
    # Reliability recommendations
    if reliability.reliability_improvement_percent > 90:
        recommendations.append(
            f"Microgrid provides {reliability.reliability_improvement_percent:.0f}% reliability improvement, virtually eliminating outage impacts."
        )
    
    if reliability.avoided_outage_cost > 10000:
        recommendations.append(
            f"Estimated ${reliability.avoided_outage_cost:,.0f}/year in avoided outage costs justifies resilience investment."
        )
    
    # Louisiana-specific
    recommendations.append(
        "Consider grid-forming inverters for seamless islanding during Louisiana hurricane events."
    )
    
    return recommendations


# ============== API Endpoints ==============

@app.get("/")
async def root():
    return {
        "message": "MGCE Platform API",
        "version": "1.0.0",
        "endpoints": ["/analyze", "/component-costs", "/utility-rates", "/load-profiles"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "data_loaded": len(DATA) > 0}

@app.post("/analyze", response_model=FullAnalysisResult)
async def analyze_microgrid(facility: FacilityInput):
    """
    Perform complete microgrid analysis
    
    Returns system design, cost estimate, financial analysis, and reliability assessment
    """
    try:
        # Initialize analyzers
        load_analyzer = LoadAnalyzer(DATA)
        system_sizer = SystemSizer(DATA)
        cost_estimator = CostEstimator(DATA)
        financial_analyzer = FinancialAnalyzer(DATA)
        reliability_analyzer = ReliabilityAnalyzer(DATA)
        
        # Perform analysis
        load_analysis = load_analyzer.analyze_load(facility)
        design = system_sizer.size_system(facility, load_analysis)
        costs = cost_estimator.estimate_costs(design)
        financial = financial_analyzer.analyze_financials(facility, design, costs)
        reliability = reliability_analyzer.assess_reliability(facility, design, load_analysis)
        
        # Generate recommendations
        recommendations = generate_recommendations(facility, design, costs, financial, reliability)
        
        return FullAnalysisResult(
            facility=load_analysis,
            design=design,
            costs=costs,
            financial=financial,
            reliability=reliability,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/component-costs")
async def get_component_costs():
    """Get component cost data from NREL ATB 2024"""
    try:
        df = DATA.get('component_costs', pd.DataFrame())
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/utility-rates")
async def get_utility_rates():
    """Get Entergy Louisiana utility rate data"""
    try:
        df = DATA.get('utility_rates', pd.DataFrame())
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/load-profiles")
async def get_load_profiles(building_type: Optional[str] = None):
    """Get Louisiana load profile data"""
    try:
        df = DATA.get('load_profiles', pd.DataFrame())
        if building_type:
            df = df[df['Building_Type'].str.contains(building_type, case=False, na=False)]
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reliability-data")
async def get_reliability_data():
    """Get Louisiana reliability data from EIA Form 861"""
    try:
        df = DATA.get('reliability', pd.DataFrame())
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/financial-parameters")
async def get_financial_parameters():
    """Get financial parameters (tax credits, rates, etc.)"""
    try:
        df = DATA.get('financial_params', pd.DataFrame())
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/solar-resource")
async def get_solar_resource():
    """Get Louisiana solar resource data"""
    try:
        df = DATA.get('solar_resource', pd.DataFrame())
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tou-rates")
async def get_tou_rates():
    """Get Entergy Louisiana Time-of-Use rate data (HLFS-TOD-G)"""
    try:
        df = DATA.get('tou_rates', pd.DataFrame())
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tou-summary")
async def get_tou_summary():
    """Get TOU rate summary for quick reference"""
    return {
        "rate_schedule": "HLFS-TOD-G",
        "utility": "Entergy Louisiana",
        "summer": {
            "on_peak_rate": 0.02554,
            "off_peak_rate": 0.00607,
            "spread": 0.01947,
            "spread_percent": 321,
            "peak_hours": "1pm-9pm M-F (May 15 - Oct 15)",
            "demand_charge": 16.13
        },
        "winter": {
            "on_peak_rate": 0.00746,
            "off_peak_rate": 0.00607,
            "spread": 0.00139,
            "spread_percent": 23,
            "peak_hours": "6am-10am, 6pm-10pm M-F (Oct 16 - May 14)",
            "demand_charge": 14.50
        },
        "export_credit": 0.0259,
        "arbitrage_potential": "High in summer, limited in winter",
        "unit": "$/kWh"
    }

@app.get("/louisiana-incentives")
async def get_louisiana_incentives():
    """Get Louisiana state incentives and interconnection data"""
    try:
        df = DATA.get('la_incentives', pd.DataFrame())
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/louisiana-incentives-summary")
async def get_louisiana_incentives_summary():
    """Get Louisiana incentives summary for quick reference"""
    return {
        "state": "Louisiana",
        "tax_credits": {
            "state_solar_credit": {"available": False, "value": 0, "notes": "Expired, not renewed"},
            "federal_itc": {"available": True, "value": 30, "unit": "%", "expires": "2032"}
        },
        "exemptions": {
            "property_tax": {"available": True, "value": 100, "unit": "%"},
            "sales_tax": {"available": False, "rate": 9.45, "unit": "%"}
        },
        "net_billing": {
            "export_rate": 0.026,
            "unit": "$/kWh",
            "type": "Avoided cost (NOT retail rate)",
            "residential_limit": 25,
            "commercial_limit": 300,
            "limit_unit": "kW"
        },
        "interconnection": {
            "residential_fee": 50,
            "commercial_fee": 75,
            "permit_range": "50-500",
            "unit": "$",
            "study_required_above": 300,
            "study_unit": "kW"
        },
        "financing": {
            "help_program": {"available": True, "min": 6000, "max": 12000, "unit": "$"}
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
