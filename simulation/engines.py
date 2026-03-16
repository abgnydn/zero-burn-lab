"""
Zero-Burn Blueprint — Scientific Simulation Engines
All formulas sourced from FEASIBILITY_STUDY.md v2.0
"""
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ================================================================
# VERIFIED CONSTANTS
# ================================================================

# Water / Steam Thermodynamics
CP_WATER = 4.186      # kJ/(kg·K)
CP_VAPOR = 2.010      # kJ/(kg·K)
LV = 2257.0           # kJ/kg — latent heat of vaporization at 1 atm
T_BOIL = 100.0        # °C at ~1 atm
T_AMBIENT = 25.0      # °C — average Thailand water temp

# Biomass Fuel
BIOMASS_LHV = 14.0    # MJ/kg (LHV, dry rice husk/straw)

# Default Boiler Design
DEFAULT_COIL_LENGTH = 21.0   # meters
DEFAULT_TUBE_OD = 0.0127     # meters (1/2 inch)
DEFAULT_TUBE_ID = 0.01118    # meters
DEFAULT_COIL_DIAM = 0.200    # meters
DEFAULT_FLOW_RATE = 0.045    # kg/s

# Thailand Agriculture
STRAW_PER_RAI_DEFAULT = 650  # kg
BURN_FRACTION = 0.70

# Mushroom — V. volvacea
MUSHROOM_TEMP_OPTIMAL = (30, 35)     # °C
MUSHROOM_HUMIDITY_OPTIMAL = (80, 90) # %RH
MUSHROOM_PH_RANGE = (6.0, 8.0)
MUSHROOM_CYCLE_DAYS = (14, 22)

# IPCC 2019 Emission Factors (Vol.4, Ch.2, Table 2.5)
CH4_EF = 2.7     # kg CH₄ per ton dry straw
N2O_EF = 0.07    # kg N₂O per ton dry straw
GWP_CH4 = 28     # 100-year GWP
GWP_N2O = 265    # 100-year GWP

# Thai Operating Costs (THB per rai per cycle)
DEFAULT_COSTS = {
    'Water (100L)': 50,
    'Spawn (1.5 kg)': 90,
    'Supplements': 30,
    'Labor: Steam (1 hr)': 100,
    'Labor: Inoculation (2 hr)': 200,
    'Labor: Monitoring (3 hr)': 300,
    'Labor: Harvest (2 hr)': 200,
    'Shade structure (amortized)': 150,
    'Equipment (amortized)': 66,
}


# ================================================================
# THERMODYNAMIC ENGINE
# ================================================================

def compute_steam_energy(
    flow_rate: float = DEFAULT_FLOW_RATE,
    t_out: float = 120.0,
    t_in: float = T_AMBIENT,
) -> Dict[str, float]:
    """
    Compute energy required for steam generation.
    Q = ṁ × [cp_w(T_boil - T_in) + Lv + cp_v(T_out - T_boil)]
    
    Returns dict with kW values for each phase.
    """
    q_sensible = flow_rate * CP_WATER * (T_BOIL - t_in)    # kW
    q_latent = flow_rate * LV                                # kW
    q_superheat = flow_rate * CP_VAPOR * (t_out - T_BOIL)   # kW
    q_total = q_sensible + q_latent + q_superheat

    return {
        'q_sensible_kw': round(q_sensible, 2),
        'q_latent_kw': round(q_latent, 2),
        'q_superheat_kw': round(q_superheat, 2),
        'q_total_kw': round(q_total, 2),
    }


def compute_fuel_requirement(
    q_total_kw: float,
    combustion_eff: float = 0.35,
    treatment_time_min: float = 45.0,
) -> Dict[str, float]:
    """
    Compute biomass fuel consumption.
    """
    effective_energy_kj_per_kg = BIOMASS_LHV * 1000 * combustion_eff
    fuel_rate_kg_s = q_total_kw / effective_energy_kj_per_kg
    fuel_rate_kg_hr = fuel_rate_kg_s * 3600
    fuel_per_treatment = fuel_rate_kg_hr * (treatment_time_min / 60)

    return {
        'fuel_rate_kg_hr': round(fuel_rate_kg_hr, 1),
        'fuel_per_treatment_kg': round(fuel_per_treatment, 0),
        'effective_energy_kj_per_kg': round(effective_energy_kj_per_kg, 0),
    }


def compute_temperature_profile(
    coil_length: float = DEFAULT_COIL_LENGTH,
    flow_rate: float = DEFAULT_FLOW_RATE,
    combustion_eff: float = 0.35,
    core_temp: float = 850.0,
    n_points: int = 100,
) -> np.ndarray:
    """
    Compute temperature and pressure profile along the helical coil.
    Returns structured array with columns: position, water_temp, flue_temp, pressure, zone
    """
    positions = np.linspace(0, coil_length, n_points)
    water_temps = np.zeros(n_points)
    pressures = np.zeros(n_points)
    zones = []

    for i, pos in enumerate(positions):
        frac = pos / coil_length

        if frac < 0.55:
            # Sensible heating: 25°C → 100°C
            water_temps[i] = T_AMBIENT + (T_BOIL - T_AMBIENT) * (frac / 0.55)
            zones.append('Sensible')
        elif frac < 0.90:
            # Vaporization: ~100°C (phase change)
            water_temps[i] = T_BOIL
            zones.append('Vaporization')
        else:
            # Superheating: 100°C → T_out
            superheat_frac = (frac - 0.90) / 0.10
            water_temps[i] = T_BOIL + 20 * superheat_frac
            zones.append('Superheat')

        # Pressure drops along coil (friction + elevation)
        pressures[i] = max(0.1, 2.4 * (1 - pos / (coil_length * 1.3)))

    return positions, water_temps, pressures, zones


def compute_lmtd(t_hot_in: float, t_hot_out: float, t_cold_in: float, t_cold_out: float) -> float:
    """Logarithmic Mean Temperature Difference (counter-flow)."""
    dt1 = t_hot_in - t_cold_out
    dt2 = t_hot_out - t_cold_in
    if dt1 <= 0 or dt2 <= 0:
        return 0.001  # prevent log of negative
    if abs(dt1 - dt2) < 0.001:
        return dt1
    return (dt1 - dt2) / np.log(dt1 / dt2)


def compute_heat_transfer_adequacy(
    coil_length: float = DEFAULT_COIL_LENGTH,
    tube_od: float = DEFAULT_TUBE_OD,
    u_value: float = 300.0,
    core_temp: float = 850.0,
    exhaust_temp: float = 300.0,
    t_out: float = 120.0,
) -> Dict[str, float]:
    """
    Check if coil provides adequate heat transfer area.
    A_required = Q / (U × LMTD)
    """
    energy = compute_steam_energy(t_out=t_out)
    lmtd = compute_lmtd(core_temp, exhaust_temp, T_AMBIENT, t_out)
    required_area = (energy['q_total_kw'] * 1000) / (u_value * lmtd) if lmtd > 0 else float('inf')
    available_area = np.pi * tube_od * coil_length

    return {
        'lmtd_c': round(lmtd, 1),
        'required_area_m2': round(required_area, 4),
        'available_area_m2': round(available_area, 4),
        'adequacy_pct': round((available_area / required_area) * 100, 1) if required_area > 0 else 0,
        'is_adequate': available_area >= required_area,
    }


def optimize_coil_length(
    u_value: float = 300.0,
    tube_od: float = DEFAULT_TUBE_OD,
    t_out: float = 120.0,
    safety_margin: float = 1.15,
) -> float:
    """Find minimum coil length for adequate heat transfer (with safety margin)."""
    ht = compute_heat_transfer_adequacy(coil_length=1.0, tube_od=tube_od, u_value=u_value, t_out=t_out)
    min_length = ht['required_area_m2'] / (np.pi * tube_od) * safety_margin
    return round(min_length, 1)


# ================================================================
# SCALING / MAINTENANCE ENGINE
# ================================================================

def compute_scale_profile(
    hours: int = 500,
    water_hardness_ppm: float = 250.0,
    flow_rate: float = DEFAULT_FLOW_RATE,
    coil_length: float = DEFAULT_COIL_LENGTH,
    tube_id: float = DEFAULT_TUBE_ID,
    base_u: float = 300.0,
    step: int = 10,
) -> List[Dict]:
    """
    Model CaCO₃ scale deposition and efficiency degradation over time.
    Scale thermal conductivity: ~1.5 W/(m·K)
    """
    results = []
    inner_area = np.pi * tube_id * coil_length

    for h in range(0, hours + 1, step):
        # Deposited mass (kg) — simplified empirical model
        mass = (flow_rate * h * 3600 * water_hardness_ppm * 0.7) / 1e6
        thickness_mm = (mass / 2500) / inner_area * 1000  # mm

        # Reduced U-value with scale insulation layer
        adjusted_u = 1.0 / ((1.0 / base_u) + (thickness_mm / 1000 / 1.5))
        efficiency = (adjusted_u / base_u) * 100

        results.append({
            'hours': h,
            'scale_mm': round(thickness_mm, 4),
            'efficiency_pct': round(max(efficiency, 10), 1),
            'u_effective': round(adjusted_u, 1),
            'needs_descale': thickness_mm > 0.5,
        })

    return results


# ================================================================
# MUSHROOM YIELD ENGINE
# ================================================================

def compute_mushroom_yield(
    straw_per_rai: float = STRAW_PER_RAI_DEFAULT,
    biological_efficiency: float = 0.12,
    fuel_fraction: float = 0.10,
    supplement_boost: float = 0.0,
) -> Dict[str, float]:
    """
    Compute mushroom yield per rai.
    BE = fresh_mushroom_weight / dry_substrate_weight × 100
    """
    substrate = straw_per_rai * (1 - fuel_fraction)
    effective_be = biological_efficiency + supplement_boost
    fresh_yield = substrate * effective_be

    return {
        'straw_available_kg': straw_per_rai,
        'fuel_consumed_kg': round(straw_per_rai * fuel_fraction),
        'substrate_kg': round(substrate),
        'effective_be_pct': round(effective_be * 100, 1),
        'fresh_yield_kg': round(fresh_yield, 1),
    }


def compute_contamination_risk(
    steam_temp: float = 120.0,
    spawn_quality: str = 'certified',
    sanitation_protocol: str = 'standard',
) -> Dict[str, float]:
    """
    Estimate Trichoderma contamination risk based on conditions.
    Based on literature: 60-100% loss when contaminated.
    """
    # Base risk (outdoor, uncontrolled)
    base_risk = 0.30

    # Steam temperature effect
    if steam_temp >= 120:
        temp_factor = 0.2
    elif steam_temp >= 100:
        temp_factor = 0.4
    elif steam_temp >= 80:
        temp_factor = 0.7
    else:
        temp_factor = 1.0

    # Spawn quality
    spawn_factors = {'certified': 0.5, 'local': 0.8, 'unknown': 1.2}
    spawn_factor = spawn_factors.get(spawn_quality, 1.0)

    # Sanitation
    sanitation_factors = {'strict': 0.4, 'standard': 0.7, 'none': 1.5}
    sanitation_factor = sanitation_factors.get(sanitation_protocol, 1.0)

    risk = min(base_risk * temp_factor * spawn_factor * sanitation_factor, 0.95)
    expected_loss = risk * 0.80  # 80% loss when contamination occurs

    return {
        'contamination_prob': round(risk, 3),
        'expected_loss_fraction': round(expected_loss, 3),
        'risk_level': 'HIGH' if risk > 0.3 else 'MEDIUM' if risk > 0.1 else 'LOW',
    }


# ================================================================
# ECONOMIC ENGINE
# ================================================================

def compute_economics(
    be: float = 0.12,
    price_per_kg: float = 45.0,
    straw_per_rai: float = STRAW_PER_RAI_DEFAULT,
    fuel_fraction: float = 0.10,
    costs: Dict[str, float] = None,
    supplement_boost: float = 0.0,
) -> Dict[str, float]:
    """
    Full per-rai cost-benefit analysis.
    """
    if costs is None:
        costs = DEFAULT_COSTS

    total_cost = sum(costs.values())
    yield_data = compute_mushroom_yield(straw_per_rai, be, fuel_fraction, supplement_boost)
    revenue = yield_data['fresh_yield_kg'] * price_per_kg
    profit = revenue - total_cost

    # Break-even
    break_even_kg = total_cost / price_per_kg if price_per_kg > 0 else float('inf')
    break_even_be = break_even_kg / yield_data['substrate_kg'] if yield_data['substrate_kg'] > 0 else float('inf')

    return {
        'total_cost_thb': total_cost,
        'revenue_thb': round(revenue),
        'profit_thb': round(profit),
        'profit_per_year_thb': round(profit * 2),  # 2 crop cycles
        'margin_pct': round((profit / revenue) * 100, 1) if revenue > 0 else 0,
        'break_even_kg': round(break_even_kg, 1),
        'break_even_be_pct': round(break_even_be * 100, 1),
        'yield_kg': yield_data['fresh_yield_kg'],
        'is_profitable': profit > 0,
    }


def compute_sensitivity_matrix(
    be_values: List[float] = None,
    price_values: List[float] = None,
    straw_per_rai: float = STRAW_PER_RAI_DEFAULT,
) -> np.ndarray:
    """2D sensitivity: profit by BE × Price."""
    if be_values is None:
        be_values = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20]
    if price_values is None:
        price_values = [30, 45, 60, 90, 120]

    matrix = np.zeros((len(be_values), len(price_values)))
    for i, be in enumerate(be_values):
        for j, price in enumerate(price_values):
            econ = compute_economics(be=be, price_per_kg=price, straw_per_rai=straw_per_rai)
            matrix[i, j] = econ['profit_thb']

    return be_values, price_values, matrix


def monte_carlo_profit(
    n_simulations: int = 10000,
    be_mean: float = 0.10,
    be_std: float = 0.03,
    price_mean: float = 55.0,
    price_std: float = 15.0,
    straw_mean: float = 650.0,
    straw_std: float = 75.0,
    contamination_prob: float = 0.08,
    seed: int = 42,
) -> Dict:
    """
    Monte Carlo simulation of per-rai profit.
    Accounts for biological efficiency variance, price variance,
    straw availability, and contamination risk.
    """
    rng = np.random.default_rng(seed)

    # Sample parameters
    be_samples = np.clip(rng.normal(be_mean, be_std, n_simulations), 0.01, 0.40)
    price_samples = np.clip(rng.normal(price_mean, price_std, n_simulations), 15, 200)
    straw_samples = np.clip(rng.normal(straw_mean, straw_std, n_simulations), 300, 1000)

    # Contamination events (bernoulli)
    contaminated = rng.random(n_simulations) < contamination_prob
    # When contaminated, yield drops 80%
    yield_multiplier = np.where(contaminated, 0.20, 1.0)

    # Compute profits
    total_cost = sum(DEFAULT_COSTS.values())
    substrate = straw_samples * 0.90  # 10% fuel
    yields = substrate * be_samples * yield_multiplier
    revenues = yields * price_samples
    profits = revenues - total_cost

    return {
        'profits': profits,
        'mean_profit': round(float(np.mean(profits))),
        'median_profit': round(float(np.median(profits))),
        'std_profit': round(float(np.std(profits))),
        'p5': round(float(np.percentile(profits, 5))),
        'p25': round(float(np.percentile(profits, 25))),
        'p75': round(float(np.percentile(profits, 75))),
        'p95': round(float(np.percentile(profits, 95))),
        'prob_profitable': round(float(np.mean(profits > 0)) * 100, 1),
        'prob_loss_gt_500': round(float(np.mean(profits < -500)) * 100, 1),
        'n_contaminated': int(np.sum(contaminated)),
        'n_simulations': n_simulations,
    }


# ================================================================
# CARBON CREDIT ENGINE
# ================================================================

def compute_carbon_credits(
    straw_per_rai: float = STRAW_PER_RAI_DEFAULT,
    carbon_price_thb: float = 1000.0,
    n_rai: float = 1.0,
) -> Dict[str, float]:
    """
    Compute avoided GHG emissions and carbon credit revenue.
    IPCC methodology: only non-CO₂ gases count.
    """
    straw_burned_tons = (straw_per_rai * BURN_FRACTION) / 1000  # tons per rai

    ch4_co2eq = straw_burned_tons * CH4_EF * GWP_CH4   # kg CO₂eq
    n2o_co2eq = straw_burned_tons * N2O_EF * GWP_N2O   # kg CO₂eq
    total_co2eq_kg = ch4_co2eq + n2o_co2eq
    total_tco2eq = total_co2eq_kg / 1000

    revenue_per_rai = total_tco2eq * carbon_price_thb
    revenue_total = revenue_per_rai * n_rai

    return {
        'straw_burned_tons': round(straw_burned_tons, 3),
        'ch4_co2eq_kg': round(ch4_co2eq, 2),
        'n2o_co2eq_kg': round(n2o_co2eq, 2),
        'total_co2eq_kg': round(total_co2eq_kg, 2),
        'total_tco2eq': round(total_tco2eq, 4),
        'revenue_per_rai_thb': round(revenue_per_rai, 2),
        'revenue_total_thb': round(revenue_total, 2),
    }


# ================================================================
# REGIONAL SCALING ENGINE
# ================================================================

def compute_regional_impact(
    n_villages: int = 4,
    farmers_per_village: int = 50,
    rai_per_farmer: float = 12.0,
    adoption_rate: float = 0.75,
    be: float = 0.12,
    price_per_kg: float = 45.0,
) -> Dict:
    """
    Compute regional impact of program deployment.
    """
    total_rai = n_villages * farmers_per_village * rai_per_farmer * adoption_rate
    econ = compute_economics(be=be, price_per_kg=price_per_kg)
    carbon = compute_carbon_credits(n_rai=total_rai)

    # Equipment needs
    rai_per_day = 25  # 45 min/rai, 8hr day
    treatment_window = 14  # days
    units_needed = int(np.ceil(total_rai / (rai_per_day * treatment_window)))
    equipment_cost = units_needed * 26550

    return {
        'total_rai': round(total_rai),
        'total_farmers': round(n_villages * farmers_per_village * adoption_rate),
        'total_mushroom_revenue': round(econ['revenue_thb'] * total_rai),
        'total_profit': round(econ['profit_thb'] * total_rai),
        'total_co2eq_avoided_tons': round(carbon['total_tco2eq'] * total_rai, 1),
        'total_carbon_revenue': round(carbon['revenue_per_rai_thb'] * total_rai),
        'units_needed': units_needed,
        'equipment_investment': equipment_cost,
        'roi_pct': round((econ['profit_thb'] * total_rai * 2) / equipment_cost * 100, 0) if equipment_cost > 0 else 0,
    }


# ================================================================
# OPTIMIZER: Find Best Parameters
# ================================================================

def optimize_system(
    target: str = 'profit',  # 'profit', 'be_threshold', 'fuel_efficiency'
) -> Dict:
    """
    Find optimal system parameters using scipy.
    """
    from scipy.optimize import minimize_scalar, minimize

    if target == 'min_coil_for_100c':
        # Find minimum coil length to achieve 100°C outlet
        result = optimize_coil_length(u_value=300, t_out=100)
        return {'optimal_coil_length_m': result, 'target': '≥100°C outlet'}

    elif target == 'max_profit_flow_rate':
        # Optimize flow rate for max profit (more flow = more area treated/hr but more fuel)
        def neg_profit(flow_rate):
            energy = compute_steam_energy(flow_rate=flow_rate, t_out=120)
            fuel = compute_fuel_requirement(energy['q_total_kw'])
            fuel_kg = fuel['fuel_per_treatment_kg']
            substrate = STRAW_PER_RAI_DEFAULT - fuel_kg
            if substrate <= 0:
                return 0
            yield_kg = substrate * 0.12
            revenue = yield_kg * 45
            cost = sum(DEFAULT_COSTS.values())
            return -(revenue - cost)

        result = minimize_scalar(neg_profit, bounds=(0.01, 0.10), method='bounded')
        optimal_flow = round(result.x, 4)
        econ = compute_economics(fuel_fraction=compute_fuel_requirement(
            compute_steam_energy(flow_rate=optimal_flow)['q_total_kw'])['fuel_per_treatment_kg'] / STRAW_PER_RAI_DEFAULT)

        return {
            'optimal_flow_rate_kg_s': optimal_flow,
            'optimal_flow_rate_ml_s': round(optimal_flow * 1000, 1),
            'profit_at_optimal': econ['profit_thb'],
        }

    return {}
