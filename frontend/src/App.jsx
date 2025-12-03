import React, { useState } from 'react';
import { 
  Sun, Battery, Zap, DollarSign, Shield, Building2, 
  MapPin, Clock, TrendingUp, CheckCircle, AlertCircle,
  BarChart3, PieChart, Activity, FileText, Settings,
  ChevronDown, ChevronUp, Calculator, Info
} from 'lucide-react';

// API Configuration - uses environment variable for deployment
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// Facility Types
const FACILITY_TYPES = [
  { value: 'commercial', label: 'Commercial Office' },
  { value: 'industrial', label: 'Industrial Facility' },
  { value: 'hospital', label: 'Hospital/Healthcare' },
  { value: 'residential', label: 'Residential Complex' },
  { value: 'retail', label: 'Retail/Shopping' },
  { value: 'school', label: 'School/University' },
  { value: 'warehouse', label: 'Warehouse/Distribution' },
];

// Louisiana Locations
const LOCATIONS = [
  { value: 'baton_rouge', label: 'Baton Rouge' },
  { value: 'new_orleans', label: 'New Orleans' },
  { value: 'lafayette', label: 'Lafayette' },
  { value: 'shreveport', label: 'Shreveport' },
  { value: 'lake_charles', label: 'Lake Charles' },
  { value: 'monroe', label: 'Monroe' },
  { value: 'houma', label: 'Houma' },
  { value: 'alexandria', label: 'Alexandria' },
];

function App() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [showCalculations, setShowCalculations] = useState(false);
  
  const [validationErrors, setValidationErrors] = useState({});

  const [formData, setFormData] = useState({
    facility_name: '',
    facility_type: 'commercial',
    location: 'baton_rouge',
    peak_demand_kw: '',
    annual_consumption_kwh: '',
    critical_load_percent: '',
    essential_load_percent: '',
    backup_duration_hours: '',
    grid_connected: true,
    include_solar: true,
    include_battery: true,
    include_generator: true,
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    let newValue;
    if (type === 'checkbox') {
      newValue = checked;
    } else if (type === 'number') {
      // Handle empty string to avoid NaN
      newValue = value === '' ? '' : parseFloat(value);
    } else {
      newValue = value;
    }
    setFormData(prev => ({
      ...prev,
      [name]: newValue
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    const errors = {};
    if (!formData.critical_load_percent || formData.critical_load_percent <= 0) {
      errors.critical_load_percent = 'Critical Load % is required';
    }
    if (!formData.essential_load_percent || formData.essential_load_percent <= 0) {
      errors.essential_load_percent = 'Essential Load % is required';
    }
    
    setValidationErrors(errors);
    if (Object.keys(errors).length > 0) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    // Prepare data
    const submitData = {
      ...formData,
      facility_name: formData.facility_name || 'Unnamed Facility',
    };
    
    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });
      
      if (!response.ok) {
        throw new Error('Analysis failed. Please check your inputs.');
      }
      
      const data = await response.json();
      setResults(data);
      setStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value, decimals = 0) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">MGCE Platform</h1>
                <p className="text-sm text-gray-500">Microgrid Cost Estimator</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <MapPin className="h-4 w-4" />
              <span>Louisiana Focus</span>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center space-x-4 mb-8">
          {[
            { num: 1, label: 'Facility Info' },
            { num: 2, label: 'System Options' },
            { num: 3, label: 'Results' },
          ].map((s, idx) => (
            <React.Fragment key={s.num}>
              <div className={`flex items-center space-x-2 ${step >= s.num ? 'text-primary-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm
                  ${step >= s.num ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  {step > s.num ? <CheckCircle className="h-5 w-5" /> : s.num}
                </div>
                <span className="font-medium hidden sm:inline">{s.label}</span>
              </div>
              {idx < 2 && (
                <div className={`w-16 h-1 rounded ${step > s.num ? 'bg-primary-600' : 'bg-gray-200'}`} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Step 1: Facility Information */}
        {step === 1 && (
          <div className="card max-w-3xl mx-auto">
            <div className="flex items-center space-x-3 mb-6">
              <Building2 className="h-6 w-6 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">Facility Information</h2>
            </div>
            
            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="label">Facility Name</label>
                  <input
                    type="text"
                    name="facility_name"
                    value={formData.facility_name}
                    onChange={handleInputChange}
                    placeholder="e.g., Main Office Building"
                    className="input-field"
                  />
                </div>
                
                <div>
                  <label className="label">Facility Type</label>
                  <select
                    name="facility_type"
                    value={formData.facility_type}
                    onChange={handleInputChange}
                    className="input-field"
                  >
                    {FACILITY_TYPES.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="label">Location</label>
                  <select
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    className="input-field"
                  >
                    {LOCATIONS.map(loc => (
                      <option key={loc.value} value={loc.value}>{loc.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="label">Peak Demand (kW) <span className="text-red-500">*</span></label>
                  <input
                    type="number"
                    name="peak_demand_kw"
                    value={formData.peak_demand_kw}
                    onChange={handleInputChange}
                    placeholder="e.g., 500"
                    min="10"
                    max="100000"
                    className={`input-field ${validationErrors.peak_demand_kw ? 'border-red-500' : ''}`}
                    required
                  />
                  {validationErrors.peak_demand_kw && (
                    <p className="text-red-500 text-xs mt-1">{validationErrors.peak_demand_kw}</p>
                  )}
                </div>
                
                <div>
                  <label className="label">Annual Consumption (kWh) <span className="text-red-500">*</span></label>
                  <input
                    type="number"
                    name="annual_consumption_kwh"
                    value={formData.annual_consumption_kwh}
                    onChange={handleInputChange}
                    placeholder="e.g., 2000000"
                    min="1000"
                    className={`input-field ${validationErrors.annual_consumption_kwh ? 'border-red-500' : ''}`}
                    required
                  />
                  {validationErrors.annual_consumption_kwh && (
                    <p className="text-red-500 text-xs mt-1">{validationErrors.annual_consumption_kwh}</p>
                  )}
                </div>
                
                <div>
                  <label className="label">Required Backup Duration (hours) <span className="text-red-500">*</span></label>
                  <input
                    type="number"
                    name="backup_duration_hours"
                    value={formData.backup_duration_hours}
                    onChange={handleInputChange}
                    placeholder="e.g., 24"
                    min="1"
                    max="168"
                    className={`input-field ${validationErrors.backup_duration_hours ? 'border-red-500' : ''}`}
                    required
                  />
                  {validationErrors.backup_duration_hours && (
                    <p className="text-red-500 text-xs mt-1">{validationErrors.backup_duration_hours}</p>
                  )}
                </div>
              </div>
              
              <div className="pt-4">
                <button
                  type="button"
                  onClick={() => {
                    const errors = {};
                    if (!formData.peak_demand_kw || formData.peak_demand_kw <= 0) {
                      errors.peak_demand_kw = 'Peak Demand is required';
                    }
                    if (!formData.annual_consumption_kwh || formData.annual_consumption_kwh <= 0) {
                      errors.annual_consumption_kwh = 'Annual Consumption is required';
                    }
                    if (!formData.backup_duration_hours || formData.backup_duration_hours <= 0) {
                      errors.backup_duration_hours = 'Backup Duration is required';
                    }
                    setValidationErrors(errors);
                    if (Object.keys(errors).length === 0) {
                      setStep(2);
                    }
                  }}
                  className="btn-primary w-full"
                >
                  Continue to System Options
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Step 2: System Options */}
        {step === 2 && (
          <div className="card max-w-3xl mx-auto">
            <div className="flex items-center space-x-3 mb-6">
              <Settings className="h-6 w-6 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">System Configuration</h2>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Load Breakdown */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-4">Load Priority Breakdown</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Critical Load (%) <span className="text-red-500">*</span></label>
                    <input
                      type="number"
                      name="critical_load_percent"
                      value={formData.critical_load_percent}
                      onChange={handleInputChange}
                      placeholder="e.g., 30"
                      min="1"
                      max="100"
                      className={`input-field ${validationErrors.critical_load_percent ? 'border-red-500' : ''}`}
                      required
                    />
                    {validationErrors.critical_load_percent ? (
                      <p className="text-red-500 text-xs mt-1">{validationErrors.critical_load_percent}</p>
                    ) : (
                      <p className="text-xs text-gray-500 mt-1">Life safety, emergency systems</p>
                    )}
                  </div>
                  <div>
                    <label className="label">Essential Load (%) <span className="text-red-500">*</span></label>
                    <input
                      type="number"
                      name="essential_load_percent"
                      value={formData.essential_load_percent}
                      onChange={handleInputChange}
                      placeholder="e.g., 40"
                      min="1"
                      max="100"
                      className={`input-field ${validationErrors.essential_load_percent ? 'border-red-500' : ''}`}
                      required
                    />
                    {validationErrors.essential_load_percent ? (
                      <p className="text-red-500 text-xs mt-1">{validationErrors.essential_load_percent}</p>
                    ) : (
                      <p className="text-xs text-gray-500 mt-1">HVAC, refrigeration, key operations</p>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Component Selection */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-4">Microgrid Components</h3>
                <div className="space-y-4">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      name="include_solar"
                      checked={formData.include_solar}
                      onChange={handleInputChange}
                      className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                    />
                    <Sun className="h-5 w-5 text-yellow-500" />
                    <div>
                      <span className="font-medium text-gray-900">Solar PV</span>
                      <p className="text-sm text-gray-500">Clean energy generation, 30% ITC eligible</p>
                    </div>
                  </label>
                  
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      name="include_battery"
                      checked={formData.include_battery}
                      onChange={handleInputChange}
                      className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                    />
                    <Battery className="h-5 w-5 text-green-500" />
                    <div>
                      <span className="font-medium text-gray-900">Battery Storage</span>
                      <p className="text-sm text-gray-500">Peak shaving, backup power, 30% ITC eligible</p>
                    </div>
                  </label>
                  
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      name="include_generator"
                      checked={formData.include_generator}
                      onChange={handleInputChange}
                      className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                    />
                    <Zap className="h-5 w-5 text-orange-500" />
                    <div>
                      <span className="font-medium text-gray-900">Backup Generator</span>
                      <p className="text-sm text-gray-500">Extended outage protection (72+ hours)</p>
                    </div>
                  </label>
                </div>
              </div>
              
              {/* Grid Connection */}
              <div className="bg-gray-50 rounded-lg p-4">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    name="grid_connected"
                    checked={formData.grid_connected}
                    onChange={handleInputChange}
                    className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <Activity className="h-5 w-5 text-blue-500" />
                  <div>
                    <span className="font-medium text-gray-900">Grid-Connected</span>
                    <p className="text-sm text-gray-500">Interconnected with Entergy Louisiana grid</p>
                  </div>
                </label>
              </div>
              
              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="btn-secondary flex-1"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex-1 flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <BarChart3 className="h-5 w-5" />
                      <span>Generate Analysis</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Step 3: Results */}
        {step === 3 && results && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm">Total System Size</p>
                    <p className="text-2xl font-bold">{formatNumber(results.design.total_generation_kw)} kW</p>
                  </div>
                  <Zap className="h-10 w-10 text-blue-200" />
                </div>
              </div>
              
              <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm">Total Capital Cost</p>
                    <p className="text-2xl font-bold">{formatCurrency(results.costs.total_capital_cost)}</p>
                  </div>
                  <DollarSign className="h-10 w-10 text-green-200" />
                </div>
              </div>
              
              <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm">Simple Payback</p>
                    <p className="text-2xl font-bold">{results.financial.simple_payback_years} years</p>
                  </div>
                  <TrendingUp className="h-10 w-10 text-purple-200" />
                </div>
              </div>
              
              <div className="card bg-gradient-to-br from-orange-500 to-orange-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 text-sm">Reliability Improvement</p>
                    <p className="text-2xl font-bold">{results.reliability.reliability_improvement_percent}%</p>
                  </div>
                  <Shield className="h-10 w-10 text-orange-200" />
                </div>
              </div>
            </div>

            {/* Detailed Results */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* System Design */}
              <div className="card">
                <div className="flex items-center space-x-3 mb-4">
                  <Settings className="h-5 w-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">System Design</h3>
                </div>
                <div className="space-y-3">
                  {results.design.solar_pv_kw > 0 && (
                    <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Sun className="h-5 w-5 text-yellow-600" />
                        <span className="font-medium">Solar PV</span>
                      </div>
                      <span className="font-semibold">{formatNumber(results.design.solar_pv_kw)} kW</span>
                    </div>
                  )}
                  {results.design.battery_kwh > 0 && (
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Battery className="h-5 w-5 text-green-600" />
                        <span className="font-medium">Battery Storage</span>
                      </div>
                      <span className="font-semibold">{formatNumber(results.design.battery_kwh)} kWh / {formatNumber(results.design.battery_kw)} kW</span>
                    </div>
                  )}
                  {results.design.generator_kw > 0 && (
                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Zap className="h-5 w-5 text-orange-600" />
                        <span className="font-medium">Backup Generator</span>
                      </div>
                      <span className="font-semibold">{formatNumber(results.design.generator_kw)} kW</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Activity className="h-5 w-5 text-blue-600" />
                      <span className="font-medium">Inverter</span>
                    </div>
                    <span className="font-semibold">{formatNumber(results.design.inverter_kw)} kW</span>
                  </div>
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Renewable Fraction</span>
                      <span className="font-semibold text-green-600">{(results.design.renewable_fraction * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-sm mt-2">
                      <span className="text-gray-600">Critical Load Coverage</span>
                      <span className="font-semibold text-blue-600">{(results.design.critical_load_coverage * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Cost Breakdown */}
              <div className="card">
                <div className="flex items-center space-x-3 mb-4">
                  <DollarSign className="h-5 w-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Cost Breakdown</h3>
                </div>
                <div className="space-y-3">
                  {results.costs.solar_pv_cost > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Solar PV</span>
                      <span className="font-medium">{formatCurrency(results.costs.solar_pv_cost)}</span>
                    </div>
                  )}
                  {results.costs.battery_cost > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Battery Storage</span>
                      <span className="font-medium">{formatCurrency(results.costs.battery_cost)}</span>
                    </div>
                  )}
                  {results.costs.generator_cost > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Backup Generator</span>
                      <span className="font-medium">{formatCurrency(results.costs.generator_cost)}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-600">Inverter</span>
                    <span className="font-medium">{formatCurrency(results.costs.inverter_cost)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Balance of System</span>
                    <span className="font-medium">{formatCurrency(results.costs.bos_cost)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Installation</span>
                    <span className="font-medium">{formatCurrency(results.costs.installation_cost)}</span>
                  </div>
                  <div className="pt-3 mt-3 border-t border-gray-200">
                    <div className="flex justify-between font-semibold text-lg">
                      <span>Total Capital Cost</span>
                      <span className="text-primary-600">{formatCurrency(results.costs.total_capital_cost)}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-2">
                      <span className="text-gray-600">Cost per kW</span>
                      <span className="font-medium">{formatCurrency(results.costs.cost_per_kw)}/kW</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-gray-600">Annual O&M</span>
                      <span className="font-medium">{formatCurrency(results.costs.annual_om_cost)}/year</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Financial Analysis */}
              <div className="card">
                <div className="flex items-center space-x-3 mb-4">
                  <TrendingUp className="h-5 w-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Financial Analysis</h3>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-3 text-center">
                      <p className="text-sm text-gray-600">LCOE</p>
                      <p className="text-xl font-bold text-gray-900">${(results.financial.lcoe * 100).toFixed(1)}/kWh</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 text-center">
                      <p className="text-sm text-gray-600">IRR</p>
                      <p className="text-xl font-bold text-gray-900">{results.financial.irr.toFixed(1)}%</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Federal ITC (30%)</span>
                      <span className="font-medium text-green-600">-{formatCurrency(results.financial.federal_itc)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Net Cost After Incentives</span>
                      <span className="font-semibold">{formatCurrency(results.financial.net_cost_after_incentives)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Annual Savings</span>
                      <span className="font-medium text-green-600">{formatCurrency(results.financial.annual_savings)}/year</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-gray-200">
                      <span className="text-gray-600">25-Year NPV</span>
                      <span className={`font-bold ${results.financial.npv > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(results.financial.npv)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Reliability Assessment */}
              <div className="card">
                <div className="flex items-center space-x-3 mb-4">
                  <Shield className="h-5 w-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Reliability Assessment</h3>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <p className="text-sm text-blue-600">Backup Duration</p>
                      <p className="text-xl font-bold text-blue-900">{results.reliability.backup_duration_hours} hrs</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-3 text-center">
                      <p className="text-sm text-green-600">Critical Coverage</p>
                      <p className="text-xl font-bold text-green-900">{results.reliability.critical_load_coverage_percent}%</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Expected Outages (LA avg)</span>
                      <span className="font-medium">{results.reliability.expected_outage_hours_per_year} hrs/year</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avoided Outage Cost</span>
                      <span className="font-medium text-green-600">{formatCurrency(results.reliability.avoided_outage_cost)}/year</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-gray-200">
                      <span className="text-gray-600">Reliability Improvement</span>
                      <span className="font-bold text-green-600">{results.reliability.reliability_improvement_percent}%</span>
                    </div>
                  </div>
                  
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-4">
                    <div className="flex items-start space-x-2">
                      <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                      <p className="text-sm text-yellow-800">
                        Louisiana experiences higher-than-average outages due to hurricane exposure. 
                        This microgrid provides critical resilience during storm events.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="card">
              <div className="flex items-center space-x-3 mb-4">
                <FileText className="h-5 w-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {results.recommendations.map((rec, idx) => (
                  <div key={idx} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-gray-700">{rec}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Calculation Details Toggle */}
            <div className="card">
              <button
                onClick={() => setShowCalculations(!showCalculations)}
                className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <Calculator className="h-5 w-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Calculation Methodology</h3>
                </div>
                <div className="flex items-center space-x-2 text-primary-600">
                  <span className="text-sm">{showCalculations ? 'Hide Details' : 'Show Details'}</span>
                  {showCalculations ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                </div>
              </button>
              
              {showCalculations && (
                <div className="mt-4 space-y-6 border-t border-gray-200 pt-4">
                  {/* DER Sizing Methodology */}
                  <div>
                    <h4 className="font-semibold text-gray-900 flex items-center space-x-2 mb-3">
                      <Info className="h-4 w-4 text-blue-500" />
                      <span>DER Sizing Methodology</span>
                    </h4>
                    <div className="bg-blue-50 rounded-lg p-4 space-y-3 text-sm">
                      <div>
                        <p className="font-medium text-blue-900">Solar PV Sizing:</p>
                        <p className="text-blue-800 font-mono text-xs mt-1">
                          Solar kW = Peak Demand × 1.2 (120% coverage factor)
                        </p>
                        <p className="text-blue-700 mt-1">
                          = {formData.peak_demand_kw || 500} kW × 1.2 = <strong>{formatNumber(results.design.solar_pv_kw)} kW</strong>
                        </p>
                      </div>
                      <div>
                        <p className="font-medium text-blue-900">Battery Storage Sizing:</p>
                        <p className="text-blue-800 font-mono text-xs mt-1">
                          Battery kWh = Critical Load × Backup Duration
                        </p>
                        <p className="text-blue-700 mt-1">
                          = ({formData.peak_demand_kw || 500} kW × {formData.critical_load_percent || 30}%) × {formData.backup_duration_hours || 24} hrs = <strong>{formatNumber(results.design.battery_kwh)} kWh</strong>
                        </p>
                      </div>
                      <div>
                        <p className="font-medium text-blue-900">Generator Sizing:</p>
                        <p className="text-blue-800 font-mono text-xs mt-1">
                          Generator kW = (Critical + Essential Load) × 1.25 (safety margin)
                        </p>
                        <p className="text-blue-700 mt-1">
                          = ({formData.peak_demand_kw || 500} kW × {(formData.critical_load_percent || 30) + (formData.essential_load_percent || 40)}%) × 1.25 = <strong>{formatNumber(results.design.generator_kw)} kW</strong>
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Cost Calculation */}
                  <div>
                    <h4 className="font-semibold text-gray-900 flex items-center space-x-2 mb-3">
                      <Info className="h-4 w-4 text-green-500" />
                      <span>Cost Calculation (NREL ATB 2024)</span>
                    </h4>
                    <div className="bg-green-50 rounded-lg p-4 space-y-3 text-sm">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="font-medium text-green-900">Solar PV Cost:</p>
                          <p className="text-green-800 font-mono text-xs mt-1">$1,551/kW (NREL ATB 2024 Moderate)</p>
                          <p className="text-green-700 mt-1">
                            {formatNumber(results.design.solar_pv_kw)} kW × $1,551 = <strong>{formatCurrency(results.costs.solar_pv_cost)}</strong>
                          </p>
                        </div>
                        <div>
                          <p className="font-medium text-green-900">Battery Cost:</p>
                          <p className="text-green-800 font-mono text-xs mt-1">$485/kWh (NREL ATB 2024, 4-hr system)</p>
                          <p className="text-green-700 mt-1">
                            {formatNumber(results.design.battery_kwh)} kWh × $485 = <strong>{formatCurrency(results.costs.battery_cost)}</strong>
                          </p>
                        </div>
                        <div>
                          <p className="font-medium text-green-900">Generator Cost:</p>
                          <p className="text-green-800 font-mono text-xs mt-1">$800/kW (Diesel generator)</p>
                          <p className="text-green-700 mt-1">
                            {formatNumber(results.design.generator_kw)} kW × $800 = <strong>{formatCurrency(results.costs.generator_cost)}</strong>
                          </p>
                        </div>
                        <div>
                          <p className="font-medium text-green-900">BOS & Installation:</p>
                          <p className="text-green-800 font-mono text-xs mt-1">BOS: 15% | Installation: 10%</p>
                          <p className="text-green-700 mt-1">
                            Equipment × 25% = <strong>{formatCurrency(results.costs.bos_cost + results.costs.installation_cost)}</strong>
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Financial Analysis */}
                  <div>
                    <h4 className="font-semibold text-gray-900 flex items-center space-x-2 mb-3">
                      <Info className="h-4 w-4 text-purple-500" />
                      <span>Financial Analysis Methodology</span>
                    </h4>
                    <div className="bg-purple-50 rounded-lg p-4 space-y-3 text-sm">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="font-medium text-purple-900">Federal ITC (30%):</p>
                          <p className="text-purple-800 font-mono text-xs mt-1">ITC = (Solar + Battery Cost) × 30%</p>
                          <p className="text-purple-700 mt-1">
                            ({formatCurrency(results.costs.solar_pv_cost)} + {formatCurrency(results.costs.battery_cost)}) × 30% = <strong>{formatCurrency(results.financial.federal_itc)}</strong>
                          </p>
                        </div>
                        <div>
                          <p className="font-medium text-purple-900">Annual Savings:</p>
                          <p className="text-purple-800 font-mono text-xs mt-1">Energy + Demand Charge + Arbitrage Savings</p>
                          <p className="text-purple-700 mt-1">
                            Solar production × $0.0945/kWh + TOU arbitrage = <strong>{formatCurrency(results.financial.annual_savings)}/yr</strong>
                          </p>
                        </div>
                        <div>
                          <p className="font-medium text-purple-900">Simple Payback:</p>
                          <p className="text-purple-800 font-mono text-xs mt-1">Net Cost ÷ Annual Savings</p>
                          <p className="text-purple-700 mt-1">
                            {formatCurrency(results.financial.net_cost_after_incentives)} ÷ {formatCurrency(results.financial.annual_savings)} = <strong>{results.financial.simple_payback_years} years</strong>
                          </p>
                        </div>
                        <div>
                          <p className="font-medium text-purple-900">NPV (25-year):</p>
                          <p className="text-purple-800 font-mono text-xs mt-1">Discount Rate: 6% | Escalation: 2%/yr</p>
                          <p className="text-purple-700 mt-1">
                            Present value of savings - Net cost = <strong>{formatCurrency(results.financial.npv)}</strong>
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* TOU Arbitrage */}
                  <div>
                    <h4 className="font-semibold text-gray-900 flex items-center space-x-2 mb-3">
                      <Info className="h-4 w-4 text-orange-500" />
                      <span>TOU Arbitrage (Entergy Louisiana HLFS-TOD-G)</span>
                    </h4>
                    <div className="bg-orange-50 rounded-lg p-4 text-sm">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                        <div className="text-center">
                          <p className="text-orange-600 text-xs">Summer On-Peak</p>
                          <p className="font-bold text-orange-900">$0.02554/kWh</p>
                        </div>
                        <div className="text-center">
                          <p className="text-orange-600 text-xs">Summer Off-Peak</p>
                          <p className="font-bold text-orange-900">$0.00607/kWh</p>
                        </div>
                        <div className="text-center">
                          <p className="text-orange-600 text-xs">Price Spread</p>
                          <p className="font-bold text-orange-900">321%</p>
                        </div>
                        <div className="text-center">
                          <p className="text-orange-600 text-xs">Export Credit</p>
                          <p className="font-bold text-orange-900">$0.026/kWh</p>
                        </div>
                      </div>
                      <p className="text-orange-800 text-xs">
                        Battery charges during off-peak hours and discharges during on-peak, capturing the price spread. 
                        Summer months (May-Oct) offer highest arbitrage value.
                      </p>
                    </div>
                  </div>

                  {/* Data Sources */}
                  <div>
                    <h4 className="font-semibold text-gray-900 flex items-center space-x-2 mb-3">
                      <Info className="h-4 w-4 text-gray-500" />
                      <span>Data Sources</span>
                    </h4>
                    <div className="bg-gray-100 rounded-lg p-4 text-xs text-gray-700 space-y-1">
                      <p>• <strong>Component Costs:</strong> NREL Annual Technology Baseline 2024</p>
                      <p>• <strong>Solar Resource:</strong> NREL PVWatts API (Baton Rouge TMY3, CF: 26.9%)</p>
                      <p>• <strong>Load Profiles:</strong> OpenEI Louisiana EnergyPlus Data</p>
                      <p>• <strong>Utility Rates:</strong> Entergy Louisiana LGS-L Tariff (Aug 2024)</p>
                      <p>• <strong>TOU Rates:</strong> Entergy Louisiana HLFS-TOD-G</p>
                      <p>• <strong>Reliability:</strong> EIA Form 861 - Entergy Louisiana (SAIDI: 213.2 min/yr)</p>
                      <p>• <strong>Incentives:</strong> IRS (30% ITC), LPSC (Net Billing $0.026/kWh)</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => {
                  setStep(1);
                  setResults(null);
                }}
                className="btn-secondary"
              >
                Start New Analysis
              </button>
              <button
                onClick={() => window.print()}
                className="btn-primary flex items-center space-x-2"
              >
                <FileText className="h-5 w-5" />
                <span>Export Report</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
            <p>MGCE Platform - University of Louisiana at Lafayette</p>
            <p className="mt-2 md:mt-0">Data Sources: NREL ATB 2024, EIA Form 861, Entergy Louisiana</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
