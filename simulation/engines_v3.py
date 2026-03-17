"""
Zero-Burn Blueprint — Advanced Simulation Engines v3.0
Deep physics and biological models from verified research.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional


# ================================================================
# ADVANCED THERMODYNAMIC ENGINE
# ================================================================

# Physical properties
RHO_WATER = 997.0      # kg/m³ at 25°C
MU_WATER = 8.9e-4      # Pa·s dynamic viscosity at 25°C
MU_WATER_100 = 2.82e-4 # Pa·s at 100°C
K_WATER = 0.607        # W/(m·K) thermal conductivity at 25°C
K_COPPER = 385.0       # W/(m·K)
PR_WATER = 6.14        # Prandtl number at 25°C
PR_WATER_100 = 1.75    # Prandtl number at 100°C

# Tube geometry
DEFAULT_TUBE_ID = 0.01118   # m (½" Type L copper)
DEFAULT_TUBE_OD = 0.0127    # m
DEFAULT_COIL_DIAM = 0.200   # m (coil center-to-center)
DEFAULT_PITCH = 0.020       # m spacing between turns


def compute_reynolds(flow_rate_kg_s: float, tube_id: float = DEFAULT_TUBE_ID) -> float:
    """Reynolds number: Re = ρvD/μ = 4ṁ/(πDμ)"""
    return (4 * flow_rate_kg_s) / (np.pi * tube_id * MU_WATER)


def compute_dean_number(
    flow_rate_kg_s: float,
    tube_id: float = DEFAULT_TUBE_ID,
    coil_diam: float = DEFAULT_COIL_DIAM,
) -> float:
    """
    Dean number: De = Re × √(d/D_c)
    Characterizes secondary flow intensity in helical coils.
    Source: Dean (1927), validated by Berger et al. (1983)
    """
    re = compute_reynolds(flow_rate_kg_s, tube_id)
    delta = tube_id / coil_diam  # curvature ratio
    return re * np.sqrt(delta)


def compute_critical_reynolds_helical(
    tube_id: float = DEFAULT_TUBE_ID,
    coil_diam: float = DEFAULT_COIL_DIAM,
) -> float:
    """
    Critical Reynolds for laminar-turbulent transition in helical coils.
    Srinivasan (1968): Re_crit = 2100 × [1 + 12 × √(d/D)]
    Helical coils delay transition due to centrifugal stabilization.
    """
    delta = tube_id / coil_diam
    return 2100 * (1 + 12 * np.sqrt(delta))


def compute_nusselt_helical(
    flow_rate_kg_s: float,
    tube_id: float = DEFAULT_TUBE_ID,
    coil_diam: float = DEFAULT_COIL_DIAM,
) -> Dict[str, float]:
    """
    Nusselt number for helical coil using Schmidt (1967) correlation.
    
    Laminar (De < 100):
        Nu = 3.66 + 0.19 × (De × Pr)^0.8 / [1 + 0.117 × (De × Pr)^0.467]
    
    Turbulent:
        Nu = 0.023 × Re^0.8 × Pr^0.33 × [1 + 14.8 × (1 + d/D_c) × (d/D_c)^3]
    
    Source: Schmidt (1967), Seban & McLaughlin (1963)
    """
    re = compute_reynolds(flow_rate_kg_s, tube_id)
    de = compute_dean_number(flow_rate_kg_s, tube_id, coil_diam)
    re_crit = compute_critical_reynolds_helical(tube_id, coil_diam)
    delta = tube_id / coil_diam
    pr = PR_WATER

    is_laminar = re < re_crit

    if is_laminar:
        # Schmidt (1967) laminar correlation
        de_pr = de * pr
        nu = 3.66 + 0.19 * (de_pr ** 0.8) / (1 + 0.117 * (de_pr ** 0.467))
        # Enhancement ratio vs straight tube (Hagen-Poiseuille: Nu = 3.66)
        nu_straight = 3.66
    else:
        # Seban & McLaughlin turbulent correlation
        nu = 0.023 * (re ** 0.8) * (pr ** 0.33) * (1 + 14.8 * (1 + delta) * (delta ** 3))
        # Dittus-Boelter for straight tube
        nu_straight = 0.023 * (re ** 0.8) * (pr ** 0.4)

    h = nu * K_WATER / tube_id  # heat transfer coefficient (W/m²K)
    h_straight = nu_straight * K_WATER / tube_id

    return {
        'reynolds': round(re, 0),
        'dean_number': round(de, 0),
        're_critical': round(re_crit, 0),
        'flow_regime': 'Laminar' if is_laminar else 'Turbulent',
        'nusselt_coil': round(nu, 2),
        'nusselt_straight': round(nu_straight, 2),
        'enhancement_ratio': round(nu / nu_straight, 2),
        'h_coil_w_m2k': round(h, 1),
        'h_straight_w_m2k': round(h_straight, 1),
    }


def compute_overall_u(
    h_inner: float,
    h_outer: float = 50.0,  # flue gas side, typically 30-80 W/m²K
    tube_id: float = DEFAULT_TUBE_ID,
    tube_od: float = DEFAULT_TUBE_OD,
    k_tube: float = K_COPPER,
    scale_thickness_mm: float = 0.0,
    k_scale: float = 1.5,  # W/(m·K) for CaCO₃
) -> Dict[str, float]:
    """
    Overall heat transfer coefficient U for tube-in-shell.
    1/U = 1/h_o + r_o×ln(r_o/r_i)/k_tube + r_o/(r_i×h_i) + R_scale
    """
    r_i = tube_id / 2
    r_o = tube_od / 2
    
    # Conduction through tube wall
    R_wall = r_o * np.log(r_o / r_i) / k_tube
    
    # Scale resistance
    R_scale = (scale_thickness_mm / 1000) / k_scale if scale_thickness_mm > 0 else 0
    
    # Overall U (based on outer area)
    U = 1 / (1/h_outer + R_wall + r_o/(r_i * h_inner) + R_scale)
    
    # Contribution breakdown
    R_total = 1/U
    pct_outer = (1/h_outer) / R_total * 100
    pct_wall = R_wall / R_total * 100
    pct_inner = (r_o/(r_i * h_inner)) / R_total * 100
    pct_scale = R_scale / R_total * 100 if R_scale > 0 else 0

    return {
        'U_overall_w_m2k': round(U, 1),
        'R_total_m2k_w': round(R_total, 6),
        'pct_outer_resistance': round(pct_outer, 1),
        'pct_wall_resistance': round(pct_wall, 1),
        'pct_inner_resistance': round(pct_inner, 1),
        'pct_scale_resistance': round(pct_scale, 1),
        'bottleneck': 'outer (flue gas)' if pct_outer > max(pct_inner, pct_wall) else 'inner (water)',
    }


def compute_pressure_drop_helical(
    flow_rate_kg_s: float,
    coil_length: float = 21.0,
    tube_id: float = DEFAULT_TUBE_ID,
    coil_diam: float = DEFAULT_COIL_DIAM,
) -> Dict[str, float]:
    """
    Pressure drop in helical coil using Darcy-Weisbach + Dean correction.
    
    Straight pipe: ΔP = f × (L/D) × (ρv²/2)
    
    Dean correction (Mishra & Gupta 1979):
        f_c/f_s = 1 + 0.033 × (log₁₀ De)^4    for De > 11.6
        f_c/f_s = 1                              for De ≤ 11.6
    
    Source: Mishra & Gupta (1979)
    """
    re = compute_reynolds(flow_rate_kg_s, tube_id)
    de = compute_dean_number(flow_rate_kg_s, tube_id, coil_diam)
    
    # Straight pipe friction (Moody - laminar)
    area = np.pi * (tube_id/2)**2
    velocity = flow_rate_kg_s / (RHO_WATER * area)
    
    if re < 2300:
        f_straight = 64 / re
    else:
        # Blasius correlation (turbulent, smooth pipe)
        f_straight = 0.316 / (re ** 0.25)
    
    # Dean correction
    if de > 11.6:
        f_ratio = 1 + 0.033 * (np.log10(de)) ** 4
    else:
        f_ratio = 1.0
    
    f_coil = f_straight * f_ratio
    
    # Pressure drop: ΔP = f × (L/D) × (ρv²/2)
    dp_straight = f_straight * (coil_length / tube_id) * (RHO_WATER * velocity**2 / 2)
    dp_coil = f_coil * (coil_length / tube_id) * (RHO_WATER * velocity**2 / 2)
    
    return {
        'velocity_m_s': round(velocity, 3),
        'f_straight': round(f_straight, 6),
        'f_coil': round(f_coil, 6),
        'friction_ratio': round(f_ratio, 2),
        'dp_straight_pa': round(dp_straight, 0),
        'dp_coil_pa': round(dp_coil, 0),
        'dp_coil_bar': round(dp_coil / 1e5, 4),
        'dp_coil_psi': round(dp_coil / 6895, 3),
        'is_acceptable': dp_coil / 1e5 < 2.0,  # < 2 bar is OK for our system
    }


def compute_flow_rate_sweep(
    flow_rates_ml_s: List[float] = None,
    coil_length: float = 21.0,
    tube_id: float = DEFAULT_TUBE_ID,
    coil_diam: float = DEFAULT_COIL_DIAM,
) -> List[Dict]:
    """Sweep flow rates and compute all engineering parameters."""
    if flow_rates_ml_s is None:
        flow_rates_ml_s = list(range(5, 105, 5))
    
    results = []
    for fr_ml in flow_rates_ml_s:
        fr_kg = fr_ml / 1000
        nu = compute_nusselt_helical(fr_kg, tube_id, coil_diam)
        u_data = compute_overall_u(nu['h_coil_w_m2k'])
        dp = compute_pressure_drop_helical(fr_kg, coil_length, tube_id, coil_diam)
        
        # Simplified inline energy calc (avoids circular import from engines.py)
        # Q = m_dot * (cp * dT + L_v), cp=4186, dT=75, L_v=2,260,000
        q_total_kw = fr_kg * (4186 * 75 + 2_260_000) / 1000
        # Fuel: rice husk HHV=15.4 MJ/kg, eta=0.65
        fuel_kg_hr = (q_total_kw / (15400 * 0.65)) * 3600
        
        results.append({
            'flow_ml_s': fr_ml,
            'reynolds': nu['reynolds'],
            'dean': nu['dean_number'],
            'regime': nu['flow_regime'],
            'nusselt': nu['nusselt_coil'],
            'enhancement': nu['enhancement_ratio'],
            'h_inner': nu['h_coil_w_m2k'],
            'U_overall': u_data['U_overall_w_m2k'],
            'bottleneck': u_data['bottleneck'],
            'dp_bar': dp['dp_coil_bar'],
            'q_total_kw': round(q_total_kw, 2),
            'fuel_kg_hr': round(fuel_kg_hr, 2),
        })
    
    return results


# ================================================================
# TRICHODERMA THERMAL KILL MODEL
# ================================================================

def compute_trichoderma_kill(
    temperature_c: float = 120.0,
    exposure_time_min: float = 45.0,
) -> Dict[str, float]:
    """
    Trichoderma thermal death model.
    
    Research data (verified sources):
    - Growth ceases above 45°C
    - Significant death at 50°C
    - D-value at 60°C ≈ 10 min (time for 90% kill)
    - Complete kill (6-log) at 60°C = ~60 min
    - D-value at 80°C ≈ 1 min
    - D-value at 100°C ≈ 0.1 min (6 seconds)
    - Our 120°C steam: D-value < 0.01 min
    
    Model: log-linear thermal death kinetics
    D(T) = D_ref × 10^((T_ref - T) / z)
    where z = 15°C (temperature sensitivity, typical for fungal spores)
    
    Sources: Bigelow (1921) thermal death model, 
             adapted from mushroom substrate pasteurization literature
    """
    # Reference: D-value at 60°C = 10 min
    D_ref = 10.0   # minutes
    T_ref = 60.0    # °C
    z_value = 15.0  # °C (z-value for fungal spores)
    
    # D-value at given temperature
    D_T = D_ref * 10 ** ((T_ref - temperature_c) / z_value)
    
    # Log reductions achieved
    log_reductions = exposure_time_min / D_T if D_T > 0 else 999
    
    # Survival fraction
    survival = 10 ** (-log_reductions)
    kill_pct = (1 - survival) * 100
    
    # Time needed for 6-log reduction (99.9999% kill)
    time_6log = D_T * 6
    
    # Safety factor
    safety_factor = exposure_time_min / time_6log if time_6log > 0 else 999
    
    return {
        'temperature_c': temperature_c,
        'exposure_time_min': exposure_time_min,
        'd_value_min': round(D_T, 6),
        'log_reductions': round(min(log_reductions, 20), 2),  # cap at 20
        'kill_pct': round(min(kill_pct, 99.999999), 6),
        'time_for_6log_min': round(time_6log, 4),
        'safety_factor': round(min(safety_factor, 999), 1),
        'assessment': _assess_kill(log_reductions),
    }


def _assess_kill(log_reductions: float) -> str:
    if log_reductions >= 12:
        return "OVERKILL — complete sterilization, way beyond needed"
    elif log_reductions >= 6:
        return "EXCELLENT — commercial sterilization standard"
    elif log_reductions >= 3:
        return "GOOD — adequate pasteurization"
    elif log_reductions >= 1:
        return "MARGINAL — 90% kill, residual risk"
    else:
        return "INSUFFICIENT — high contamination risk"


def compute_kill_curve_data(
    temperatures: List[float] = None,
    exposure_time_min: float = 45.0,
) -> List[Dict]:
    """Generate kill curves across temperatures."""
    if temperatures is None:
        temperatures = list(range(40, 141, 5))
    
    return [compute_trichoderma_kill(t, exposure_time_min) for t in temperatures]


def compute_time_to_kill(
    temperature_c: float = 120.0,
    target_log_reductions: float = 6.0,
) -> float:
    """Return time (min) needed to achieve target log reductions."""
    result = compute_trichoderma_kill(temperature_c, 1.0)  # get D-value
    return round(result['d_value_min'] * target_log_reductions, 4)


# ================================================================
# MUSHROOM GROWTH KINETICS ENGINE
# ================================================================

def compute_growth_curve(
    days: int = 30,
    be_max: float = 0.12,
    temp_c: float = 32.0,
    humidity_pct: float = 85.0,
    substrate_kg: float = 585.0,  # 650 - 10% fuel
    supplement_type: str = 'none',
) -> List[Dict]:
    """
    V. volvacea growth kinetics model.
    
    Research data:
    - Mycelium ramification: day 3-5
    - Full substrate colonization: day 7-10
    - Pinhead formation: day 10-12
    - First flush (egg stage): day 14-16 (70-75% of total yield)
    - Second flush: day 20-24 (20-25% of total yield)
    - Third flush (minor): day 26-30 (5-10% if any)
    
    Temperature effect:
    - Optimal: 30-35°C (100% efficiency)
    - Acceptable: 25-30°C (70-85% efficiency)
    - Stressed: 35-38°C (60-80% efficiency)
    - Death: <15°C or >42°C
    
    Supplement boost (on max BE):
    - None: base BE
    - Rice bran 2%: +30% BE (verified: 10.36-30.57% improvement)
    - Cotton seed hull: +15% BE
    
    Sources: CABI, ResearchGate, MASU Journal
    """
    # Temperature factor (Gaussian around optimal 32.5°C)
    temp_factor = np.exp(-((temp_c - 32.5) / 5.0) ** 2)
    if temp_c < 20 or temp_c > 42:
        temp_factor = 0.0
    
    # Humidity factor
    humidity_factor = min(1.0, max(0.0, (humidity_pct - 60) / 30))
    
    # Supplement factor
    supplement_factors = {
        'none': 1.0,
        'rice_bran_2pct': 1.30,      # +30% (verified)
        'rice_bran_5pct': 1.25,      # diminishing returns at higher concentrations
        'cotton_seed': 1.15,
        'wheat_bran': 1.20,
    }
    supp_factor = supplement_factors.get(supplement_type, 1.0)
    
    # Effective maximum BE
    effective_be = be_max * temp_factor * humidity_factor * supp_factor
    total_potential_yield = substrate_kg * effective_be
    
    # Growth phase model
    data = []
    cumulative_yield = 0.0
    
    for day in range(0, days + 1):
        # Mycelium colonization (logistic growth)
        if day <= 10:
            colonization = 1 / (1 + np.exp(-(day - 5) / 1.5))
        else:
            colonization = 1.0
        
        # Daily yield (3 flushes modeled as Gaussian peaks)
        flush1 = 0.70 * total_potential_yield * _gaussian_peak(day, 14.5, 1.8)
        flush2 = 0.22 * total_potential_yield * _gaussian_peak(day, 22.0, 2.0)
        flush3 = 0.08 * total_potential_yield * _gaussian_peak(day, 28.0, 2.5)
        daily_yield = flush1 + flush2 + flush3
        cumulative_yield += daily_yield
        
        # Phase labels
        if day <= 3:
            phase = "Inoculation"
        elif day <= 7:
            phase = "Mycelium ramification"
        elif day <= 10:
            phase = "Colonization"
        elif day <= 12:
            phase = "Pinhead formation"
        elif day <= 18:
            phase = "Flush 1 (harvest)"
        elif day <= 25:
            phase = "Flush 2 (harvest)"
        elif day <= 30:
            phase = "Flush 3 (minor)"
        else:
            phase = "Spent"
        
        data.append({
            'day': day,
            'phase': phase,
            'colonization_pct': round(colonization * 100, 1),
            'daily_yield_kg': round(daily_yield, 2),
            'cumulative_yield_kg': round(cumulative_yield, 2),
            'cumulative_be_pct': round((cumulative_yield / substrate_kg) * 100, 2) if substrate_kg > 0 else 0,
        })
    
    return data


def _gaussian_peak(x, center, sigma):
    """Gaussian distribution for flush modeling."""
    return np.exp(-((x - center) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))


def compute_substrate_comparison(
    substrate_types: List[str] = None,
) -> List[Dict]:
    """
    Compare substrate formulations based on research data.
    
    Sources: Peer-reviewed studies from ResearchGate, CABI
    """
    if substrate_types is None:
        substrate_types = ['all']
    
    data = [
        {
            'substrate': 'Rice straw only',
            'be_min': 8.0, 'be_max': 12.0, 'be_typical': 10.0,
            'cost_per_rai': 0, 'availability': 'Abundant',
            'notes': 'Baseline. Free, available post-harvest.',
        },
        {
            'substrate': 'Rice straw + 2% rice bran',
            'be_min': 10.0, 'be_max': 15.0, 'be_typical': 14.15,
            'cost_per_rai': 30, 'availability': 'Easy (rice mills)',
            'notes': 'Best supplement. +30% BE. Cheapest option.',
        },
        {
            'substrate': 'Rice straw + 5% rice bran',
            'be_min': 11.0, 'be_max': 14.0, 'be_typical': 12.5,
            'cost_per_rai': 60, 'availability': 'Easy',
            'notes': 'Diminishing returns vs 2%.',
        },
        {
            'substrate': 'Rice straw + wheat bran',
            'be_min': 10.0, 'be_max': 14.0, 'be_typical': 12.0,
            'cost_per_rai': 50, 'availability': 'Moderate',
            'notes': '+20% BE. More expensive than rice bran.',
        },
        {
            'substrate': 'Cotton waste compost',
            'be_min': 25.0, 'be_max': 35.0, 'be_typical': 30.0,
            'cost_per_rai': 500, 'availability': 'Limited (industrial)',
            'notes': 'Highest BE but expensive, not available to Thai farmers.',
        },
        {
            'substrate': 'Rice straw + oil palm EFB',
            'be_min': 12.0, 'be_max': 18.0, 'be_typical': 15.0,
            'cost_per_rai': 100, 'availability': 'Southern Thailand',
            'notes': 'Good where oil palm is grown.',
        },
    ]
    
    return data


# ================================================================
# SEASONAL CULTIVATION WINDOW MODEL
# ================================================================

def compute_seasonal_windows(region: str = 'isaan') -> List[Dict]:
    """
    Model mushroom cultivation windows based on Thai climate data.
    
    V. volvacea requirements:
    - Temperature: 30-35°C (optimal), 25-38°C (acceptable)
    - Humidity: 80-90% (optimal), 60-85% (acceptable)
    - Duration: 14-22 days per cycle
    
    Constraints:
    - Must follow rice harvest (straw availability)
    - Cannot overlap with next planting season
    - Outdoor humidity affects success
    
    Sources: Thai Meteorological Department, FFTC, FAO
    """
    if region == 'isaan':
        months = [
            {'month': 'Jan', 'avg_temp': 24, 'humidity': 65, 'rainfall_mm': 7,
             'rice_phase': 'Post-harvest', 'straw_available': True},
            {'month': 'Feb', 'avg_temp': 26, 'humidity': 60, 'rainfall_mm': 6,
             'rice_phase': 'Field prep', 'straw_available': True},
            {'month': 'Mar', 'avg_temp': 30, 'humidity': 55, 'rainfall_mm': 30,
             'rice_phase': 'Pre-monsoon', 'straw_available': False},
            {'month': 'Apr', 'avg_temp': 32, 'humidity': 60, 'rainfall_mm': 70,
             'rice_phase': 'Pre-monsoon', 'straw_available': False},
            {'month': 'May', 'avg_temp': 30, 'humidity': 75, 'rainfall_mm': 130,
             'rice_phase': 'Planting', 'straw_available': False},
            {'month': 'Jun', 'avg_temp': 29, 'humidity': 80, 'rainfall_mm': 150,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Jul', 'avg_temp': 29, 'humidity': 82, 'rainfall_mm': 180,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Aug', 'avg_temp': 29, 'humidity': 85, 'rainfall_mm': 280,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Sep', 'avg_temp': 28, 'humidity': 85, 'rainfall_mm': 250,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Oct', 'avg_temp': 27, 'humidity': 80, 'rainfall_mm': 85,
             'rice_phase': 'Maturing', 'straw_available': False},
            {'month': 'Nov', 'avg_temp': 25, 'humidity': 70, 'rainfall_mm': 20,
             'rice_phase': 'Harvest begins', 'straw_available': True},
            {'month': 'Dec', 'avg_temp': 23, 'humidity': 65, 'rainfall_mm': 7,
             'rice_phase': 'Harvest', 'straw_available': True},
        ]
    elif region == 'central':
        months = [
            {'month': 'Jan', 'avg_temp': 27, 'humidity': 70, 'rainfall_mm': 15,
             'rice_phase': 'Post-harvest / Dry rice', 'straw_available': True},
            {'month': 'Feb', 'avg_temp': 29, 'humidity': 68, 'rainfall_mm': 20,
             'rice_phase': 'Dry season rice', 'straw_available': True},
            {'month': 'Mar', 'avg_temp': 31, 'humidity': 65, 'rainfall_mm': 40,
             'rice_phase': 'Dry rice / Pre-monsoon', 'straw_available': False},
            {'month': 'Apr', 'avg_temp': 33, 'humidity': 70, 'rainfall_mm': 85,
             'rice_phase': 'Dry rice harvest', 'straw_available': True},
            {'month': 'May', 'avg_temp': 32, 'humidity': 78, 'rainfall_mm': 200,
             'rice_phase': 'Main planting', 'straw_available': False},
            {'month': 'Jun', 'avg_temp': 30, 'humidity': 80, 'rainfall_mm': 180,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Jul', 'avg_temp': 30, 'humidity': 80, 'rainfall_mm': 175,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Aug', 'avg_temp': 30, 'humidity': 82, 'rainfall_mm': 190,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Sep', 'avg_temp': 29, 'humidity': 85, 'rainfall_mm': 310,
             'rice_phase': 'Growing (wettest)', 'straw_available': False},
            {'month': 'Oct', 'avg_temp': 28, 'humidity': 82, 'rainfall_mm': 200,
             'rice_phase': 'Maturing', 'straw_available': False},
            {'month': 'Nov', 'avg_temp': 28, 'humidity': 72, 'rainfall_mm': 40,
             'rice_phase': 'Main harvest', 'straw_available': True},
            {'month': 'Dec', 'avg_temp': 27, 'humidity': 68, 'rainfall_mm': 15,
             'rice_phase': 'Post-harvest', 'straw_available': True},
        ]
    else:  # chiang_mai (northern highland, ~310m elevation)
        # Climate data: Thai Meteorological Department, Chiang Mai station
        # Cooler than central plain (~2-5°C), distinct dry season (Nov-Apr)
        # Single rice crop (Jul-Nov), burning season Feb-Apr is critical
        months = [
            {'month': 'Jan', 'avg_temp': 22, 'humidity': 62, 'rainfall_mm': 8,
             'rice_phase': 'Post-harvest (dry)', 'straw_available': True},
            {'month': 'Feb', 'avg_temp': 24, 'humidity': 55, 'rainfall_mm': 5,
             'rice_phase': 'Dry — burning season', 'straw_available': True},
            {'month': 'Mar', 'avg_temp': 28, 'humidity': 50, 'rainfall_mm': 15,
             'rice_phase': 'Dry — burning season', 'straw_available': True},
            {'month': 'Apr', 'avg_temp': 31, 'humidity': 58, 'rainfall_mm': 55,
             'rice_phase': 'Pre-monsoon', 'straw_available': True},
            {'month': 'May', 'avg_temp': 29, 'humidity': 72, 'rainfall_mm': 160,
             'rice_phase': 'Nursery preparation', 'straw_available': False},
            {'month': 'Jun', 'avg_temp': 28, 'humidity': 78, 'rainfall_mm': 140,
             'rice_phase': 'Transplanting', 'straw_available': False},
            {'month': 'Jul', 'avg_temp': 27, 'humidity': 80, 'rainfall_mm': 175,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Aug', 'avg_temp': 27, 'humidity': 82, 'rainfall_mm': 230,
             'rice_phase': 'Growing', 'straw_available': False},
            {'month': 'Sep', 'avg_temp': 27, 'humidity': 84, 'rainfall_mm': 250,
             'rice_phase': 'Growing (wettest)', 'straw_available': False},
            {'month': 'Oct', 'avg_temp': 26, 'humidity': 80, 'rainfall_mm': 130,
             'rice_phase': 'Maturing', 'straw_available': False},
            {'month': 'Nov', 'avg_temp': 24, 'humidity': 68, 'rainfall_mm': 40,
             'rice_phase': 'Harvest begins', 'straw_available': True},
            {'month': 'Dec', 'avg_temp': 22, 'humidity': 63, 'rainfall_mm': 12,
             'rice_phase': 'Harvest complete', 'straw_available': True},
        ]
    
    # Compute mushroom suitability for each month
    for m in months:
        temp_score = max(0, 1 - abs(m['avg_temp'] - 32.5) / 10) * 100
        humidity_score = max(0, min(100, (m['humidity'] - 50) / 40 * 100))
        rain_penalty = max(0, (m['rainfall_mm'] - 150) / 200 * 30) if m['rainfall_mm'] > 150 else 0
        
        suitability = (temp_score * 0.4 + humidity_score * 0.3 - rain_penalty) * (1 if m['straw_available'] else 0)
        
        m['temp_score'] = round(temp_score, 0)
        m['humidity_score'] = round(humidity_score, 0)
        m['mushroom_suitability'] = round(max(0, suitability), 1)
        m['recommendation'] = (
            '🟢 GROW' if suitability >= 40 and m['straw_available']
            else '🟡 POSSIBLE' if suitability >= 20 and m['straw_available']
            else '⚪ LOW TEMP' if m['straw_available'] and m['avg_temp'] < 25
            else '🔴 NO STRAW' if not m['straw_available']
            else '🔴 UNSUITABLE'
        )
    
    return months


# ================================================================
# COMPETITIVE ANALYSIS ENGINE
# ================================================================

def compute_competitive_comparison() -> List[Dict]:
    """
    Compare our system against alternatives.
    Sources: Thai government data, Happy Farmer website, NGO reports
    """
    return [
        {
            'method': 'Open Burning (status quo)',
            'cost_per_rai': 0,
            'revenue_per_rai': 0,
            'time_days': 0.5,
            'environmental': 'Very Negative',
            'legal_risk': 'High (fines 2,000-100,000 ฿)',
            'equipment_cost': 0,
            'be_range': 'N/A',
            'scalability': 'Instant',
            'co2eq_per_rai_kg': 42.76,
            'net_impact_per_rai': -2000,  # expected fine
        },
        {
            'method': 'Zero-Burn Steam + Mushroom',
            'cost_per_rai': 1186,
            'revenue_per_rai': 3159,
            'time_days': 14,
            'environmental': 'Positive (carbon credits)',
            'legal_risk': 'None',
            'equipment_cost': 26550,
            'be_range': '8-15%',
            'scalability': 'Village cooperative',
            'co2eq_per_rai_kg': 0,
            'net_impact_per_rai': 1973,
        },
        {
            'method': 'Trichoderma Bio-decomposer (Gov)',
            'cost_per_rai': 500,
            'revenue_per_rai': 0,
            'time_days': 20,
            'environmental': 'Positive',
            'legal_risk': 'None',
            'equipment_cost': 0,
            'be_range': 'N/A',
            'scalability': 'Government distribution',
            'co2eq_per_rai_kg': 0,
            'net_impact_per_rai': -500,  # cost only, no revenue
        },
        {
            'method': 'Happy Farmer Machine',
            'cost_per_rai': 200,
            'revenue_per_rai': 0,
            'time_days': 1,
            'environmental': 'Positive',
            'legal_risk': 'None',
            'equipment_cost': 500000,
            'be_range': 'N/A (mulching)',
            'scalability': 'Requires capital',
            'co2eq_per_rai_kg': 0,
            'net_impact_per_rai': -200,
        },
        {
            'method': 'Traditional Composting',
            'cost_per_rai': 400,
            'revenue_per_rai': 0,
            'time_days': 30,
            'environmental': 'Positive',
            'legal_risk': 'None',
            'equipment_cost': 0,
            'be_range': 'N/A',
            'scalability': 'Labor intensive',
            'co2eq_per_rai_kg': 0,
            'net_impact_per_rai': -400,
        },
        {
            'method': 'Do Nothing (leave in field)',
            'cost_per_rai': 0,
            'revenue_per_rai': 0,
            'time_days': 45,
            'environmental': 'Neutral (slow decomp)',
            'legal_risk': 'None',
            'equipment_cost': 0,
            'be_range': 'N/A',
            'scalability': 'Slow turnaround',
            'co2eq_per_rai_kg': 5,
            'net_impact_per_rai': -500,  # delayed planting cost
        },
    ]


# ================================================================
# ROUND 2: BIOLOGICAL SCIENCE ENGINES
# ================================================================

def compute_spawn_rate_optimization(
    substrate_kg: float = 585.0,
    spawn_rates_pct: List[float] = None,
    spawn_cost_per_kg: float = 80.0,  # ฿/kg typical Thai market
) -> List[Dict]:
    """
    Spawn rate vs colonization speed vs cost vs BE optimization.
    
    Research data (verified):
    - Recommended: 1-5% of wet substrate weight
    - Typical: 5-10% = 50-100 kg per ton prepared straw
    - Practical: 600g per 40kg dry straw = 1.5%
    - >10% shows no significant BE increase
    - Higher rates: faster colonization but diminishing returns
    - Liquid spawn: faster than grain spawn
    
    Colonization time model:
    - 1%: 15 days (slow, higher contamination risk)
    - 2%: 12 days (standard)
    - 5%: 9 days (accelerated)  
    - 10%: 8 days (minimal gain vs 5%)
    
    Sources: MDPI, ICAR, Khon Kaen University
    """
    if spawn_rates_pct is None:
        spawn_rates_pct = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0]
    
    results = []
    for rate in spawn_rates_pct:
        spawn_kg = substrate_kg * rate / 100
        spawn_cost = spawn_kg * spawn_cost_per_kg
        
        # Colonization time: logarithmic decay with spawn rate
        # t = 18 / (1 + 0.5 * rate)  fitted to research data
        colon_days = max(7, 18 / (1 + 0.5 * rate))
        
        # BE modifier: peaks around 5%, diminishing above
        if rate <= 5:
            be_modifier = 0.85 + 0.03 * rate  # rises to 1.0 at 5%
        else:
            be_modifier = 1.0 - 0.005 * (rate - 5)  # slight decline above 5%
        
        # Contamination risk: lower with faster colonization
        contam_risk = max(2, 15 - colon_days * 0.8)
        
        base_be = 12.0  # %
        effective_be = base_be * be_modifier
        yield_kg = substrate_kg * effective_be / 100
        revenue = yield_kg * 55  # ฿/kg
        profit = revenue - spawn_cost
        roi_spawn = (revenue - spawn_cost) / spawn_cost if spawn_cost > 0 else 0
        
        results.append({
            'spawn_rate_pct': rate,
            'spawn_kg': round(spawn_kg, 1),
            'spawn_cost_baht': round(spawn_cost, 0),
            'colonization_days': round(colon_days, 1),
            'be_modifier': round(be_modifier, 3),
            'effective_be_pct': round(effective_be, 2),
            'yield_kg': round(yield_kg, 1),
            'contamination_risk_pct': round(contam_risk, 1),
            'revenue_baht': round(revenue, 0),
            'profit_after_spawn': round(profit, 0),
            'roi_on_spawn': round(roi_spawn, 1),
            'recommendation': (
                '⚠️ TOO LOW' if rate < 1 else
                '🟡 ECONOMICAL' if rate < 2 else
                '🟢 OPTIMAL' if rate <= 5 else
                '🟡 DIMINISHING' if rate <= 10 else
                '🔴 WASTEFUL'
            ),
        })
    
    return results


def compute_moisture_optimization(
    moisture_levels: List[float] = None,
    soak_times_hr: List[float] = None,
) -> Dict:
    """
    Substrate moisture content effect on V. volvacea yield.
    
    Research data (ICAR, MASU Journal):
    - 60% moisture: optimal BE = 12.1%
    - Top layer 30% + base 60%: BE = 14.1%
    - >70%: anaerobic risk, bacterial contamination
    - <50%: insufficient for mycelium growth
    
    Soaking time vs moisture:
    - 2-4 hrs (chopped): 50-55% moisture
    - 12-18 hrs: 58-65% moisture
    - 24 hrs: 60-65% moisture (standard)
    - 24 hrs + lime: pH 7.5-8.0, better stability
    """
    if moisture_levels is None:
        moisture_levels = list(range(35, 86, 5))
    
    moisture_data = []
    for mc in moisture_levels:
        # BE response curve (Gaussian around 62%)
        be_factor = np.exp(-((mc - 62) / 8.0) ** 2)
        if mc > 75:
            be_factor *= max(0, 1 - (mc - 75) / 10)  # anaerobic penalty
        
        # Contamination risk
        if mc < 50:
            contam = 5  # low moisture = low contam but low yield
        elif mc <= 65:
            contam = 8 + (mc - 50) * 0.3  # moderate
        else:
            contam = 10 + (mc - 65) * 2  # rising sharply above 65%
        
        base_be = 14.0  # max achievable
        effective_be = base_be * be_factor
        
        moisture_data.append({
            'moisture_pct': mc,
            'be_factor': round(be_factor, 3),
            'effective_be_pct': round(effective_be, 2),
            'contamination_risk_pct': round(min(contam, 50), 1),
            'quality': (
                '🔴 TOO DRY' if mc < 45 else
                '🟡 LOW' if mc < 55 else
                '🟢 OPTIMAL' if mc <= 67 else
                '🟡 HIGH' if mc <= 75 else
                '🔴 WATERLOGGED'
            ),
        })
    
    if soak_times_hr is None:
        soak_times_hr = [1, 2, 4, 6, 8, 12, 18, 24, 36, 48]
    
    soak_data = []
    for t in soak_times_hr:
        # Moisture absorption follows exponential decay
        moisture = 65 - 30 * np.exp(-t / 8)
        
        soak_data.append({
            'soak_hours': t,
            'final_moisture_pct': round(moisture, 1),
            'status': (
                '🔴 UNDER-SOAKED' if moisture < 55 else
                '🟡 ACCEPTABLE' if moisture < 58 else
                '🟢 OPTIMAL' if moisture <= 65 else
                '🔴 OVER-SOAKED'
            ),
        })
    
    return {'moisture_curve': moisture_data, 'soak_curve': soak_data}


def compute_indoor_outdoor_comparison(
    substrate_kg: float = 585.0,
    grow_area_m2: float = 20.0,
) -> List[Dict]:
    """
    Indoor vs outdoor cultivation yield comparison.
    
    Research data (ResearchGate, MASU Journal):
    - Indoor cotton waste: 5.38 kg/m²
    - Indoor rice straw: 4.71 kg/m²
    - Outdoor cotton waste: 1.79 kg/m² 
    - Outdoor rice straw: 1.73 kg/m²
    - Indoor = 2.7-3× outdoor yield
    
    Setup cost comparison:
    - Outdoor: minimal (shade cloth ฿500-1000)
    - Simple shelter: bamboo + plastic ฿3,000-5,000
    - Polyhouse: ฿20,000-40,000
    - Full indoor: ฿50,000-100,000+
    """
    scenarios = [
        {
            'method': 'Open outdoor (traditional)',
            'yield_per_m2': 1.73,
            'be_pct': 8.5,
            'setup_cost': 500,
            'monthly_cost': 0,
            'temp_control': 'None',
            'humidity_control': 'None',
            'contamination_risk_pct': 25,
            'season_dependent': True,
            'cycles_per_year': 2,
        },
        {
            'method': 'Shade structure (bamboo)',
            'yield_per_m2': 2.5,
            'be_pct': 10.0,
            'setup_cost': 3000,
            'monthly_cost': 100,
            'temp_control': 'Shade only',
            'humidity_control': 'Manual watering',
            'contamination_risk_pct': 18,
            'season_dependent': True,
            'cycles_per_year': 3,
        },
        {
            'method': 'Polyhouse (plastic)',
            'yield_per_m2': 3.8,
            'be_pct': 13.0,
            'setup_cost': 25000,
            'monthly_cost': 500,
            'temp_control': 'Partial (venting)',
            'humidity_control': 'Misting',
            'contamination_risk_pct': 10,
            'season_dependent': False,
            'cycles_per_year': 8,
        },
        {
            'method': 'Indoor controlled (full)',
            'yield_per_m2': 4.71,
            'be_pct': 15.0,
            'setup_cost': 80000,
            'monthly_cost': 2000,
            'temp_control': '32-35°C maintained',
            'humidity_control': '80-90% maintained',
            'contamination_risk_pct': 5,
            'season_dependent': False,
            'cycles_per_year': 12,
        },
    ]
    
    for s in scenarios:
        total_yield = s['yield_per_m2'] * grow_area_m2
        annual_yield = total_yield * s['cycles_per_year']
        annual_revenue = annual_yield * 55  # ฿/kg
        annual_cost = s['setup_cost'] / 3 + s['monthly_cost'] * 12  # 3yr amortize
        annual_profit = annual_revenue - annual_cost
        s['total_yield_kg'] = round(total_yield, 1)
        s['annual_yield_kg'] = round(annual_yield, 1)
        s['annual_revenue'] = round(annual_revenue, 0)
        s['annual_cost'] = round(annual_cost, 0)
        s['annual_profit'] = round(annual_profit, 0)
        s['payback_cycles'] = round(s['setup_cost'] / (total_yield * 55 - s['monthly_cost'] * 0.5), 1) if total_yield > 0 else 999
    
    return scenarios


def compute_harvest_labor_model(
    total_yield_kg: float = 57.0,
    flushes: int = 3,
    labor_rate_per_day: float = 350.0,  # ฿/day Thai min wage
) -> List[Dict]:
    """
    Multi-flush harvest labor cost model.
    
    Each flush requires picking labor:
    - Flush 1: 2-3 days of picking (70% yield)
    - Flush 2: 1-2 days (22% yield)
    - Flush 3: 0.5-1 days (8% yield)
    
    Labor rate: Thai minimum wage ~350 ฿/day (Isaan region)
    """
    flush_data = [
        {'flush': 1, 'pct_yield': 0.70, 'pick_days': 2.5, 'quality': 'Premium (egg stage)'},
        {'flush': 2, 'pct_yield': 0.22, 'pick_days': 1.5, 'quality': 'Good (mixed stages)'},
        {'flush': 3, 'pct_yield': 0.08, 'pick_days': 0.8, 'quality': 'Mixed (some open caps)'},
    ][:flushes]
    
    results = []
    total_labor = 0
    total_revenue = 0
    
    for f in flush_data:
        flush_yield = total_yield_kg * f['pct_yield']
        labor_cost = f['pick_days'] * labor_rate_per_day
        # Price varies by quality
        price_per_kg = 60 if f['flush'] == 1 else 50 if f['flush'] == 2 else 35
        revenue = flush_yield * price_per_kg
        profit = revenue - labor_cost
        total_labor += labor_cost
        total_revenue += revenue
        
        results.append({
            'flush': f['flush'],
            'yield_kg': round(flush_yield, 1),
            'quality': f['quality'],
            'pick_days': f['pick_days'],
            'labor_cost_baht': round(labor_cost, 0),
            'price_per_kg': price_per_kg,
            'revenue_baht': round(revenue, 0),
            'flush_profit': round(profit, 0),
            'worth_harvesting': profit > 0,
        })
    
    return results


# ================================================================
# ROUND 3: ENVIRONMENTAL & SEASONAL ENGINES
# ================================================================

def compute_straw_degradation(
    weeks_stored: List[int] = None,
    storage_type: str = 'open_field',
) -> List[Dict]:
    """
    Rice straw nutrient degradation over storage time.
    
    Research data:
    - 20-30% dry matter loss in tropical storage (Bangladesh/China studies)
    - 93.5% potassium lost in first month
    - Cellulose: 68-79% remains after 50 days (aerobic)
    - Hemicellulose more vulnerable than cellulose
    - Covered storage: ~50% slower degradation
    - Baled vs loose: baled preserves 20% better
    
    Sources: Researchers Links, NIH, Agriculture Journals CZ
    """
    if weeks_stored is None:
        weeks_stored = list(range(0, 25))  # 0-24 weeks (6 months)
    
    # Storage type multipliers
    storage_factors = {
        'open_field': 1.0,      # baseline - worst
        'covered_pile': 0.5,    # 50% slower degradation
        'baled_covered': 0.35,  # best practical option
        'indoor_dry': 0.2,      # ideal but costly
    }
    factor = storage_factors.get(storage_type, 1.0)
    
    results = []
    for w in weeks_stored:
        # Exponential decay models (fitted to research data)
        days = w * 7
        
        # Dry matter loss: ~25% in 12 weeks for open field
        dm_remaining = 100 * np.exp(-0.003 * days * factor)
        
        # Cellulose: slower loss (structural)
        cellulose_remaining = 100 * np.exp(-0.001 * days * factor)
        
        # Hemicellulose: faster loss
        hemicellulose_remaining = 100 * np.exp(-0.002 * days * factor)
        
        # Potassium: very fast (93.5% lost in 4 weeks)
        k_remaining = 100 * np.exp(-0.04 * days * factor)
        
        # Nitrogen: moderate
        n_remaining = 100 * np.exp(-0.0015 * days * factor)
        
        # BE impact: proportional to cellulose + hemicellulose
        substrate_quality = (cellulose_remaining * 0.6 + hemicellulose_remaining * 0.4) / 100
        be_remaining_pct = round(substrate_quality * 100, 1)
        
        results.append({
            'weeks': w,
            'dry_matter_pct': round(dm_remaining, 1),
            'cellulose_pct': round(cellulose_remaining, 1),
            'hemicellulose_pct': round(hemicellulose_remaining, 1),
            'potassium_pct': round(k_remaining, 1),
            'nitrogen_pct': round(n_remaining, 1),
            'be_quality_pct': be_remaining_pct,
            'assessment': (
                '🟢 FRESH' if w <= 2 else
                '🟢 GOOD' if be_remaining_pct >= 90 else
                '🟡 ACCEPTABLE' if be_remaining_pct >= 75 else
                '🟠 DEGRADED' if be_remaining_pct >= 60 else
                '🔴 POOR'
            ),
        })
    
    return results


def compute_rainfall_impact(
    rainfall_mm_per_week: float = 50.0,
    growing_method: str = 'outdoor',
) -> Dict:
    """
    Rainfall impact on outdoor mushroom cultivation success.
    
    Effects:
    - Light rain (0-30mm/wk): beneficial humidity boost
    - Moderate rain (30-80mm/wk): manageable with drainage
    - Heavy rain (80-150mm/wk): flooding risk, dilution
    - Extreme rain (>150mm/wk): crop loss likely
    
    Mitigation:
    - Raised beds: +30mm tolerance
    - Plastic cover: +50mm tolerance  
    - Full shelter: rain immune
    """
    method_tolerance = {
        'outdoor': 0,
        'raised_bed': 30,
        'plastic_cover': 50,
        'shelter': 300,  # essentially immune
    }
    tolerance_bonus = method_tolerance.get(growing_method, 0)
    effective_rain = max(0, rainfall_mm_per_week - tolerance_bonus)
    
    # Yield modifier based on effective rainfall
    if effective_rain <= 30:
        yield_modifier = 1.0 + effective_rain * 0.003  # slight humidity benefit
    elif effective_rain <= 80:
        yield_modifier = 1.09 - (effective_rain - 30) * 0.005
    elif effective_rain <= 150:
        yield_modifier = 0.84 - (effective_rain - 80) * 0.008
    else:
        yield_modifier = max(0, 0.28 - (effective_rain - 150) * 0.003)
    
    # Contamination modifier
    contam_base = 5
    contam_rain = contam_base + max(0, effective_rain - 40) * 0.15
    
    return {
        'rainfall_mm_week': rainfall_mm_per_week,
        'growing_method': growing_method,
        'effective_rainfall': effective_rain,
        'yield_modifier': round(yield_modifier, 3),
        'contamination_risk_pct': round(min(contam_rain, 60), 1),
        'assessment': (
            '🟢 BENEFICIAL' if effective_rain <= 30 else
            '🟡 MANAGEABLE' if effective_rain <= 80 else
            '🟠 RISKY' if effective_rain <= 150 else
            '🔴 CROP LOSS'
        ),
    }


def compute_temperature_corridor(
    ambient_temps_c: List[float] = None,
    shelter_type: str = 'none',
) -> List[Dict]:
    """
    Temperature corridor analysis: ambient vs shelter conditions.
    
    Shelter heat retention/reduction effects:
    - None: direct ambient
    - Shade cloth: -2-3°C from peak, +1°C overnight
    - Plastic house: +3-5°C from ambient (greenhouse effect)
    - Indoor: controllable (32-35°C target)
    """
    if ambient_temps_c is None:
        ambient_temps_c = list(range(15, 43))
    
    results = []
    for t_amb in ambient_temps_c:
        if shelter_type == 'none':
            t_eff = t_amb
        elif shelter_type == 'shade_cloth':
            t_eff = t_amb - 2 if t_amb > 30 else t_amb + 1
        elif shelter_type == 'plastic_house':
            t_eff = t_amb + 4 if t_amb < 30 else t_amb + 2
        else:  # indoor
            t_eff = 33.0  # controlled
        
        # Growth rate at effective temp (Gaussian around 32.5°C)
        growth_factor = np.exp(-((t_eff - 32.5) / 5.0) ** 2)
        if t_eff < 20 or t_eff > 42:
            growth_factor = 0.0
        
        results.append({
            'ambient_c': t_amb,
            'effective_c': round(t_eff, 1),
            'growth_factor': round(growth_factor, 3),
            'growth_pct': round(growth_factor * 100, 1),
            'status': (
                '🔴 DEATH' if growth_factor < 0.05 else
                '🟠 STRESS' if growth_factor < 0.3 else
                '🟡 SUBOPTIMAL' if growth_factor < 0.7 else
                '🟢 GOOD' if growth_factor < 0.9 else
                '🟢 OPTIMAL'
            ),
        })
    
    return results


# ================================================================
# ROUND 4: ADVANCED ECONOMICS ENGINES
# ================================================================

def compute_cooperative_model(
    num_farmers: int = 10,
    rai_per_farmer: float = 15.0,
    equipment_cost: float = 26550.0,
    sharing_ratio: float = 1.0,  # 1.0 = full shared set
) -> Dict:
    """
    Cooperative equipment sharing economics.
    
    Research data (Thai farmer cooperatives):
    - Equipment sharing reduces investment by 50%
    - Labor/machinery costs down 15%
    - BAAC lending: MLR 6.025% (as of Jan 2026)
    - Cooperative groups get preferential rates: ~4-5%
    - Government Mega Farm policy encourages pooling
    
    Equipment for Zero-Burn (per set):
    - Rice husk boiler: ฿8,500
    - Copper coil system: ฿5,500
    - Steam distributor: ฿3,500
    - Spawn inoculation tools: ฿2,500
    - Growing shelters: ฿4,050
    - Misc (hoses, thermometers): ฿2,500
    Total: ฿26,550
    
    Shared model: 1 boiler + coil serves 3-5 farmers (sequential use)
    """
    # Individual model
    individual_cost = equipment_cost
    individual_annual_profit = rai_per_farmer * 1973  # ฿/rai from our simulation
    individual_payback_years = individual_cost / individual_annual_profit if individual_annual_profit > 0 else 99
    
    # Cooperative model
    # Shared equipment: boiler + coil = ฿14,000 shared among farmers
    shared_equipment = 14000  # boiler + coil
    personal_equipment = equipment_cost - shared_equipment  # shelters, tools etc.
    coop_sets_needed = max(1, num_farmers // 4)  # 1 set per 4 farmers
    total_shared_cost = shared_equipment * coop_sets_needed
    per_farmer_shared = total_shared_cost / num_farmers
    per_farmer_total = per_farmer_shared + personal_equipment
    
    # Equipment sharing discount on operations
    coop_annual_profit = rai_per_farmer * 1973 * 1.05  # 5% efficiency gain from coop
    coop_payback_years = per_farmer_total / coop_annual_profit if coop_annual_profit > 0 else 99
    
    # BAAC loan scenarios
    loan_amount = per_farmer_total
    baac_rate = 0.06025  # MLR
    coop_rate = 0.045  # cooperative preferential rate
    loan_years = 3
    
    # Simple interest (BAAC style for small loans)
    individual_repayment = individual_cost * (1 + baac_rate * loan_years)
    coop_repayment = loan_amount * (1 + coop_rate * loan_years)
    
    return {
        'num_farmers': num_farmers,
        'rai_per_farmer': rai_per_farmer,
        'individual': {
            'equipment_cost': round(individual_cost, 0),
            'annual_profit': round(individual_annual_profit, 0),
            'payback_years': round(individual_payback_years, 2),
            'loan_repayment_3yr': round(individual_repayment, 0),
            'monthly_payment': round(individual_repayment / 36, 0),
        },
        'cooperative': {
            'shared_sets_needed': coop_sets_needed,
            'per_farmer_cost': round(per_farmer_total, 0),
            'savings_vs_individual': round(individual_cost - per_farmer_total, 0),
            'savings_pct': round((1 - per_farmer_total / individual_cost) * 100, 1),
            'annual_profit': round(coop_annual_profit, 0),
            'payback_years': round(coop_payback_years, 2),
            'loan_repayment_3yr': round(coop_repayment, 0),
            'monthly_payment': round(coop_repayment / 36, 0),
        },
        'total_village': {
            'total_rai': num_farmers * rai_per_farmer,
            'total_equipment_individual': round(num_farmers * individual_cost, 0),
            'total_equipment_coop': round(total_shared_cost + num_farmers * personal_equipment, 0),
            'village_savings': round(num_farmers * individual_cost - (total_shared_cost + num_farmers * personal_equipment), 0),
            'annual_village_profit': round(num_farmers * coop_annual_profit, 0),
            'monthly_mushroom_kg': round(num_farmers * rai_per_farmer * 57.2 / 12, 0),
        },
    }


def compute_market_absorption(
    monthly_production_kg: float = 500.0,
    village_population: int = 500,
    nearby_villages: int = 3,
    market_town_population: int = 5000,
) -> Dict:
    """
    Can local markets absorb the mushroom supply?
    
    Thai mushroom consumption data:
    - Per capita: ~2.5 kg/year (straw mushrooms)
    - Market price: retail ฿40-80/kg, wholesale ฿30-50/kg
    - Cannery price: ฿12-16/kg (lower but guaranteed)
    - Thailand exports to Laos, Myanmar, China, Vietnam
    
    Distribution channels:
    - Village wet markets: 20-30% of production
    - Nearby markets: 30-40%
    - Market town: 20-30%
    - Wholesale/cannery: remainder
    """
    total_local_pop = village_population + nearby_villages * 300 + market_town_population
    local_demand_kg_month = total_local_pop * 2.5 / 12  # per capita annual / 12
    
    absorption_pct = min(100, (local_demand_kg_month / monthly_production_kg) * 100) if monthly_production_kg > 0 else 0
    surplus_kg = max(0, monthly_production_kg - local_demand_kg_month)
    
    # Channel breakdown
    channels = [
        {
            'channel': 'Village wet market',
            'capacity_kg': village_population * 2.5 / 12 * 0.3,
            'price_per_kg': 60,
            'reliability': 'Daily, walk-in',
        },
        {
            'channel': 'Nearby village markets',
            'capacity_kg': nearby_villages * 300 * 2.5 / 12 * 0.25,
            'price_per_kg': 55,
            'reliability': 'Weekly markets',
        },
        {
            'channel': 'Market town',
            'capacity_kg': market_town_population * 2.5 / 12 * 0.15,
            'price_per_kg': 50,
            'reliability': 'Daily, higher transport cost',
        },
        {
            'channel': 'Wholesale buyer',
            'capacity_kg': 500,  # typical wholesale lot/month
            'price_per_kg': 40,
            'reliability': 'Contract, reliable volume',
        },
        {
            'channel': 'Cannery (canned mushrooms)',
            'capacity_kg': 2000,  # large industrial capacity
            'price_per_kg': 15,
            'reliability': 'Guaranteed, lowest price',
        },
    ]
    
    for c in channels:
        c['capacity_kg'] = round(c['capacity_kg'], 0)
        c['monthly_revenue'] = round(min(c['capacity_kg'], monthly_production_kg * 0.3) * c['price_per_kg'], 0)
    
    # Optimal allocation
    remaining = monthly_production_kg
    allocation = []
    for c in channels:
        alloc = min(remaining, c['capacity_kg'])
        allocation.append({
            'channel': c['channel'],
            'allocated_kg': round(alloc, 0),
            'revenue': round(alloc * c['price_per_kg'], 0),
            'price_per_kg': c['price_per_kg'],
        })
        remaining -= alloc
        if remaining <= 0:
            break
    
    total_rev = sum(a['revenue'] for a in allocation)
    blended_price = total_rev / monthly_production_kg if monthly_production_kg > 0 else 0
    
    return {
        'monthly_production_kg': monthly_production_kg,
        'local_demand_kg_month': round(local_demand_kg_month, 0),
        'absorption_pct': round(absorption_pct, 1),
        'surplus_kg': round(surplus_kg, 0),
        'channels': channels,
        'optimal_allocation': allocation,
        'blended_price_per_kg': round(blended_price, 1),
        'total_monthly_revenue': round(total_rev, 0),
        'market_status': (
            '🟢 EASILY ABSORBED' if absorption_pct >= 150 else
            '🟢 WELL MATCHED' if absorption_pct >= 100 else
            '🟡 TIGHT — diversify channels' if absorption_pct >= 70 else
            '🟠 OVERSUPPLY — need wholesale/cannery' if absorption_pct >= 40 else
            '🔴 SIGNIFICANT SURPLUS'
        ),
    }


def compute_year_round_operations(
    rai_available: float = 15.0,
    region: str = 'isaan',
) -> List[Dict]:
    """
    Year-round operation model: how many cycles and when.
    
    Cycle = 14-22 days (14 min, 22 with all 3 flushes)
    Turnaround = 3-5 days (bed cleanup, re-sterilization)
    
    Constraints:
    - Need straw (post-harvest Nov-Feb in Isaan)
    - Temperature must be 25-38°C
    - Cannot grow during transplanting (May-Jun)
    
    With stored straw + shelter:
    - Isaan: 4-6 cycles/year possible
    - Central: 6-10 cycles/year possible
    """
    seasonal = compute_seasonal_windows(region)
    
    results = []
    annual_yield = 0
    annual_revenue = 0
    annual_cost = 0
    cycle_count = 0
    
    for m in seasonal:
        # Can we grow this month?
        can_grow = m['mushroom_suitability'] > 20 or m['straw_available']
        
        # With stored straw, extend season
        # But still need acceptable temperature
        temp_ok = 23 <= m['avg_temp'] <= 38
        straw_ok = m['straw_available']
        
        # With storage: use straw up to 12 weeks old = 3 months past harvest
        straw_window = (
            m['month'] in ['Nov', 'Dec', 'Jan', 'Feb', 'Mar'] if region == 'isaan'
            else m['month'] in ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'] if region == 'chiang_mai'
            else True  # central
        )
        
        cycles_this_month = 0
        if temp_ok and (straw_ok or straw_window):
            # Days available / (cycle + turnaround)
            cycle_length = 18  # 14 growing + 4 turnaround
            cycles_this_month = 30 // cycle_length  # 1-2 per month
            
            # Yield modifier for temperature
            temp_factor = np.exp(-((m['avg_temp'] - 32.5) / 5.0) ** 2)
            yield_per_cycle = rai_available * 57.2 * temp_factor / (rai_available)  # per rai
            total_yield = yield_per_cycle * rai_available * cycles_this_month
            revenue = total_yield * 55
            cost = rai_available * 1186 / 12 * cycles_this_month  # monthly portion
            
            annual_yield += total_yield
            annual_revenue += revenue
            annual_cost += cost
            cycle_count += cycles_this_month
        
        results.append({
            'month': m['month'],
            'avg_temp': m['avg_temp'],
            'humidity': m['humidity'],
            'can_grow': temp_ok and (straw_ok or straw_window),
            'straw_source': 'Fresh' if straw_ok else ('Stored' if straw_window else 'None'),
            'cycles': cycles_this_month,
            'monthly_yield_kg': round(total_yield if cycles_this_month > 0 else 0, 1),
            'monthly_revenue': round(revenue if cycles_this_month > 0 else 0, 0),
        })
    
    # Add summary
    for r in results:
        r['annual_total_yield'] = round(annual_yield, 0)
        r['annual_total_revenue'] = round(annual_revenue, 0)
        r['annual_total_cost'] = round(annual_cost, 0)
        r['annual_total_profit'] = round(annual_revenue - annual_cost, 0)
        r['total_cycles'] = cycle_count
    
    return results


# ================================================================
# ROUND 5: TECHNOLOGY & SCALE
# ================================================================

# IPCC 2019 Emission Factors
CH4_EF = 2.7     # kg CH₄ per ton dry straw
N2O_EF = 0.07    # kg N₂O per ton dry straw
GWP_CH4 = 28     # 100-year GWP
GWP_N2O = 265    # 100-year GWP


def compute_carbon_credits_v2(
    n_rai: float = 15,
    carbon_price_thb: float = 175,
    straw_per_rai: float = 650,
    burn_fraction: float = 0.70,
    include_black_carbon: bool = False,
    include_soil_carbon: bool = False,
    cooperative_size: int = 10,
    verification_method: str = 'iot',
) -> Dict:
    """
    Enhanced carbon credit model with T-VER pricing tiers and verification costs.
    
    Sources:
    - IPCC 2019 Vol.4 Ch.2 Table 2.5: CH₄ = 2.7 g/kg, N₂O = 0.07 g/kg
    - T-VER avg price Q1 FY2025: 175 ฿/tCO₂eq (Nation Thailand)
    - Ag sector T-VER range: 300-2,076 ฿/tCO₂eq
    - TGO verification cost: ~50,000-150,000 ฿ per project
    - MRV (manual): ~30,000 ฿/yr; IoT MRV: ~8,000 ฿/yr (after setup)
    """
    # Per-rai emissions avoided
    straw_burned_tons = (straw_per_rai * burn_fraction) / 1000
    
    ch4_co2eq = straw_burned_tons * CH4_EF * GWP_CH4  # kg CO₂eq
    n2o_co2eq = straw_burned_tons * N2O_EF * GWP_N2O  # kg CO₂eq
    base_co2eq_kg = ch4_co2eq + n2o_co2eq  # ~52.7 kg/rai
    
    # Optional: black carbon (short-lived climate forcer)
    bc_co2eq_kg = straw_burned_tons * 0.6 * 900 if include_black_carbon else 0  # ~245 kg
    # Optional: soil carbon sequestration from SMS incorporation
    soil_co2eq_kg = 15.0 if include_soil_carbon else 0  # conservative estimate kg/rai/yr
    
    total_co2eq_kg = base_co2eq_kg + bc_co2eq_kg + soil_co2eq_kg
    total_tco2eq_per_rai = total_co2eq_kg / 1000
    
    # Scale to cooperative
    total_rai = n_rai * cooperative_size
    total_tco2eq = total_tco2eq_per_rai * total_rai
    
    # Revenue
    gross_revenue = total_tco2eq * carbon_price_thb
    
    # Verification costs depend on method
    verification_costs = {
        'manual': {'setup': 0, 'annual': 30000, 'tgo_fee': 100000},
        'iot': {'setup': 15000, 'annual': 8000, 'tgo_fee': 80000},
        'satellite': {'setup': 0, 'annual': 5000, 'tgo_fee': 120000},
    }
    v = verification_costs.get(verification_method, verification_costs['manual'])
    total_verification = v['annual'] + v['tgo_fee'] / 5  # amortize TGO over 5 years
    
    net_revenue = gross_revenue - total_verification
    revenue_per_rai = net_revenue / total_rai if total_rai > 0 else 0
    
    # Pricing tiers
    price_scenarios = []
    for label, price in [('Low (waste mgmt)', 100), ('Average T-VER', 175), 
                          ('Ag sector avg', 500), ('Premium T-VER', 1000), ('Premium ag', 2076)]:
        rev = total_tco2eq * price
        net = rev - total_verification
        price_scenarios.append({
            'tier': label,
            'price_per_tco2eq': price,
            'gross_revenue': round(rev),
            'net_revenue': round(net),
            'per_rai': round(net / total_rai if total_rai > 0 else 0),
            'viable': net > 0,
        })
    
    return {
        'per_rai': {
            'ch4_co2eq_kg': round(ch4_co2eq, 2),
            'n2o_co2eq_kg': round(n2o_co2eq, 2),
            'bc_co2eq_kg': round(bc_co2eq_kg, 2),
            'soil_co2eq_kg': round(soil_co2eq_kg, 2),
            'total_co2eq_kg': round(total_co2eq_kg, 2),
            'total_tco2eq': round(total_tco2eq_per_rai, 4),
        },
        'cooperative': {
            'total_rai': total_rai,
            'total_tco2eq': round(total_tco2eq, 2),
            'gross_revenue': round(gross_revenue),
            'verification_cost': round(total_verification),
            'net_revenue': round(net_revenue),
            'revenue_per_rai': round(revenue_per_rai, 1),
            'revenue_per_farmer': round(net_revenue / cooperative_size if cooperative_size > 0 else 0),
        },
        'price_scenarios': price_scenarios,
        'methodology_note': 'IPCC biogenic CO₂ excluded. Only CH₄ + N₂O claimable under T-VER.',
        'verification_method': verification_method,
    }


def compute_iot_monitoring(
    num_sensor_nodes: int = 5,
    gateway_type: str = 'lora',
    monitoring_months: int = 12,
) -> Dict:
    """
    IoT MRV (Monitoring, Reporting, Verification) system cost model.
    
    Architecture:
    - Sensor nodes: ESP32 + DHT22 + PT100 + NEO-6M GPS
    - Communication: LoRa / WiFi / 4G
    - Gateway: LoRa concentrator or 4G router
    - Cloud: MQTT → TimescaleDB → Dashboard
    
    Sources:
    - Artronshop Thailand: DHT22 ฿42-169, ESP32 ฿150-300
    - PT100 RTD: ฿200-500
    - NEO-6M GPS module: ฿150-250
    - LoRa gateway: ฿3,000-17,000
    - LoRa modules (SX1276): ฿250-400
    """
    # Sensor node BOM
    node_components = {
        'ESP32 microcontroller': 250,
        'DHT22 (temp/humidity)': 100,
        'PT100 RTD (steam temp)': 350,
        'NEO-6M GPS module': 200,
        'Waterproof enclosure': 150,
        'Solar panel + battery': 450,
        'PCB + connectors': 100,
    }
    
    # Add communication module based on gateway type
    comm_costs = {
        'lora': {'module': ('LoRa SX1276 module', 300), 'gateway': ('LoRa gateway', 8000), 'monthly_data': 0},
        'wifi': {'module': ('WiFi (built-in ESP32)', 0), 'gateway': ('WiFi router', 1500), 'monthly_data': 0},
        '4g': {'module': ('4G SIM7600 module', 800), 'gateway': ('No gateway needed', 0), 'monthly_data': 200},
    }
    
    comm = comm_costs.get(gateway_type, comm_costs['lora'])
    node_components[comm['module'][0]] = comm['module'][1]
    
    node_cost = sum(node_components.values())
    total_nodes_cost = node_cost * num_sensor_nodes
    gateway_cost = comm['gateway'][1]
    monthly_data_cost = comm['monthly_data'] * num_sensor_nodes
    
    # Cloud/software costs
    cloud_monthly = 200  # basic MQTT broker + storage
    dashboard_setup = 3000  # one-time Grafana/custom dashboard
    
    # Total costs
    hardware_total = total_nodes_cost + gateway_cost + dashboard_setup
    monthly_operating = monthly_data_cost + cloud_monthly
    annual_operating = monthly_operating * 12
    
    # MRV value: cost savings vs manual verification
    manual_verification_annual = 30000  # person-days for manual data collection
    iot_verification_annual = annual_operating + (hardware_total / 36)  # amortize over 3 years
    mrv_savings = manual_verification_annual - iot_verification_annual
    
    # Data quality comparison
    data_comparison = [
        {'metric': 'Data frequency', 'manual': '1x/week', 'iot': 'Every 5 min', 'improvement': '2,016×'},
        {'metric': 'GPS accuracy', 'manual': '±50m (phone)', 'iot': '±2.5m (NEO-6M)', 'improvement': '20×'},
        {'metric': 'Temp accuracy', 'manual': '±2°C (thermometer)', 'iot': '±0.5°C (PT100)', 'improvement': '4×'},
        {'metric': 'Tamper risk', 'manual': 'High (paper logs)', 'iot': 'Low (cryptographic)', 'improvement': 'Digital proof'},
        {'metric': 'Annual cost', 'manual': f'฿{manual_verification_annual:,}', 'iot': f'฿{round(iot_verification_annual):,}', 'improvement': f'Save ฿{round(mrv_savings):,}'},
    ]
    
    return {
        'node_bom': node_components,
        'node_cost': round(node_cost),
        'total_nodes_cost': round(total_nodes_cost),
        'gateway_cost': round(gateway_cost),
        'hardware_total': round(hardware_total),
        'monthly_operating': round(monthly_operating),
        'annual_operating': round(annual_operating),
        'total_first_year': round(hardware_total + annual_operating),
        'mrv_savings_annual': round(mrv_savings),
        'payback_months': round(hardware_total / mrv_savings * 12) if mrv_savings > 0 else 999,
        'data_comparison': data_comparison,
        'sensors_data': [
            {'sensor': 'DHT22', 'measures': 'Air temp + humidity', 'range': '-40-80°C / 0-100%RH', 'cost': 100},
            {'sensor': 'PT100 RTD', 'measures': 'Steam temperature', 'range': '-200-600°C', 'cost': 350},
            {'sensor': 'NEO-6M GPS', 'measures': 'Location (MRV)', 'range': '±2.5m accuracy', 'cost': 200},
            {'sensor': 'Flow meter', 'measures': 'Water/steam flow', 'range': '0-100 ml/s', 'cost': 400},
        ],
        'gateway_type': gateway_type,
    }


def compute_tractor_operations(
    total_rai: float = 150,
    num_tractors: int = 1,
    treatment_time_per_rai_min: float = 45,
    travel_time_per_rai_min: float = 15,
    working_hours_per_day: float = 8,
    treatment_window_days: int = 14,
    tractor_cost: float = 426000,
    steam_unit_cost: float = 26550,
    fuel_cost_per_hour: float = 120,
    operator_daily_wage: float = 450,
) -> Dict:
    """
    Tractor scheduling model for cooperative steam treatment.
    
    Sources:
    - Kubota L-series: ฿426,000 starting (siamkubota.co.th)
    - Treatment speed: 45 min/rai (from feasibility study)
    - Diesel consumption: ~4-6 L/hr for L-series (EF = ฿30/L × 4L = ฿120/hr)
    - Treatment window: 14 days post-harvest before next planting
    """
    # Time calculations
    time_per_rai = treatment_time_per_rai_min + travel_time_per_rai_min  # min
    rai_per_hour = 60 / time_per_rai
    rai_per_day = rai_per_hour * working_hours_per_day
    rai_per_tractor_in_window = rai_per_day * treatment_window_days
    
    # Can we serve all rai?
    total_capacity = rai_per_tractor_in_window * num_tractors
    coverage_pct = min(100, (total_capacity / total_rai) * 100) if total_rai > 0 else 0
    tractors_needed = int(np.ceil(total_rai / rai_per_tractor_in_window))
    
    # Cost analysis
    days_needed = np.ceil(total_rai / (rai_per_day * num_tractors))
    fuel_total = days_needed * working_hours_per_day * fuel_cost_per_hour * num_tractors
    operator_total = days_needed * operator_daily_wage * num_tractors
    equipment_amortized = (tractor_cost + steam_unit_cost) * num_tractors / 5 / 2  # 5yr, 2 seasons
    total_operating_cost = fuel_total + operator_total + equipment_amortized
    cost_per_rai = total_operating_cost / total_rai if total_rai > 0 else 0
    
    # Revenue offset (mushroom revenue earned per rai treated)
    mushroom_revenue_per_rai = 57.2 * 55  # avg yield × avg price
    total_mushroom_revenue = mushroom_revenue_per_rai * min(total_rai, total_capacity)
    
    # Scheduling timeline
    schedule = []
    rai_done = 0
    for day in range(1, int(days_needed) + 1):
        daily_rai = min(rai_per_day * num_tractors, total_rai - rai_done)
        rai_done += daily_rai
        schedule.append({
            'day': day,
            'rai_treated': round(daily_rai, 1),
            'cumulative_rai': round(rai_done, 1),
            'pct_complete': round(rai_done / total_rai * 100, 1) if total_rai > 0 else 0,
        })
    
    return {
        'rai_per_hour': round(rai_per_hour, 1),
        'rai_per_day': round(rai_per_day, 1),
        'rai_per_tractor_window': round(rai_per_tractor_in_window, 0),
        'coverage_pct': round(coverage_pct, 1),
        'tractors_needed': tractors_needed,
        'days_needed': int(days_needed),
        'fuel_total': round(fuel_total),
        'operator_total': round(operator_total),
        'equipment_amortized': round(equipment_amortized),
        'total_operating_cost': round(total_operating_cost),
        'cost_per_rai': round(cost_per_rai),
        'mushroom_revenue_total': round(total_mushroom_revenue),
        'net_profit': round(total_mushroom_revenue - total_operating_cost),
        'schedule': schedule,
    }


def compute_autonomous_tractor_roi(
    total_rai: float = 150,
    cooperative_size: int = 10,
    current_labor_cost_per_day: float = 450,
    gps_autosteer_cost: float = 35000,
    full_autonomous_cost: float = 250000,
    working_hours_per_day: float = 8,
) -> List[Dict]:
    """
    ROI comparison: Manual tractor vs GPS auto-steer vs fully autonomous.
    
    Sources:
    - GPS auto-steer kit: ฿30,000-60,000 (Chinese-made, ecns.cn)
      - Reduces plowing cost from ฿1,600 → ฿200/rai
    - Kubota Value Line Steering: ~฿220,000 (Topcon, RTK)
    - Full autonomous (concept): ฿200,000-500,000 premium
    - Yanmar autonomous demo in Thailand (mynewsdesk.com)
    - Labor savings: 30% (auto-steer) to 80% (fully autonomous)
    - Fuel savings: 10% (auto-steer, less overlap) to 15% (autonomous, optimized paths)
    - Extended hours: autonomous can work 12-16 hrs/day vs 8 hrs manual
    """
    base_tractor = 426000  # Kubota L-series
    steam_unit = 26550
    
    scenarios = [
        {
            'mode': 'Manual Operation',
            'description': 'Human driver, standard tractor',
            'tractor_cost': base_tractor,
            'automation_cost': 0,
            'steam_unit': steam_unit,
            'operator_needed': True,
            'operators_per_day': 1,
            'working_hours': 8,
            'fuel_savings_pct': 0,
            'labor_savings_pct': 0,
            'accuracy_improvement': '0%',
            'overlap_waste_pct': 15,  # manual steering overlap
        },
        {
            'mode': 'GPS Auto-Steer',
            'description': 'GPS-guided steering, human supervision',
            'tractor_cost': base_tractor,
            'automation_cost': gps_autosteer_cost,
            'steam_unit': steam_unit,
            'operator_needed': True,
            'operators_per_day': 1,
            'working_hours': 10,  # easier to extend with GPS guidance
            'fuel_savings_pct': 10,
            'labor_savings_pct': 30,  # less skill needed
            'accuracy_improvement': '±2.5cm RTK',
            'overlap_waste_pct': 3,  # precise GPS = minimal overlap
        },
        {
            'mode': 'Semi-Autonomous',
            'description': 'Autonomous field operation, human monitors remotely',
            'tractor_cost': base_tractor,
            'automation_cost': full_autonomous_cost * 0.6,
            'steam_unit': steam_unit,
            'operator_needed': True,  # monitoring only
            'operators_per_day': 0.5,  # 1 person monitors 2 tractors
            'working_hours': 12,
            'fuel_savings_pct': 12,
            'labor_savings_pct': 60,
            'accuracy_improvement': '±2.5cm + obstacle detection',
            'overlap_waste_pct': 2,
        },
        {
            'mode': 'Fully Autonomous',
            'description': 'No human needed in field (concept/2027+)',
            'tractor_cost': base_tractor,
            'automation_cost': full_autonomous_cost,
            'steam_unit': steam_unit,
            'operator_needed': False,
            'operators_per_day': 0.2,  # remote monitoring
            'working_hours': 16,  # day+extended hours
            'fuel_savings_pct': 15,
            'labor_savings_pct': 80,
            'accuracy_improvement': 'AI path planning + LiDAR',
            'overlap_waste_pct': 1,
        },
    ]
    
    results = []
    for s in scenarios:
        total_investment = s['tractor_cost'] + s['automation_cost'] + s['steam_unit']
        per_farmer = total_investment / cooperative_size
        
        # Treatment capacity
        rai_per_hour = 60 / (45 + 15)  # 45 min treat + 15 min travel
        effective_rai_per_day = rai_per_hour * s['working_hours'] * (1 - s['overlap_waste_pct'] / 100)
        days_for_coop = total_rai / effective_rai_per_day if effective_rai_per_day > 0 else 999
        
        # Annual operating cost (2 seasons)
        fuel_per_season = days_for_coop * s['working_hours'] * 120 * (1 - s['fuel_savings_pct'] / 100)
        labor_per_season = days_for_coop * current_labor_cost_per_day * s['operators_per_day']
        annual_operating = (fuel_per_season + labor_per_season) * 2
        
        # Revenue (mushroom income from treated rai)
        annual_revenue = total_rai * 57.2 * 55 * 2  # 2 seasons
        annual_profit = annual_revenue - annual_operating - (total_investment / 5)  # 5yr amortize
        
        payback_years = total_investment / (annual_revenue - annual_operating) if (annual_revenue - annual_operating) > 0 else 99
        
        results.append({
            'mode': s['mode'],
            'description': s['description'],
            'total_investment': round(total_investment),
            'per_farmer_cost': round(per_farmer),
            'automation_cost': round(s['automation_cost']),
            'effective_rai_per_day': round(effective_rai_per_day, 1),
            'days_to_treat_coop': round(days_for_coop, 1),
            'annual_operating': round(annual_operating),
            'annual_revenue': round(annual_revenue),
            'annual_profit': round(annual_profit),
            'payback_years': round(payback_years, 1),
            'fuel_savings_pct': s['fuel_savings_pct'],
            'labor_savings_pct': s['labor_savings_pct'],
            'overlap_waste_pct': s['overlap_waste_pct'],
            'accuracy': s['accuracy_improvement'],
            'working_hours': s['working_hours'],
        })
    
    return results


# ================================================================
# ROUND 6: FIELD VALIDATION & RISK ANALYSIS
# ================================================================

def compute_contamination_stress_test(
    steam_temp: float = 120,
    sanitation_level: str = 'standard',
    spawn_quality: str = 'certified',
    environment: str = 'polyhouse',
    n_simulations: int = 5000,
    seed: int = 42,
) -> Dict:
    """
    Monte Carlo stress test for contamination under realistic field conditions.
    
    Research basis:
    - Trichoderma colonizes straw 60-80% within 1 month (ResearchGate)
    - Field contamination higher than lab: outdoor 15-30%, shelter 8-15%, indoor 3-8%
    - Steam >100°C eliminates most pathogens but recontamination occurs post-treatment
    - Spawn quality is critical: certified vs local vs unknown source
    """
    rng = np.random.default_rng(seed)
    
    # Base contamination rate by environment
    env_base = {
        'outdoor': 0.25,     # 25% base rate
        'shade_cloth': 0.15,
        'polyhouse': 0.08,
        'indoor': 0.04,
    }
    base_rate = env_base.get(environment, 0.10)
    
    # Steam temperature modifier
    if steam_temp >= 120:
        steam_mod = 0.3
    elif steam_temp >= 100:
        steam_mod = 0.5
    elif steam_temp >= 80:
        steam_mod = 0.8
    else:
        steam_mod = 1.2  # insufficient sterilization
    
    # Sanitation modifier
    sanitation_mod = {'strict': 0.4, 'standard': 0.7, 'none': 1.5}[sanitation_level]
    
    # Spawn quality modifier
    spawn_mod = {'certified': 0.5, 'local': 0.8, 'unknown': 1.5}[spawn_quality]
    
    # Effective contamination rate
    eff_rate = min(0.95, base_rate * steam_mod * sanitation_mod * spawn_mod)
    
    # Monte Carlo simulation
    contaminated = rng.random(n_simulations) < eff_rate
    
    # When contaminated, yield loss varies 40-100%
    loss_pct = np.where(contaminated, rng.uniform(0.4, 1.0, n_simulations), 0)
    
    # Calculate profit impact
    base_yield = 57.2  # kg per rai
    base_price = 55  # ฿/kg
    base_cost = 1186  # ฿/rai
    
    yields = base_yield * (1 - loss_pct)
    profits = yields * base_price - base_cost
    
    # Scenario comparison
    scenarios = []
    for env_name, env_rate in env_base.items():
        for san_name, san_mod_val in [('strict', 0.4), ('standard', 0.7), ('none', 1.5)]:
            rate = min(0.95, env_rate * steam_mod * san_mod_val * spawn_mod)
            exp_loss = rate * 0.70  # avg 70% loss when contaminated
            exp_yield = base_yield * (1 - exp_loss)
            exp_profit = exp_yield * base_price - base_cost
            scenarios.append({
                'environment': env_name,
                'sanitation': san_name,
                'contamination_rate': round(rate * 100, 1),
                'expected_yield': round(exp_yield, 1),
                'expected_profit': round(exp_profit),
            })
    
    return {
        'effective_rate': round(eff_rate * 100, 1),
        'mean_profit': round(float(np.mean(profits))),
        'p10_profit': round(float(np.percentile(profits, 10))),
        'p90_profit': round(float(np.percentile(profits, 90))),
        'prob_profitable': round(float(np.mean(profits > 0)) * 100, 1),
        'prob_loss': round(float(np.mean(profits < 0)) * 100, 1),
        'worst_case': round(float(np.min(profits))),
        'scenario_matrix': scenarios,
        'profits': profits,
        'n_simulations': n_simulations,
    }


def compute_market_saturation(
    current_village_production_kg: float = 500,
    num_cooperatives: int = 1,
    production_per_coop_kg: float = 500,
    local_demand_kg: float = 2000,
    wholesale_capacity_kg: float = 1500,
    cannery_capacity_kg: float = 3000,
    dried_capacity_kg: float = 500,
) -> Dict:
    """
    Market saturation model — what happens when multiple cooperatives produce simultaneously?
    
    Sources:
    - Thai mushroom market projected to reach $530M by 2033 (IMARC Group)
    - Puffball prices crashed 350→30 ฿/L at end of season (TheThaiger)
    - Village wet market absorbs ~500 kg/month without price drop
    - Price elasticity: oversupply typically drops prices 20-40%
    """
    # Total supply at different scale levels
    scenarios = []
    for n_coops in range(1, min(num_cooperatives + 1, 21)):
        total_supply = n_coops * production_per_coop_kg
        total_demand = local_demand_kg + wholesale_capacity_kg + cannery_capacity_kg + dried_capacity_kg
        
        # Allocation priority: local → wholesale → cannery → dried
        local_sold = min(total_supply, local_demand_kg)
        remaining = total_supply - local_sold
        wholesale_sold = min(remaining, wholesale_capacity_kg)
        remaining -= wholesale_sold
        cannery_sold = min(remaining, cannery_capacity_kg)
        remaining -= cannery_sold
        dried_sold = min(remaining, dried_capacity_kg)
        unsold = remaining - dried_sold
        
        # Price pressure: oversupply drops local prices
        supply_ratio = total_supply / total_demand if total_demand > 0 else 999
        if supply_ratio <= 0.5:
            price_drop = 0
        elif supply_ratio <= 0.8:
            price_drop = 5
        elif supply_ratio <= 1.0:
            price_drop = 15
        elif supply_ratio <= 1.5:
            price_drop = 30
        else:
            price_drop = 50
        
        # Blended revenue
        prices = {
            'local': max(20, 80 * (1 - price_drop / 100)),
            'wholesale': max(15, 45 * (1 - price_drop / 100)),
            'cannery': max(10, 25 * (1 - price_drop / 100)),
            'dried': max(30, 120 * (1 - price_drop / 100)),
        }
        
        revenue = (local_sold * prices['local'] + wholesale_sold * prices['wholesale'] +
                  cannery_sold * prices['cannery'] + dried_sold * prices['dried'])
        blended_price = revenue / total_supply if total_supply > 0 else 0
        
        scenarios.append({
            'cooperatives': n_coops,
            'total_supply_kg': round(total_supply),
            'total_demand_kg': round(total_demand),
            'supply_ratio': round(supply_ratio, 2),
            'price_drop_pct': price_drop,
            'blended_price': round(blended_price, 1),
            'unsold_kg': round(max(0, unsold)),
            'revenue': round(revenue),
            'local_price': round(prices['local']),
            'status': '🟢 Healthy' if supply_ratio < 0.8 else '🟡 Pressure' if supply_ratio < 1.2 else '🔴 Oversupply',
        })
    
    return {
        'scenarios': scenarios,
        'saturation_point': next((s['cooperatives'] for s in scenarios if s['supply_ratio'] >= 1.0), None),
        'max_coops_healthy': next((s['cooperatives'] for s in reversed(scenarios) if s['status'] == '🟢 Healthy'), 0),
    }


def compute_straw_variety_comparison() -> List[Dict]:
    """
    Compare rice straw quality by Thai variety for mushroom substrate.
    
    Sources:
    - Rice straw: 30-60% cellulose, 10-40% hemicellulose, 5-30% lignin (NIH, IRRI)
    - KDML105 (Jasmine): premium aromatic rice, moderate straw yield
    - RD6 (glutinous): sticky rice, higher straw yield, different nutrient profile
    - RD41, RD47: high-yield varieties with different residue characteristics
    - Straw N content ~0.7%, P ~0.23%, K ~1.75% (IRRI)
    """
    varieties = [
        {
            'variety': 'KDML105 (Jasmine)',
            'region': 'Isaan, Central',
            'grain_yield_kg_rai': 450,
            'straw_yield_kg_rai': 580,
            'cellulose_pct': 38,
            'hemicellulose_pct': 28,
            'lignin_pct': 12,
            'silica_pct': 14,
            'nitrogen_pct': 0.65,
            'potassium_pct': 1.6,
            'notes': 'Most common Isaan variety. Good substrate but lower straw yield.',
            'mushroom_be_modifier': 1.0,  # baseline
            'price_premium': 'Premium grain = less incentive to burn',
        },
        {
            'variety': 'RD6 (Glutinous)',
            'region': 'Isaan, North',
            'grain_yield_kg_rai': 420,
            'straw_yield_kg_rai': 650,
            'cellulose_pct': 40,
            'hemicellulose_pct': 26,
            'lignin_pct': 11,
            'silica_pct': 15,
            'nitrogen_pct': 0.72,
            'potassium_pct': 1.8,
            'notes': 'Sticky rice — higher straw yield, slightly better substrate.',
            'mushroom_be_modifier': 1.05,
            'price_premium': 'Lower grain price = higher burning incentive',
        },
        {
            'variety': 'RD41 (High-yield)',
            'region': 'Central Plain',
            'grain_yield_kg_rai': 620,
            'straw_yield_kg_rai': 750,
            'cellulose_pct': 42,
            'hemicellulose_pct': 24,
            'lignin_pct': 13,
            'silica_pct': 13,
            'nitrogen_pct': 0.68,
            'potassium_pct': 1.7,
            'notes': 'Modern high-yield variety. Highest straw volume.',
            'mushroom_be_modifier': 1.02,
            'price_premium': 'Commodity price — strong burning incentive',
        },
        {
            'variety': 'RD47 (Photoperiod)',
            'region': 'Central, Lower North',
            'grain_yield_kg_rai': 550,
            'straw_yield_kg_rai': 680,
            'cellulose_pct': 39,
            'hemicellulose_pct': 27,
            'lignin_pct': 12,
            'silica_pct': 14,
            'nitrogen_pct': 0.70,
            'potassium_pct': 1.75,
            'notes': 'Non-photoperiod sensitive, can grow off-season.',
            'mushroom_be_modifier': 1.0,
            'price_premium': 'Year-round availability = consistent substrate supply',
        },
    ]
    
    # Calculate mushroom metrics for each variety
    base_be = 0.12
    for v in varieties:
        eff_be = base_be * v['mushroom_be_modifier']
        substrate = v['straw_yield_kg_rai'] * 0.90  # 10% for fuel
        mushroom_yield = substrate * eff_be
        revenue = mushroom_yield * 55
        v['effective_be'] = round(eff_be * 100, 1)
        v['mushroom_yield_kg'] = round(mushroom_yield, 1)
        v['mushroom_revenue'] = round(revenue)
        v['substrate_quality'] = round(v['cellulose_pct'] + v['hemicellulose_pct'] - v['lignin_pct'], 1)
    
    return varieties


def compute_adoption_curve(
    total_farmers: int = 200,
    initial_adopters: int = 5,
    innovation_factor: float = 0.15,
    demonstration_effect: float = 0.3,
    training_quality: str = 'good',
    years: int = 10,
) -> Dict:
    """
    S-curve adoption model for Zero-Burn technology in Thai farming communities.
    
    Based on Rogers' Diffusion of Innovation + Thai agricultural adoption data:
    - Generally low adoption rate for new tech (cam.ac.uk)
    - 57,000 farmers adopted digital tools in 2022 (marketresearchthailand.com)
    - Older farmers resist unfamiliar technology (nrct.go.th)
    - Cooperative structure accelerates adoption (fftc.org.tw)
    - Hands-on demonstration most effective training method
    
    Categories (Rogers):
    - Innovators: 2.5% — first 1-2 farmers who try anything
    - Early adopters: 13.5% — opinion leaders, others watch them
    - Early majority: 34% — join once they see neighbors succeed
    - Late majority: 34% — risk-averse, need strong proof
    - Laggards: 16% — may never adopt
    """
    training_mod = {'excellent': 1.3, 'good': 1.0, 'basic': 0.7, 'none': 0.4}
    train_factor = training_mod.get(training_quality, 1.0)
    
    # Adjusted adoption rate (Bass model parameters)
    p = innovation_factor * 0.01 * train_factor  # innovation coefficient
    q = demonstration_effect * train_factor  # imitation coefficient
    
    adopters = [initial_adopters]
    cumulative = [initial_adopters]
    
    timeline = []
    for year in range(1, years + 1):
        current = cumulative[-1]
        remaining = total_farmers - current
        
        # Bass diffusion: new = (p + q * current/total) * remaining
        new_adopters = max(0, min(remaining, 
                                  (p + q * current / total_farmers) * remaining))
        new_adopters = round(new_adopters)
        
        cum = min(total_farmers, current + new_adopters)
        adopters.append(new_adopters)
        cumulative.append(cum)
        
        # Revenue impact
        active_rai = cum * 15  # avg 15 rai per farmer
        annual_profit = active_rai * 3128  # ~฿3,128/rai profit
        
        # Adoption category
        pct = cum / total_farmers * 100
        category = ('Innovators' if pct < 5 else 'Early Adopters' if pct < 16
                    else 'Early Majority' if pct < 50 else 'Late Majority' if pct < 84
                    else 'Laggards')
        
        timeline.append({
            'year': year,
            'new_adopters': new_adopters,
            'cumulative': cum,
            'adoption_pct': round(pct, 1),
            'category': category,
            'active_rai': active_rai,
            'annual_profit': round(annual_profit),
            'co2_avoided_tons': round(active_rai * 0.0428, 1),
        })
    
    # Key milestones
    y50 = next((t['year'] for t in timeline if t['adoption_pct'] >= 50), None)
    y80 = next((t['year'] for t in timeline if t['adoption_pct'] >= 80), None)
    
    return {
        'timeline': timeline,
        'year_to_50pct': y50,
        'year_to_80pct': y80,
        'total_farmers': total_farmers,
        'final_adoption': timeline[-1]['adoption_pct'] if timeline else 0,
    }


def compute_full_sensitivity(
    base_rai: float = 15,
) -> Dict:
    """
    Comprehensive multi-variable sensitivity analysis.
    Tests profit sensitivity to all major risk factors simultaneously.
    """
    base_profit = 57.2 * 55 - 1186  # ~฿1,960/rai
    
    factors = [
        {'name': 'Mushroom price (฿/kg)', 'low': 30, 'base': 55, 'high': 80,
         'profit_low': 57.2 * 30 - 1186, 'profit_high': 57.2 * 80 - 1186},
        {'name': 'Biological efficiency (%)', 'low': 0.06, 'base': 0.12, 'high': 0.18,
         'profit_low': 585 * 0.06 * 55 - 1186, 'profit_high': 585 * 0.18 * 55 - 1186},
        {'name': 'Straw yield (kg/rai)', 'low': 400, 'base': 650, 'high': 900,
         'profit_low': 400 * 0.9 * 0.12 * 55 - 1186, 'profit_high': 900 * 0.9 * 0.12 * 55 - 1186},
        {'name': 'Contamination rate (%)', 'low': 0.02, 'base': 0.08, 'high': 0.25,
         'profit_low': base_profit * (1 - 0.02 * 0.8), 'profit_high': base_profit * (1 - 0.25 * 0.8)},
        {'name': 'Input costs (฿/rai)', 'low': 900, 'base': 1186, 'high': 1500,
         'profit_low': 57.2 * 55 - 900, 'profit_high': 57.2 * 55 - 1500},
        {'name': 'Cycles per year', 'low': 2, 'base': 5, 'high': 8,
         'profit_low': base_profit * 2, 'profit_high': base_profit * 8},
    ]
    
    for f in factors:
        f['profit_base'] = round(base_profit)
        f['profit_low'] = round(f['profit_low'])
        f['profit_high'] = round(f['profit_high'])
        f['swing'] = round(f['profit_high'] - f['profit_low'])
        f['impact_rank'] = f['swing']
    
    # Sort by impact
    factors.sort(key=lambda x: x['swing'], reverse=True)
    for i, f in enumerate(factors):
        f['rank'] = i + 1
    
    return {
        'factors': factors,
        'base_profit_per_rai': round(base_profit),
        'base_profit_total': round(base_profit * base_rai),
        'most_sensitive': factors[0]['name'],
        'least_sensitive': factors[-1]['name'],
    }


# ================================================================
# ROUND 7: HEALTH & POLLUTION IMPACT
# ================================================================

def compute_pm25_emissions(
    rai_burned: float = 15,
    straw_yield_kg_per_rai: float = 650,
    burn_efficiency: float = 0.85,
) -> Dict:
    """
    Calculate pollutant emissions from open-field rice straw burning vs zero-burn.
    
    Emission factors (IPCC 2006 + Thailand-specific research):
    - PM2.5: 9.4 g/kg straw burned (Gadde et al. 2009)
    - PM10: 13.0 g/kg (IPCC)
    - CO: 92.0 g/kg (IPCC)
    - CO2: 1,460 g/kg (stoichiometric combustion)
    - CH4: 5.0 g/kg (IPCC default)
    - N2O: 0.07 g/kg (IPCC default)
    - Black carbon: 0.75 g/kg (Bond et al. 2004)
    - NOx: 3.5 g/kg
    - SO2: 2.0 g/kg
    
    Health context:
    - 32,200 premature deaths/year in Thailand from crop burning (ThinkGlobalHealth)
    - 12.3M people affected by air pollution in 2024 (Nation Thailand)
    - PM2.5 healthcare costs: ฿3 billion in 2023-2024
    """
    straw_total = rai_burned * straw_yield_kg_per_rai
    straw_burned = straw_total * burn_efficiency  # some straw is left unburned
    
    # Emission factors (g per kg of straw burned)
    emission_factors = {
        'PM2.5': 9.4,
        'PM10': 13.0,
        'CO': 92.0,
        'CO₂': 1460.0,
        'CH₄': 5.0,
        'N₂O': 0.07,
        'Black Carbon': 0.75,
        'NOx': 3.5,
        'SO₂': 2.0,
    }
    
    emissions_burning = {}
    emissions_zero_burn = {}
    avoided = {}
    
    for pollutant, ef in emission_factors.items():
        burn_g = straw_burned * ef
        # Zero-burn still produces some from steam boiler (rice husk fuel, ~10% of straw)
        boiler_fuel = straw_total * 0.10  # 10% used as fuel
        if pollutant in ['PM2.5', 'PM10', 'CO', 'NOx', 'SO₂']:
            zero_burn_g = boiler_fuel * ef * 0.15  # improper combustion is ~85% cleaner with proper boiler
        elif pollutant == 'CO₂':
            zero_burn_g = boiler_fuel * ef * 0.90  # CO2 still produced from fuel
        else:
            zero_burn_g = boiler_fuel * ef * 0.10
        
        emissions_burning[pollutant] = round(burn_g / 1000, 3)  # convert to kg
        emissions_zero_burn[pollutant] = round(zero_burn_g / 1000, 3)
        avoided[pollutant] = round((burn_g - zero_burn_g) / 1000, 3)
    
    # PM2.5 equivalent "cigarettes" — 1 cigarette ≈ 12mg PM2.5 inhaled
    pm25_avoided_mg = avoided['PM2.5'] * 1_000_000
    cigarette_equivalent = round(pm25_avoided_mg / 12)
    
    # Health impact estimation
    # WHO: 10 μg/m³ increase in PM2.5 → 7% increase in mortality risk
    pm25_kg = avoided['PM2.5']
    
    return {
        'straw_total_kg': round(straw_total),
        'straw_burned_kg': round(straw_burned),
        'emissions_burning': emissions_burning,
        'emissions_zero_burn': emissions_zero_burn,
        'emissions_avoided': avoided,
        'pm25_avoided_kg': avoided['PM2.5'],
        'co2_avoided_kg': avoided['CO₂'],
        'cigarette_equivalent': cigarette_equivalent,
        'emission_factors': emission_factors,
        'pollutant_list': [
            {'pollutant': p, 'burning_kg': emissions_burning[p],
             'zero_burn_kg': emissions_zero_burn[p], 'avoided_kg': avoided[p],
             'reduction_pct': round((1 - emissions_zero_burn[p] / emissions_burning[p]) * 100, 1)
             if emissions_burning[p] > 0 else 0}
            for p in emission_factors
        ],
    }


def compute_health_cost_impact(
    family_size: int = 4,
    rai_burned: float = 15,
    exposure_days: int = 30,
    has_children: bool = True,
    has_elderly: bool = True,
) -> Dict:
    """
    Estimate healthcare costs and health outcomes for a farming family from burning.
    
    Sources:
    - Asthma treatment: ฿2,752/episode (Nation Thailand 2024)
    - COPD treatment: ฿16,000/episode (Nation Thailand 2024)
    - Hospital visits per burning season for affected families: 2-5 (estimated from 200k admissions / burning season)
    - Children asthma risk increase during burning: 1.4x (ScienceAsia)
    - Life expectancy reduction: -2 years average (ThinkGlobalHealth)
    - Lost workdays: 5-15 days during haze season (MOPH estimates)
    """
    # Base health risk factors
    conditions = [
        {
            'condition': 'Respiratory irritation',
            'prob_per_season': 0.60,
            'cost_per_episode': 500,
            'episodes_per_season': 3,
            'affected': 'All family',
        },
        {
            'condition': 'Asthma attack (children)',
            'prob_per_season': 0.35 if has_children else 0,
            'cost_per_episode': 2752,
            'episodes_per_season': 2,
            'affected': 'Children',
        },
        {
            'condition': 'COPD exacerbation',
            'prob_per_season': 0.25 if has_elderly else 0,
            'cost_per_episode': 16000,
            'episodes_per_season': 1,
            'affected': 'Elderly',
        },
        {
            'condition': 'Conjunctivitis/dermatitis',
            'prob_per_season': 0.40,
            'cost_per_episode': 800,
            'episodes_per_season': 2,
            'affected': 'All family',
        },
        {
            'condition': 'Acute bronchitis',
            'prob_per_season': 0.15,
            'cost_per_episode': 3500,
            'episodes_per_season': 1,
            'affected': 'All family',
        },
        {
            'condition': 'ER visit (severe)',
            'prob_per_season': 0.05,
            'cost_per_episode': 8000,
            'episodes_per_season': 1,
            'affected': 'Elderly/Children',
        },
    ]
    
    total_cost_burn = 0
    condition_breakdown = []
    for c in conditions:
        expected_cost = c['prob_per_season'] * c['cost_per_episode'] * c['episodes_per_season']
        total_cost_burn += expected_cost
        condition_breakdown.append({
            **c,
            'expected_cost': round(expected_cost),
        })
    
    # Lost workdays
    lost_days = round(exposure_days * 0.15)  # ~15% of burning days result in reduced productivity
    lost_income = lost_days * 300  # ฿300/day labor value
    
    # Long-term costs (amortized per year over lifetime)
    long_term = {
        'lung_cancer_risk_increase': '1.2x over 30 years',
        'life_expectancy_reduction_years': 2.0,
        'value_of_lost_years': round(2 * 365 * 300),  # ฿ value of 2 years at ฿300/day
    }
    
    total_annual_cost_burning = round(total_cost_burn + lost_income)
    
    return {
        'conditions': condition_breakdown,
        'total_healthcare_cost': round(total_cost_burn),
        'lost_workdays': lost_days,
        'lost_income': round(lost_income),
        'total_annual_cost': total_annual_cost_burning,
        'total_zero_burn_cost': round(total_cost_burn * 0.05),  # 95% reduction with zero-burn
        'annual_savings': round(total_annual_cost_burning * 0.95),
        'long_term': long_term,
        'family_size': family_size,
    }


def compute_regional_pollution_impact(
    adopting_farmers: int = 100,
    rai_per_farmer: float = 15,
    district_population: int = 50000,
    years: int = 10,
) -> Dict:
    """
    Project cumulative health, environmental, and economic impact at district scale.
    
    Scale factors:
    - Thailand has ~60M rai of rice paddies
    - ~32,200 premature deaths/year from crop burning nationally
    - ฿3 billion healthcare costs annually
    - Average Isaan district: ~50,000 people, ~5,000 farming families
    """
    total_rai = adopting_farmers * rai_per_farmer
    straw_per_rai = 650  # kg
    
    # Per-year calculations
    yearly = []
    cumulative_pm25 = 0
    cumulative_co2 = 0
    cumulative_health_savings = 0
    cumulative_income = 0
    
    for year in range(1, years + 1):
        # Use adoption S-curve for realistic farmer count growth
        if year == 1:
            n_farmers = adopting_farmers
        else:
            # Simple logistic growth to district's farming families
            max_farmers = district_population * 0.10  # ~10% are rice farming families
            n_farmers = min(max_farmers, adopting_farmers * (1 + 0.3) ** (year - 1))
        
        n_farmers = round(n_farmers)
        year_rai = n_farmers * rai_per_farmer
        year_straw = year_rai * straw_per_rai
        
        # PM2.5 avoided (kg)
        pm25_avoided = year_straw * 0.85 * 9.4 / 1000  # burn efficiency * EF / 1000
        co2_avoided = year_straw * 0.85 * 1.46  # tons
        
        # Healthcare savings
        health_savings_per_farmer = 7000  # ฿/year average
        year_health_savings = n_farmers * health_savings_per_farmer
        
        # Mushroom income
        mushroom_income = year_rai * 3128 * 5  # ฿/rai × 5 cycles (conservative)
        
        # People protected from PM2.5 (rough estimate based on local dispersion)
        people_protected = min(district_population, n_farmers * 15)  # each farmer protects ~15 people nearby
        
        # Premature deaths avoided (proportional estimate)
        # 32,200 deaths / 60M rai = 0.000537 deaths/rai
        deaths_avoided = year_rai * 0.000537
        
        # Hospital visits avoided per year
        # 200,000 admissions in March 2023 across ~25M affected people
        # = 0.008 visits per person per burning month × 4 months = 0.032/person/season
        hospital_visits_avoided = people_protected * 0.032
        
        cumulative_pm25 += pm25_avoided
        cumulative_co2 += co2_avoided
        cumulative_health_savings += year_health_savings
        cumulative_income += mushroom_income
        
        yearly.append({
            'year': year,
            'farmers': n_farmers,
            'rai_treated': round(year_rai),
            'pm25_avoided_kg': round(pm25_avoided, 1),
            'co2_avoided_tons': round(co2_avoided, 1),
            'health_savings': round(year_health_savings),
            'mushroom_income': round(mushroom_income),
            'people_protected': round(people_protected),
            'deaths_avoided': round(deaths_avoided, 2),
            'hospital_visits_avoided': round(hospital_visits_avoided),
            'cumulative_pm25_kg': round(cumulative_pm25, 1),
            'cumulative_co2_tons': round(cumulative_co2, 1),
            'cumulative_health_savings': round(cumulative_health_savings),
        })
    
    return {
        'yearly': yearly,
        'total_pm25_avoided_kg': round(cumulative_pm25, 1),
        'total_co2_avoided_tons': round(cumulative_co2, 1),
        'total_health_savings': round(cumulative_health_savings),
        'total_mushroom_income': round(cumulative_income),
        'total_deaths_avoided': round(sum(y['deaths_avoided'] for y in yearly), 1),
        'total_hospital_visits_avoided': round(sum(y['hospital_visits_avoided'] for y in yearly)),
    }


# ================================================================
# ROUND 8: BREAKTHROUGH SCIENCE
# ================================================================

def compute_multi_species_comparison(
    rai: float = 15,
    cycles_per_year: int = 5,
    substrate_kg_per_rai: float = 650,
) -> Dict:
    """
    Compare profitability of different mushroom species grown on rice straw substrate.
    
    Species data from Thai research and market prices (2024-2025):
    
    1. Straw Mushroom (Volvariella volvacea): Traditional Thai species
       - Price: ฿55/kg (farm gate), up to ฿80/kg retail
       - Biological efficiency on rice straw: 10-15%
       - Cycle time: 15-20 days (fastest)
       - Difficulty: Easy
       - Straw compatibility: Excellent (native substrate)
    
    2. Oyster Mushroom (Pleurotus ostreatus): 
       - Price: ฿70-80/kg wholesale
       - Biological efficiency on rice straw: 80-120% (!!!) 
       - Rice straw yields 18-28% MORE than sawdust (Thai research)
       - Cycle time: 25-35 days
       - Difficulty: Easy
       - Straw compatibility: Excellent
    
    3. King Oyster (Pleurotus eryngii):
       - Price: ฿80-120/kg
       - Biological efficiency on rice straw: 40-70%
       - Cycle time: 35-50 days
       - Difficulty: Medium (needs cooler temps)
       - Straw compatibility: Good (with supplements)
    
    4. Shiitake (Lentinula edodes):
       - Price: ฿200-320/kg
       - Biological efficiency: 60-100% (on sawdust)
       - On rice straw: needs 50-70% sawdust supplement
       - Cycle time: 90-120 days
       - Difficulty: Hard
       - Straw compatibility: Poor (needs sawdust mix)
    
    5. Lion's Mane (Hericium erinaceus):
       - Price: ฿633-760/kg  
       - Biological efficiency: 30-50%
       - On rice straw: needs sawdust + wheat bran supplement
       - Cycle time: 60-90 days
       - Difficulty: Hard
       - Straw compatibility: Poor (needs sawdust mix)
    
    6. Reishi / Lingzhi (Ganoderma lucidum):
       - Price: ฿500-1000/kg (dried), ฿200-300/kg fresh
       - Biological efficiency: 10-20%
       - Rice straw: proven viable substrate
       - Cycle time: 60-90 days
       - Difficulty: Medium
       - Straw compatibility: Good
    """
    
    species = [
        {
            'name': 'Straw Mushroom',
            'thai_name': 'เห็ดฟาง',
            'emoji': '🍄',
            'price_per_kg': 55,
            'price_retail': 80,
            'bio_efficiency_low': 0.10,
            'bio_efficiency_high': 0.15,
            'bio_efficiency_avg': 0.12,
            'cycle_days': 18,
            'max_cycles_per_year': 8 if cycles_per_year >= 8 else cycles_per_year,
            'difficulty': 'Easy',
            'difficulty_score': 1,
            'straw_compatibility': 'Excellent',
            'straw_pct': 1.0,  # 100% rice straw
            'supplement_cost_per_kg': 0,
            'notes': 'Traditional Thai species. Fastest cycle. Lowest entry barrier.',
            'temp_range': '32-38°C',
            'market_demand': 'Very High (Thai staple)',
        },
        {
            'name': 'Oyster Mushroom',
            'thai_name': 'เห็ดนางฟ้า',
            'emoji': '🦪',
            'price_per_kg': 75,
            'price_retail': 100,
            'bio_efficiency_low': 0.80,
            'bio_efficiency_high': 1.20,
            'bio_efficiency_avg': 0.95,
            'cycle_days': 30,
            'max_cycles_per_year': 6 if cycles_per_year >= 6 else cycles_per_year,
            'difficulty': 'Easy',
            'difficulty_score': 1,
            'straw_compatibility': 'Excellent',
            'straw_pct': 0.85,
            'supplement_cost_per_kg': 2,  # rice bran supplement
            'notes': 'Rice straw yields 18-28% MORE than sawdust. Best value upgrade.',
            'temp_range': '20-30°C',
            'market_demand': 'Very High (growing fast)',
        },
        {
            'name': 'King Oyster',
            'thai_name': 'เห็ดเอรินจิ',
            'emoji': '👑',
            'price_per_kg': 100,
            'price_retail': 150,
            'bio_efficiency_low': 0.40,
            'bio_efficiency_high': 0.70,
            'bio_efficiency_avg': 0.55,
            'cycle_days': 42,
            'max_cycles_per_year': 4 if cycles_per_year >= 4 else cycles_per_year,
            'difficulty': 'Medium',
            'difficulty_score': 2,
            'straw_compatibility': 'Good',
            'straw_pct': 0.70,
            'supplement_cost_per_kg': 5,
            'notes': 'Premium restaurant mushroom. Needs cooler environment for fruiting.',
            'temp_range': '15-22°C',
            'market_demand': 'High (restaurants, export)',
        },
        {
            'name': 'Shiitake',
            'thai_name': 'เห็ดหอม',
            'emoji': '🔶',
            'price_per_kg': 260,
            'price_retail': 400,
            'bio_efficiency_low': 0.60,
            'bio_efficiency_high': 1.00,
            'bio_efficiency_avg': 0.75,
            'cycle_days': 105,
            'max_cycles_per_year': 2,
            'difficulty': 'Hard',
            'difficulty_score': 3,
            'straw_compatibility': 'Poor',
            'straw_pct': 0.30,
            'supplement_cost_per_kg': 8,
            'notes': 'Needs 50-70% hardwood sawdust. High value but complex cultivation.',
            'temp_range': '12-20°C',
            'market_demand': 'Very High (premium, export)',
        },
        {
            'name': "Lion's Mane",
            'thai_name': 'เห็ดหัวลิง',
            'emoji': '🦁',
            'price_per_kg': 700,
            'price_retail': 1000,
            'bio_efficiency_low': 0.30,
            'bio_efficiency_high': 0.50,
            'bio_efficiency_avg': 0.40,
            'cycle_days': 75,
            'max_cycles_per_year': 3,
            'difficulty': 'Hard',
            'difficulty_score': 3,
            'straw_compatibility': 'Poor',
            'straw_pct': 0.25,
            'supplement_cost_per_kg': 10,
            'notes': 'Premium medicinal mushroom. Bangkok price ฿633-760/kg. Needs controlled environment.',
            'temp_range': '18-24°C',
            'market_demand': 'Growing (health market)',
        },
        {
            'name': 'Reishi (Lingzhi)',
            'thai_name': 'เห็ดหลินจือ',
            'emoji': '❤️',
            'price_per_kg': 250,
            'price_retail': 500,
            'bio_efficiency_low': 0.10,
            'bio_efficiency_high': 0.20,
            'bio_efficiency_avg': 0.15,
            'cycle_days': 75,
            'max_cycles_per_year': 3,
            'difficulty': 'Medium',
            'difficulty_score': 2,
            'straw_compatibility': 'Good',
            'straw_pct': 0.60,
            'supplement_cost_per_kg': 5,
            'notes': 'Medicinal mushroom proven on rice straw. Dried form ฿500-1000/kg.',
            'temp_range': '25-35°C',
            'market_demand': 'High (Traditional Chinese medicine)',
        },
    ]
    
    total_straw = rai * substrate_kg_per_rai
    results = []
    
    for sp in species:
        # How much straw this species can use
        straw_used = total_straw * sp['straw_pct']
        supplement_needed = total_straw * (1 - sp['straw_pct'])
        supplement_cost = supplement_needed * sp['supplement_cost_per_kg']
        
        # Yield calculation
        yield_per_cycle = straw_used * sp['bio_efficiency_avg']
        actual_cycles = min(sp['max_cycles_per_year'], cycles_per_year)
        if sp['difficulty_score'] >= 3 and sp['temp_range'].startswith('1'):
            # Hard species in tropical climate — reduce yield by 30%
            yield_per_cycle *= 0.70
        
        annual_yield = yield_per_cycle * actual_cycles
        
        # Revenue
        gross_revenue = annual_yield * sp['price_per_kg']
        
        # Costs
        substrate_cost = rai * 200 * actual_cycles  # base substrate prep
        spawn_cost = rai * 150 * actual_cycles
        labor_cost = rai * 100 * actual_cycles * sp['difficulty_score']
        total_cost = substrate_cost + spawn_cost + labor_cost + (supplement_cost * actual_cycles)
        
        net_profit = gross_revenue - total_cost
        profit_per_rai = net_profit / rai if rai > 0 else 0
        
        # Compare to baseline (straw mushroom)
        baseline_profit = total_straw * 0.12 * 55 * cycles_per_year - (rai * 450 * cycles_per_year)
        multiplier = net_profit / baseline_profit if baseline_profit > 0 else 0
        
        results.append({
            **sp,
            'straw_used_kg': round(straw_used),
            'supplement_needed_kg': round(supplement_needed),
            'supplement_cost_total': round(supplement_cost * actual_cycles),
            'yield_per_cycle_kg': round(yield_per_cycle, 1),
            'actual_cycles': actual_cycles,
            'annual_yield_kg': round(annual_yield, 1),
            'gross_revenue': round(gross_revenue),
            'total_cost': round(total_cost),
            'net_profit': round(net_profit),
            'profit_per_rai': round(profit_per_rai),
            'multiplier': round(multiplier, 1),
            'roi_pct': round((net_profit / total_cost * 100) if total_cost > 0 else 0),
        })
    
    # Sort by net profit
    results.sort(key=lambda x: x['net_profit'], reverse=True)
    
    return {
        'species': results,
        'total_straw_kg': round(total_straw),
        'rai': rai,
        'cycles_per_year': cycles_per_year,
        'best_species': results[0]['name'],
        'best_profit': results[0]['net_profit'],
        'best_multiplier': results[0]['multiplier'],
        'best_easy_species': next((s for s in results if s['difficulty'] == 'Easy'), results[0])['name'],
    }


def compute_circular_economy_cascade(
    mushroom_yield_kg: float = 5000,
    sms_ratio: float = 5.0,
    enable_vermicompost: bool = True,
    enable_biogas: bool = True,
    enable_animal_feed: bool = True,
    enable_compost: bool = True,
    rai: float = 15,
) -> Dict:
    """
    Model the Circular Economy Cascade: what happens to Spent Mushroom Substrate (SMS).
    5 kg SMS per 1 kg mushrooms. Multiple value streams extract remaining value.
    """
    total_sms = mushroom_yield_kg * sms_ratio

    enabled = []
    if enable_vermicompost: enabled.append('vermicompost')
    if enable_biogas: enabled.append('biogas')
    if enable_animal_feed: enabled.append('animal_feed')
    if enable_compost: enabled.append('compost')
    if not enabled: enabled = ['compost']

    alloc_map = {
        4: {'vermicompost': 0.40, 'biogas': 0.25, 'animal_feed': 0.20, 'compost': 0.15},
        3: {'vermicompost': 0.45, 'biogas': 0.30, 'animal_feed': 0.25, 'compost': 0.25},
        2: {'vermicompost': 0.55, 'biogas': 0.45, 'animal_feed': 0.45, 'compost': 0.45},
        1: {'vermicompost': 1.0, 'biogas': 1.0, 'animal_feed': 1.0, 'compost': 1.0},
    }
    n = len(enabled)
    alloc = {s: alloc_map[n].get(s, 1.0/n) for s in enabled}
    t = sum(alloc.values())
    alloc = {k: v/t for k, v in alloc.items()}

    streams = []

    if 'vermicompost' in alloc:
        si = total_sms * alloc['vermicompost']
        out = si * 0.40; price = 22; rev = out * price
        cost = si * 1.5 + 5000/3
        streams.append({'name': 'Vermicompost', 'emoji': '🪱', 'sms_input_kg': round(si),
            'output_kg': round(out), 'output_unit': 'kg vermicompost', 'price_per_unit': price,
            'gross_revenue': round(rev), 'processing_cost': round(cost),
            'net_revenue': round(rev - cost), 'processing_days': 50,
            'description': 'Premium organic fertilizer via earthworm conversion.',
            'market': 'Organic farmers, garden centers', 'difficulty': 'Easy',
            'allocation_pct': round(alloc['vermicompost'] * 100)})

    if 'biogas' in alloc:
        si = total_sms * alloc['biogas']
        vs = si * 0.65; m3 = vs * 300 / 1000
        kwh = m3 * 36 * 0.278; e_rev = kwh * 4.0; f_rev = m3 * 15
        rev = max(e_rev, f_rev)
        dig = si * 0.4; dig_val = dig * 3
        cost = 15000/5 + si * 0.3
        streams.append({'name': 'Biogas Energy', 'emoji': '⚡', 'sms_input_kg': round(si),
            'output_kg': round(m3), 'output_unit': 'm³ methane',
            'price_per_unit': round(rev/m3) if m3 > 0 else 0,
            'gross_revenue': round(rev + dig_val), 'processing_cost': round(cost),
            'net_revenue': round(rev + dig_val - cost), 'processing_days': 30,
            'description': f'Anaerobic digestion: {round(m3)} m³ CH₄ + {round(dig)} kg digestate.',
            'market': 'On-farm energy, boiler fuel', 'difficulty': 'Medium',
            'allocation_pct': round(alloc['biogas'] * 100)})

    if 'animal_feed' in alloc:
        si = total_sms * alloc['animal_feed']
        out = si * 0.70; price = 3.5; rev = out * price
        cost = si * 0.8
        streams.append({'name': 'Animal Feed', 'emoji': '🐄', 'sms_input_kg': round(si),
            'output_kg': round(out), 'output_unit': 'kg feed supplement',
            'price_per_unit': price, 'gross_revenue': round(rev),
            'processing_cost': round(cost), 'net_revenue': round(rev - cost),
            'processing_days': 7,
            'description': 'Mycelium-enriched straw with improved digestibility for cattle.',
            'market': 'Local livestock farmers', 'difficulty': 'Easy',
            'allocation_pct': round(alloc['animal_feed'] * 100)})

    if 'compost' in alloc:
        si = total_sms * alloc['compost']
        out = si * 0.50; price = 5; rev = out * price
        cost = si * 0.3; fert = rai * 800
        streams.append({'name': 'Compost / Soil', 'emoji': '🌱', 'sms_input_kg': round(si),
            'output_kg': round(out), 'output_unit': 'kg compost', 'price_per_unit': price,
            'gross_revenue': round(rev + fert), 'processing_cost': round(cost),
            'net_revenue': round(rev + fert - cost), 'processing_days': 30,
            'description': f'Composting + ฿{fert:,}/yr chemical fertilizer savings.',
            'market': 'Own farm, local organic farms', 'difficulty': 'Easy',
            'allocation_pct': round(alloc['compost'] * 100)})

    tg = sum(s['gross_revenue'] for s in streams)
    tc = sum(s['processing_cost'] for s in streams)
    tn = sum(s['net_revenue'] for s in streams)
    vpk = tn / mushroom_yield_kg if mushroom_yield_kg > 0 else 0

    return {
        'streams': streams, 'total_sms_kg': round(total_sms),
        'mushroom_yield_kg': mushroom_yield_kg,
        'total_gross_revenue': round(tg), 'total_processing_cost': round(tc),
        'total_net_revenue': round(tn),
        'value_per_kg_mushroom': round(vpk, 1),
        'pct_increase': round((tn / (mushroom_yield_kg * 55)) * 100 if mushroom_yield_kg > 0 else 0, 1),
        'circular_efficiency': round(
            sum(s['output_kg'] for s in streams) / total_sms * 100 if total_sms > 0 else 0, 1),
    }


def compute_biochar_carbon_credits(
    straw_for_biochar_kg: float = 3000,
    pyrolysis_temp: int = 500,
    carbon_credit_price: float = 175,
    biochar_sale_price: float = 12,
    rai: float = 15,
    years: int = 10,
) -> Dict:
    """
    Model biochar production from rice straw and carbon credit revenue.
    
    Pyrolysis science:
    - Rice straw → biochar conversion: 25-35% by weight (temp dependent)
    - Higher temp → less biochar but higher carbon content
    - Carbon content: 40-70% of biochar mass
    - Each kg biochar sequesters ~2.5-3.5 kg CO2eq (stable for 100+ years)
    
    Thailand T-VER carbon credits (2024):
    - Biomass projects: ฿35-500/tCO2eq
    - Average: ฿175/tCO2eq
    - Forest/agriculture: ฿300-2,076/tCO2eq
    - Global biochar credits: $153-220/tCO2eq (~฿5,500-7,900)
    
    Biochar as soil amendment:
    - Sale price: ฿8-20/kg
    - Increases rice yield 5-15%
    - Reduces fertilizer need 20-30%
    - Improves water retention
    """
    # Pyrolysis conversion rate depends on temperature
    if pyrolysis_temp <= 350:
        conversion_rate = 0.35
        carbon_content = 0.45
        stability_factor = 0.70
    elif pyrolysis_temp <= 500:
        conversion_rate = 0.30
        carbon_content = 0.55
        stability_factor = 0.80
    elif pyrolysis_temp <= 650:
        conversion_rate = 0.25
        carbon_content = 0.65
        stability_factor = 0.90
    else:
        conversion_rate = 0.22
        carbon_content = 0.70
        stability_factor = 0.95
    
    biochar_kg = straw_for_biochar_kg * conversion_rate
    carbon_in_biochar = biochar_kg * carbon_content
    stable_carbon = carbon_in_biochar * stability_factor
    
    # CO2 equivalent: 1 kg C = 3.67 kg CO2
    co2_sequestered = stable_carbon * 3.67
    co2_tonnes = co2_sequestered / 1000
    
    # Avoided emissions from NOT burning this straw
    # Rice straw burning emits ~1.5 kg CO2eq per kg straw (includes CH4, N2O)
    avoided_emissions_kg = straw_for_biochar_kg * 1.5
    avoided_tonnes = avoided_emissions_kg / 1000
    
    total_carbon_benefit_tonnes = co2_tonnes + avoided_tonnes
    
    # Revenue streams
    # 1. Carbon credits (T-VER)
    carbon_credit_revenue = total_carbon_benefit_tonnes * carbon_credit_price
    
    # 2. Biochar sales
    biochar_revenue = biochar_kg * biochar_sale_price
    
    # 3. Soil improvement value (if used on own farm)
    yield_increase_pct = 0.10  # 10% rice yield increase
    rice_income_per_rai = 8000  # ฿/rai from rice
    soil_value = rai * rice_income_per_rai * yield_increase_pct
    
    # 4. Fertilizer savings
    fert_savings = rai * 500  # ฿500/rai saved
    
    # Costs
    pyrolysis_fuel_cost = straw_for_biochar_kg * 0.5
    labor_cost = straw_for_biochar_kg * 0.3
    equipment_amortized = 20000 / 5  # Simple kiln, 5-year life
    tver_registration = 5000  # Annual T-VER fees
    total_cost = pyrolysis_fuel_cost + labor_cost + equipment_amortized + tver_registration
    
    total_revenue = carbon_credit_revenue + biochar_revenue + soil_value + fert_savings
    net_profit = total_revenue - total_cost
    
    # Multi-year projection
    yearly = []
    for y in range(1, years + 1):
        # Carbon credit prices growing ~15% per year
        price_growth = carbon_credit_price * (1.15 ** (y - 1))
        yr_carbon_rev = total_carbon_benefit_tonnes * price_growth
        yr_biochar_rev = biochar_revenue
        yr_soil = soil_value
        yr_fert = fert_savings
        yr_cost = total_cost if y > 1 else total_cost + 20000  # extra setup cost year 1
        yr_total = yr_carbon_rev + yr_biochar_rev + yr_soil + yr_fert
        yr_net = yr_total - yr_cost
        
        yearly.append({
            'year': y,
            'carbon_price': round(price_growth),
            'carbon_revenue': round(yr_carbon_rev),
            'biochar_revenue': round(yr_biochar_rev),
            'soil_value': round(yr_soil),
            'fert_savings': round(yr_fert),
            'total_revenue': round(yr_total),
            'cost': round(yr_cost),
            'net_profit': round(yr_net),
            'cumulative_co2': round(total_carbon_benefit_tonnes * y, 1),
        })
    
    return {
        'biochar_kg': round(biochar_kg),
        'carbon_content_pct': round(carbon_content * 100),
        'co2_sequestered_kg': round(co2_sequestered),
        'co2_sequestered_tonnes': round(co2_tonnes, 2),
        'avoided_emissions_tonnes': round(avoided_tonnes, 2),
        'total_carbon_benefit_tonnes': round(total_carbon_benefit_tonnes, 2),
        'carbon_credit_revenue': round(carbon_credit_revenue),
        'biochar_revenue': round(biochar_revenue),
        'soil_value': round(soil_value),
        'fert_savings': round(fert_savings),
        'total_revenue': round(total_revenue),
        'total_cost': round(total_cost),
        'net_profit': round(net_profit),
        'yearly': yearly,
        'pyrolysis_temp': pyrolysis_temp,
        'conversion_rate': round(conversion_rate * 100),
        'revenue_breakdown': [
            {'source': 'Carbon Credits (T-VER)', 'emoji': '🌿', 'amount': round(carbon_credit_revenue)},
            {'source': 'Biochar Sales', 'emoji': '⬛', 'amount': round(biochar_revenue)},
            {'source': 'Soil Improvement', 'emoji': '🌾', 'amount': round(soil_value)},
            {'source': 'Fertilizer Savings', 'emoji': '💊', 'amount': round(fert_savings)},
        ],
    }



def compute_enzymatic_pretreatment(
    straw_kg: float = 9750,
    enzyme_type: str = 'cellulase_complex',
    enzyme_dose_pct: float = 1.0,
    species: str = 'oyster',
    cycles: int = 5,
) -> Dict:
    """Model enzymatic pre-treatment of rice straw to boost mushroom yield."""
    enzymes = {
        'cellulase_complex': {'name': 'Cellulase Complex', 'emoji': '\U0001f9ec',
            'be_boost': 0.45, 'cost_per_kg': 15,
            'desc': 'Breaks cellulose into glucose. Most cost-effective.'},
        'laccase': {'name': 'Laccase (Lignin)', 'emoji': '\U0001f52c',
            'be_boost': 0.30, 'cost_per_kg': 25,
            'desc': 'Degrades lignin barrier, exposing cellulose.'},
        'xylanase': {'name': 'Xylanase', 'emoji': '\U0001f9ea',
            'be_boost': 0.20, 'cost_per_kg': 12,
            'desc': 'Breaks hemicellulose. Cheapest, moderate effect.'},
        'full_cocktail': {'name': 'Full Cocktail (All 3)', 'emoji': '\U0001f489',
            'be_boost': 0.75, 'cost_per_kg': 35,
            'desc': 'Maximum synergistic effect. Best for premium species.'},
    }
    species_data = {
        'straw': {'name': 'Straw Mushroom', 'base_be': 0.12, 'price': 55},
        'oyster': {'name': 'Oyster Mushroom', 'base_be': 0.95, 'price': 75},
        'king_oyster': {'name': 'King Oyster', 'base_be': 0.55, 'price': 100},
        'shiitake': {'name': 'Shiitake', 'base_be': 0.75, 'price': 260},
        'lions_mane': {'name': "Lion's Mane", 'base_be': 0.40, 'price': 700},
    }
    enz = enzymes[enzyme_type]
    sp = species_data.get(species, species_data['oyster'])
    dose_factor = min(enzyme_dose_pct / 1.0, 1.5)
    actual_boost = enz['be_boost'] * dose_factor
    base_be = sp['base_be']
    treated_be = base_be * (1 + actual_boost)

    base_yield = straw_kg * base_be * cycles
    treated_yield = straw_kg * treated_be * cycles
    yield_increase = treated_yield - base_yield

    base_revenue = base_yield * sp['price']
    treated_revenue = treated_yield * sp['price']
    revenue_increase = treated_revenue - base_revenue

    enzyme_kg_used = straw_kg * (enzyme_dose_pct / 100) * cycles
    enzyme_cost = enzyme_kg_used * enz['cost_per_kg']
    net_gain = revenue_increase - enzyme_cost
    roi = (net_gain / enzyme_cost * 100) if enzyme_cost > 0 else 0

    comparison = []
    for etype, edata in enzymes.items():
        eb = edata['be_boost'] * dose_factor
        t_be = base_be * (1 + eb)
        t_yield = straw_kg * t_be * cycles
        t_rev = t_yield * sp['price']
        e_kg = straw_kg * (enzyme_dose_pct / 100) * cycles
        e_cost = e_kg * edata['cost_per_kg']
        n_gain = (t_rev - base_revenue) - e_cost
        comparison.append({
            'type': edata['name'], 'emoji': edata['emoji'],
            'be_boost_pct': round(eb * 100), 'treated_be': round(t_be, 3),
            'yield_kg': round(t_yield), 'revenue': round(t_rev),
            'enzyme_cost': round(e_cost), 'net_gain': round(n_gain),
            'roi_pct': round((n_gain / e_cost * 100) if e_cost > 0 else 0),
            'desc': edata['desc'],
        })
    comparison.sort(key=lambda x: x['net_gain'], reverse=True)

    return {
        'species': sp['name'], 'enzyme': enz['name'],
        'base_be': round(base_be, 3), 'treated_be': round(treated_be, 3),
        'be_boost_pct': round(actual_boost * 100),
        'base_yield_kg': round(base_yield), 'treated_yield_kg': round(treated_yield),
        'yield_increase_kg': round(yield_increase),
        'base_revenue': round(base_revenue), 'treated_revenue': round(treated_revenue),
        'revenue_increase': round(revenue_increase),
        'enzyme_cost': round(enzyme_cost), 'net_gain': round(net_gain),
        'roi_pct': round(roi), 'comparison': comparison,
    }


def compute_mycelium_materials(
    straw_kg: float = 5000,
    product_mix: str = 'packaging',
    production_scale: str = 'small',
) -> Dict:
    """Model mycelium-based material production from rice straw."""
    products = {
        'packaging': {
            'name': 'Mycelium Packaging', 'emoji': '\U0001f4e6',
            'growth_days': 7, 'conversion_rate': 0.80,
            'unit': 'units', 'kg_per_unit': 0.5,
            'price_per_unit': 25, 'cost_per_unit': 8,
            'market': 'Replace styrofoam for electronics, food, cosmetics',
            'competitors': 'Ecovative, Magical Mushroom Company',
            'difficulty': 'Medium',
        },
        'leather': {
            'name': 'Mycelium Leather', 'emoji': '\U0001f45c',
            'growth_days': 14, 'conversion_rate': 0.15,
            'unit': 'm\u00b2', 'kg_per_unit': 2.0,
            'price_per_unit': 800, 'cost_per_unit': 200,
            'market': 'Fashion, accessories, automotive interiors',
            'competitors': 'MycoWorks (Hermes), Bolt Threads (Mylo)',
            'difficulty': 'Hard',
        },
        'insulation': {
            'name': 'Building Insulation', 'emoji': '\U0001f9f1',
            'growth_days': 10, 'conversion_rate': 0.70,
            'unit': 'panels', 'kg_per_unit': 3.0,
            'price_per_unit': 150, 'cost_per_unit': 40,
            'market': 'Construction, renovation, eco-building',
            'competitors': 'Myceen, Biohm',
            'difficulty': 'Medium',
        },
    }
    scales = {
        'small': {'name': 'Cottage', 'multiplier': 1.0, 'setup': 50000, 'label': 'Home workshop'},
        'medium': {'name': 'Workshop', 'multiplier': 3.0, 'setup': 250000, 'label': 'Cooperative'},
        'large': {'name': 'Factory', 'multiplier': 10.0, 'setup': 2000000, 'label': 'Industrial'},
    }
    prod = products[product_mix]
    scale = scales[production_scale]

    usable_straw = straw_kg * prod['conversion_rate']
    effective_units = (usable_straw / prod['kg_per_unit']) * scale['multiplier']

    gross_revenue = effective_units * prod['price_per_unit']
    production_cost = effective_units * prod['cost_per_unit']
    setup_amortized = scale['setup'] / 5
    labor = effective_units * 3 * (1 if production_scale == 'small' else 0.5)
    total_cost = production_cost + setup_amortized + labor
    net_profit = gross_revenue - total_cost

    mushroom_baseline = straw_kg * 0.12 * 55
    mushroom_oyster = straw_kg * 0.95 * 75

    all_products = []
    for ptype, pdata in products.items():
        u_straw = straw_kg * pdata['conversion_rate']
        u_prod = (u_straw / pdata['kg_per_unit']) * scale['multiplier']
        g_rev = u_prod * pdata['price_per_unit']
        p_cost = u_prod * pdata['cost_per_unit'] + setup_amortized
        p_labor = u_prod * 3 * (1 if production_scale == 'small' else 0.5)
        n_prof = g_rev - p_cost - p_labor
        all_products.append({
            'product': pdata['name'], 'emoji': pdata['emoji'],
            'units': round(u_prod), 'revenue': round(g_rev),
            'cost': round(p_cost + p_labor), 'profit': round(n_prof),
            'vs_mushroom': round(n_prof / mushroom_baseline if mushroom_baseline > 0 else 0, 1),
            'difficulty': pdata['difficulty'], 'market': pdata['market'],
        })
    all_products.sort(key=lambda x: x['profit'], reverse=True)

    return {
        'product': prod['name'], 'emoji': prod['emoji'],
        'scale': scale['name'], 'scale_label': scale['label'],
        'units_produced': round(effective_units),
        'gross_revenue': round(gross_revenue),
        'total_cost': round(total_cost),
        'net_profit': round(net_profit),
        'setup_cost': scale['setup'],
        'multiplier_vs_straw': round(net_profit / mushroom_baseline if mushroom_baseline > 0 else 0, 1),
        'multiplier_vs_oyster': round(net_profit / mushroom_oyster if mushroom_oyster > 0 else 0, 1),
        'all_products': all_products,
        'growth_days': prod['growth_days'],
        'market_info': prod['market'],
        'competitors': prod['competitors'],
    }


# ================================================================
# DRONE OPERATIONS & ROI ENGINE (Round 9)
# ================================================================

def compute_drone_operations(
    n_rai: float = 15,
    drone_model: str = 'service',
    use_cases: list = None,
    cooperative_size: int = 10,
    subsidy_pct: float = 60,
    spray_cycles_per_year: int = 6,
    monitoring_flights_per_year: int = 12,
) -> Dict:
    """
    Comprehensive drone ROI model for Thai rice + mushroom farming.
    
    Sources (verified):
    - DJI Agras T10 price: ฿204,000 (package w/ 2 batteries, Siam Kubota)
    - DJI Agras T10 drone only: ฿153,000
    - Spray service: ฿60-100/rai (Winrock/Bangkok Post)
    - Manual spray: ฿150-300/rai (Winrock)
    - DEPA subsidy: 60% of drone cost (One Drone, One Community)
    - Chemical reduction: 40% (DJI Thailand/Winrock)
    - Production loss reduction: 10-15% (DJI/IDE)
    - Rice productivity boost: up to 15% (Oreateai)
    - CAAT regulations: register, 30m altitude, 6AM-6PM, no-fly near airports
    - DJI drone sales in Thailand: 50x increase by end 2024
    - 10,000+ certified operators in Thailand (DJI 2024)
    """
    if use_cases is None:
        use_cases = ['spray', 'monitoring', 'burn_detection']
    
    # ─── Drone models with Thai pricing ───
    drone_models = {
        'service': {
            'name': 'Drone Service (Hire)',
            'purchase_cost': 0,
            'annual_maintenance': 0,
            'battery_cost': 0,
            'spray_cost_per_rai': 80,  # ฿/rai per application
            'coverage_rai_per_hour': 0,
            'tank_liters': 0,
            'description': 'Hire a local drone service provider — no investment needed',
        },
        'dji_t10': {
            'name': 'DJI Agras T10',
            'purchase_cost': 204000,  # ฿ package with 2 batteries
            'annual_maintenance': 8000,
            'battery_cost': 25500,
            'spray_cost_per_rai': 15,  # fuel + chemicals only
            'coverage_rai_per_hour': 8,  # 8 rai/hr
            'tank_liters': 8,
            'description': '8L tank, entry-level ag drone, ideal for cooperatives',
        },
        'dji_t25': {
            'name': 'DJI Agras T25',
            'purchase_cost': 385000,  # ~$10,999 USD
            'annual_maintenance': 12000,
            'battery_cost': 35000,
            'spray_cost_per_rai': 12,
            'coverage_rai_per_hour': 15,
            'tank_liters': 20,
            'description': '20L tank, AI obstacle avoidance, terrain following',
        },
        'dji_t50': {
            'name': 'DJI Agras T50',
            'purchase_cost': 560000,  # ~$15,999 USD
            'annual_maintenance': 18000,
            'battery_cost': 45000,
            'spray_cost_per_rai': 10,
            'coverage_rai_per_hour': 25,
            'tank_liters': 40,
            'description': '40L tank, dual atomizers, largest capacity for serious ops',
        },
        'thai_local': {
            'name': 'Thai-Made GCS-9',
            'purchase_cost': 75000,
            'annual_maintenance': 5000,
            'battery_cost': 12000,
            'spray_cost_per_rai': 20,
            'coverage_rai_per_hour': 5,
            'tank_liters': 10,
            'description': 'Locally made drone, lower cost, basic features',
        },
    }
    
    drone = drone_models[drone_model]
    total_rai = n_rai * cooperative_size
    
    # ─── USE CASE 1: Precision Spraying ───
    spray_results = {}
    if 'spray' in use_cases:
        manual_cost_per_rai = 200  # ฿/rai for manual spraying
        manual_chemical_cost_per_rai = 300  # chemicals per rai
        
        # Drone spraying
        if drone_model == 'service':
            drone_spray_cost = drone['spray_cost_per_rai'] * total_rai * spray_cycles_per_year
        else:
            drone_spray_cost = drone['spray_cost_per_rai'] * total_rai * spray_cycles_per_year
        
        # Manual baseline
        manual_total = (manual_cost_per_rai + manual_chemical_cost_per_rai) * total_rai * spray_cycles_per_year
        
        # Chemical savings (40% reduction from precision spraying)
        chemical_savings_pct = 40
        drone_chemical_cost = manual_chemical_cost_per_rai * (1 - chemical_savings_pct / 100) * total_rai * spray_cycles_per_year
        
        drone_total_spray = drone_spray_cost + drone_chemical_cost
        spray_savings = manual_total - drone_total_spray
        
        # Yield improvement from better pest/disease management
        yield_boost_pct = 12  # 10-15% documented
        base_rice_income_per_rai = 4500  # ฿/rai rice income
        yield_income_boost = base_rice_income_per_rai * (yield_boost_pct / 100) * total_rai
        
        spray_results = {
            'manual_cost_annual': round(manual_total),
            'drone_cost_annual': round(drone_total_spray),
            'spray_savings': round(spray_savings),
            'chemical_reduction_pct': chemical_savings_pct,
            'yield_boost_pct': yield_boost_pct,
            'yield_income_boost': round(yield_income_boost),
            'total_spray_benefit': round(spray_savings + yield_income_boost),
        }
    
    # ─── USE CASE 2: Crop Monitoring & NDVI ───
    monitoring_results = {}
    if 'monitoring' in use_cases:
        # Multispectral camera add-on
        camera_cost = 45000 if drone_model != 'service' else 0
        monitoring_service_cost = 50 * total_rai if drone_model == 'service' else 0  # ฿50/rai for monitoring service
        
        # Early disease detection saves 5-8% of crop loss
        disease_detection_saving_pct = 6
        crop_value = base_rice_income_per_rai if 'spray' in use_cases else 4500
        disease_savings = crop_value * (disease_detection_saving_pct / 100) * total_rai
        
        # Water management optimization
        water_savings_per_rai = 150  # ฿/rai from optimal irrigation timing
        water_savings = water_savings_per_rai * total_rai
        
        # Straw inventory mapping for mushroom farming
        straw_mapping_value = 50 * total_rai  # ฿50/rai better straw collection efficiency
        
        monitoring_cost = monitoring_service_cost + (camera_cost / 5 if camera_cost > 0 else 0)  # amortize camera over 5 years
        
        monitoring_results = {
            'monitoring_flights_per_year': monitoring_flights_per_year,
            'camera_cost': camera_cost,
            'annual_monitoring_cost': round(monitoring_cost),
            'disease_detection_savings': round(disease_savings),
            'water_savings': round(water_savings),
            'straw_mapping_value': round(straw_mapping_value),
            'total_monitoring_benefit': round(disease_savings + water_savings + straw_mapping_value - monitoring_cost),
        }
    
    # ─── USE CASE 3: Burn Detection & Carbon Credit Verification ───
    burn_results = {}
    if 'burn_detection' in use_cases:
        # Thermal camera for burn spot detection
        thermal_camera_cost = 35000 if drone_model != 'service' else 0
        burn_detection_service = 30 * total_rai if drone_model == 'service' else 0  # ฿30/rai
        
        # Value: proves zero-burn compliance for T-VER carbon credits
        # Without proof → no credits. With drone proof → ฿175-2,076/tCO₂
        tco2_per_rai = 0.053  # from our carbon credits engine
        baseline_credit_value = tco2_per_rai * total_rai * 500  # mid-range T-VER price
        
        # Premium for drone-verified credits (higher trust = higher price)
        drone_verified_premium = 1.30  # 30% premium for drone MRV
        verified_credit_value = baseline_credit_value * drone_verified_premium
        premium_value = verified_credit_value - baseline_credit_value
        
        # Penalty avoidance (Thai govt 2026 regulations)
        # Farmers face loss of subsidies + potential fines for burning
        penalty_avoidance = 5000 * cooperative_size  # ฿5,000 per farmer subsidy protection
        
        burn_detection_cost = burn_detection_service + (thermal_camera_cost / 5 if thermal_camera_cost > 0 else 0)
        
        burn_results = {
            'thermal_camera_cost': thermal_camera_cost,
            'annual_detection_cost': round(burn_detection_cost),
            'baseline_credit_value': round(baseline_credit_value),
            'verified_credit_value': round(verified_credit_value),
            'drone_premium_value': round(premium_value),
            'penalty_avoidance': round(penalty_avoidance),
            'total_burn_benefit': round(verified_credit_value + penalty_avoidance - burn_detection_cost),
        }
    
    # ─── Investment & ROI ───
    if drone_model == 'service':
        total_investment = 0
        annual_fixed_cost = 0
    else:
        subsidy_amount = drone['purchase_cost'] * (subsidy_pct / 100)
        net_purchase = drone['purchase_cost'] - subsidy_amount
        extra_batteries = drone['battery_cost'] * 2  # 2 extra batteries
        total_investment = net_purchase + extra_batteries
        annual_fixed_cost = drone['annual_maintenance'] + (total_investment / 5)  # 5-year depreciation
    
    total_annual_benefit = (
        spray_results.get('total_spray_benefit', 0) +
        monitoring_results.get('total_monitoring_benefit', 0) +
        burn_results.get('total_burn_benefit', 0)
    )
    
    total_annual_cost = annual_fixed_cost + (
        spray_results.get('drone_cost_annual', 0) if drone_model != 'service' else
        spray_results.get('drone_cost_annual', 0)
    )
    
    net_annual_benefit = total_annual_benefit - annual_fixed_cost
    roi_pct = (net_annual_benefit / total_investment * 100) if total_investment > 0 else float('inf')
    payback_years = total_investment / net_annual_benefit if net_annual_benefit > 0 else 99
    
    # ─── Service income opportunity ───
    # A trained operator can earn income by servicing other farmers
    service_income = 0
    if drone_model != 'service':
        available_hours = 200  # hours/year servicing others
        service_rate = drone['coverage_rai_per_hour'] * 80  # ฿80/rai service charge
        service_income = available_hours * service_rate
    
    # ─── Regulatory compliance ───
    regulations = {
        'registration': 'Required with CAAT (Civil Aviation Authority of Thailand)',
        'operator_cert': 'Agricultural flight authorization needed',
        'flight_hours': '6:00 AM - 6:00 PM only',
        'max_altitude': '30 meters',
        'notification': '12 hours advance via CAAT UAS Portal',
        'insurance': 'Third-party liability required (based on drone weight)',
        'penalty': 'Up to 1 year imprisonment / ฿40,000 fine for violations',
        'no_fly_zones': '9km radius from airports',
    }
    
    return {
        'drone': drone,
        'drone_model': drone_model,
        'total_rai': total_rai,
        'cooperative_size': cooperative_size,
        'spray': spray_results,
        'monitoring': monitoring_results,
        'burn_detection': burn_results,
        'investment': {
            'drone_cost': drone['purchase_cost'],
            'subsidy_pct': subsidy_pct,
            'subsidy_amount': round(drone['purchase_cost'] * subsidy_pct / 100),
            'net_investment': round(total_investment),
            'annual_fixed_cost': round(annual_fixed_cost),
        },
        'roi': {
            'total_annual_benefit': round(total_annual_benefit),
            'net_annual_benefit': round(net_annual_benefit),
            'roi_pct': round(roi_pct, 1),
            'payback_years': round(payback_years, 2),
        },
        'service_income': round(service_income),
        'per_farmer': {
            'investment': round(total_investment / cooperative_size) if cooperative_size > 0 else 0,
            'annual_benefit': round(total_annual_benefit / cooperative_size) if cooperative_size > 0 else 0,
        },
        'regulations': regulations,
    }


# ================================================================
# DRONE COLD PASTEURIZATION ENGINE (Round 9 — Lab 35)
# ================================================================

def compute_cold_pasteurization(
    n_rai: float = 15,
    straw_per_rai: float = 650,
    method: str = 'lime',
    drone_model: str = 'dji_t10',
    cooperative_size: int = 10,
    mushroom_price: float = 60,
    be_pct: float = 12,
) -> Dict:
    """
    Compare pasteurization methods: traditional steam vs drone-delivered
    cold pasteurization (lime, H₂O₂, fermentation).
    
    Sources (verified):
    - Lime pasteurization: 2g Ca(OH)₂/L water, pH 12+, soak 12-24h (GroCycle, FreshCap)
    - Hydrogen peroxide: 3% H₂O₂, 1:10 dilution, soak 12-24h (BellaBora, HouseDigest)
    - Cold water fermentation: plain water, 7-14 days anaerobic (NAMYCO)
    - Log reduction equivalent to steam for all chemical methods (GroCycle)
    - Hydrated lime price Thailand: ~฿8/kg (bulk agricultural grade)
    - H₂O₂ 35% price Thailand: ~฿80/L (industrial grade)
    - Contamination rate impact from method choice: 2-15% range
    """
    
    total_straw_kg = n_rai * straw_per_rai * cooperative_size
    
    # ─── Water requirements: ~3L water per 1kg dry straw for soaking ───
    water_per_kg_straw = 3.0  # liters
    total_water_liters = total_straw_kg * water_per_kg_straw
    
    # ─── Method definitions ───
    methods = {
        'steam': {
            'name': '🔥 Traditional Steam Boiler',
            'description': 'Barrel + coil boiler at 80-100°C for 45-90 min',
            'treatment_type': 'thermal',
            'drone_compatible': False,
            # Equipment
            'equipment_cost': 50000,  # ฿ for boiler + barrels + coil
            'equipment_lifespan_years': 10,
            # Per-batch costs
            'fuel_cost_per_batch': 150,  # ฿ rice husk/firewood per pasteurization batch
            'chemical_cost_per_kg_straw': 0,
            'water_cost_per_liter': 0.05,
            'labor_hours_per_batch': 4,  # loading, firing, monitoring, unloading
            'batch_size_kg': 100,  # kg straw per barrel batch
            # Time
            'heating_time_hours': 1.5,
            'treatment_time_hours': 1.5,
            'cooling_time_hours': 8,
            'total_cycle_hours': 11,
            # Effectiveness
            'contamination_rate_pct': 3,  # well-managed steam = low contamination
            'be_modifier': 1.0,  # baseline
            'log_reduction': 5,
            # Pros/Cons
            'pros': ['Most reliable kill', 'Well-documented', 'No chemical residue'],
            'cons': ['High equipment cost', 'Fuel needed', 'Labor intensive', 'Not scalable', 'Energy waste'],
        },
        'lime': {
            'name': '🧪 Lime Cold Pasteurization (Drone-Spray)',
            'description': 'Ca(OH)₂ solution raises pH to 12+ → kills contaminants in 12-24h',
            'treatment_type': 'chemical_alkaline',
            'drone_compatible': True,
            # Equipment: just drone (shared) + containers
            'equipment_cost': 5000,  # ฿ containers/tarps only
            'equipment_lifespan_years': 5,
            # Per-batch costs
            'fuel_cost_per_batch': 0,
            'chemical_cost_per_kg_straw': 0.40,  # 2g lime/L × 3L/kg × ฿8/kg ÷ 1000 = ฿0.048... but need more for buffer
            'water_cost_per_liter': 0.05,
            'labor_hours_per_batch': 1.5,  # load straw into container, drone sprays, drain
            'batch_size_kg': 500,  # much larger batches possible (open containers)
            # Time
            'heating_time_hours': 0,
            'treatment_time_hours': 18,  # 12-24h soak average
            'cooling_time_hours': 0,
            'total_cycle_hours': 20,  # soak + drain
            # Effectiveness
            'contamination_rate_pct': 5,  # slightly higher than steam but very good
            'be_modifier': 0.98,  # nearly equal to steam
            'log_reduction': 4,
            # Lime specifics
            'lime_grams_per_liter': 2,
            'target_ph': 12.0,
            'lime_price_per_kg': 8,  # ฿/kg hydrated lime (Ca(OH)₂) in Thailand
            # Pros/Cons
            'pros': ['No fuel/energy needed', 'Drone-compatible spray', '80% cheaper', 'Scales easily', 'Proven effective'],
            'cons': ['12-24h soak time', 'Must use hydrated lime (not garden lime)', 'Slightly higher contamination'],
        },
        'h2o2': {
            'name': '🧴 Hydrogen Peroxide (Drone-Spray)',
            'description': '3% H₂O₂ solution → oxidative kill. Mycelium naturally resistant!',
            'treatment_type': 'chemical_oxidative',
            'drone_compatible': True,
            # Equipment
            'equipment_cost': 5000,
            'equipment_lifespan_years': 5,
            # Per-batch costs
            'fuel_cost_per_batch': 0,
            'chemical_cost_per_kg_straw': 1.60,  # higher chemical cost than lime
            'water_cost_per_liter': 0.05,
            'labor_hours_per_batch': 1.5,
            'batch_size_kg': 500,
            # Time
            'heating_time_hours': 0,
            'treatment_time_hours': 18,
            'cooling_time_hours': 0,
            'total_cycle_hours': 20,
            # Effectiveness
            'contamination_rate_pct': 4,
            'be_modifier': 1.02,  # slight boost — H₂O₂ breaks down lignocellulose slightly
            'log_reduction': 4.5,
            # H₂O₂ specifics
            'h2o2_conc_pct': 3,
            'dilution_ratio': '1:10',
            'h2o2_35pct_price_per_liter': 80,  # ฿/L industrial 35% H₂O₂
            # Pros/Cons
            'pros': ['No fuel needed', 'Drone-compatible', 'Mycelium is naturally resistant', 'Slight BE boost', 'Clean decomposition to water + O₂'],
            'cons': ['Higher chemical cost', 'Must handle 35% H₂O₂ carefully', 'Storage concerns'],
        },
        'fermentation': {
            'name': '💧 Cold Water Fermentation',
            'description': 'Submerge in water 7-14 days → anaerobic bacteria kill competitors',
            'treatment_type': 'biological',
            'drone_compatible': False,  # no drone needed at all
            # Equipment
            'equipment_cost': 3000,  # ฿ just containers
            'equipment_lifespan_years': 10,
            # Per-batch costs
            'fuel_cost_per_batch': 0,
            'chemical_cost_per_kg_straw': 0,
            'water_cost_per_liter': 0.05,
            'labor_hours_per_batch': 1,
            'batch_size_kg': 1000,  # can do very large batches in ponds
            # Time
            'heating_time_hours': 0,
            'treatment_time_hours': 240,  # 10 days average
            'cooling_time_hours': 0,
            'total_cycle_hours': 264,  # 11 days total including drain
            # Effectiveness
            'contamination_rate_pct': 8,  # less reliable
            'be_modifier': 0.95,  # slightly lower BE
            'log_reduction': 3,
            # Pros/Cons
            'pros': ['Zero cost (just water)', 'Zero energy', 'Largest batch size', 'Zero chemicals'],
            'cons': ['7-14 day wait', 'Bad smell', 'Less reliable', 'Weather dependent', 'Lower BE'],
        },
    }
    
    m = methods[method]
    labor_rate = 370  # ฿/day (Thai minimum wage 2025) = ฿46.25/hr
    labor_per_hour = labor_rate / 8
    
    # ─── Calculate annual costs ───
    # How many batches per year?
    total_annual_straw = total_straw_kg  # all straw from cooperative
    batches_per_year = total_annual_straw / m['batch_size_kg']
    
    # Equipment annual cost (depreciation)
    annual_equipment = m['equipment_cost'] / m['equipment_lifespan_years']
    
    # Fuel cost
    annual_fuel = m['fuel_cost_per_batch'] * batches_per_year
    
    # Chemical cost
    annual_chemical = m['chemical_cost_per_kg_straw'] * total_annual_straw
    
    # Water cost
    annual_water = total_water_liters * m['water_cost_per_liter']
    
    # Labor cost
    annual_labor = m['labor_hours_per_batch'] * batches_per_year * labor_per_hour
    
    # Drone cost (if drone-compatible and using drone for delivery)
    drone_delivery_cost = 0
    if m['drone_compatible']:
        # Drone sprays 80 rai/hour for liquid, estimate for straw soaking
        spray_rate_per_hour = 60  # ฿/hour for drone service
        spray_hours = total_water_liters / 600  # 600 L/hr spray rate (DJI T50)
        drone_delivery_cost = spray_hours * spray_rate_per_hour
    
    total_annual_cost = annual_equipment + annual_fuel + annual_chemical + annual_water + annual_labor + drone_delivery_cost
    
    # ─── Revenue impact ───
    effective_be = be_pct * m['be_modifier']
    total_mushroom_kg = total_annual_straw * (effective_be / 100)
    # Account for contamination losses
    good_harvest_kg = total_mushroom_kg * (1 - m['contamination_rate_pct'] / 100)
    revenue = good_harvest_kg * mushroom_price
    
    # ─── Throughput ───
    batches_per_day = 24 / m['total_cycle_hours'] if m['total_cycle_hours'] > 0 else 1
    daily_capacity_kg = batches_per_day * m['batch_size_kg']
    days_to_process_all = total_annual_straw / daily_capacity_kg if daily_capacity_kg > 0 else 999
    
    # ─── Compare vs steam baseline ───
    steam = methods['steam']
    steam_batches = total_annual_straw / steam['batch_size_kg']
    steam_annual_cost = (
        steam['equipment_cost'] / steam['equipment_lifespan_years'] +
        steam['fuel_cost_per_batch'] * steam_batches +
        total_water_liters * steam['water_cost_per_liter'] +
        steam['labor_hours_per_batch'] * steam_batches * labor_per_hour
    )
    
    steam_be = be_pct * steam['be_modifier']
    steam_mushroom = total_annual_straw * (steam_be / 100) * (1 - steam['contamination_rate_pct'] / 100)
    steam_revenue = steam_mushroom * mushroom_price
    steam_profit = steam_revenue - steam_annual_cost
    
    profit = revenue - total_annual_cost
    savings_vs_steam = total_annual_cost - steam_annual_cost  # negative means cheaper
    profit_advantage = profit - steam_profit
    
    # ─── Boiler elimination analysis ───
    boiler_eliminated = not methods[method]['treatment_type'] == 'thermal'
    boiler_savings = 50000 if boiler_eliminated else 0  # one-time equipment savings
    
    return {
        'method': m,
        'method_key': method,
        'cooperative_size': cooperative_size,
        'total_straw_kg': round(total_straw_kg),
        'total_water_liters': round(total_water_liters),
        'costs': {
            'equipment_annual': round(annual_equipment),
            'fuel': round(annual_fuel),
            'chemicals': round(annual_chemical),
            'water': round(annual_water),
            'labor': round(annual_labor),
            'drone_delivery': round(drone_delivery_cost),
            'total_annual': round(total_annual_cost),
            'cost_per_kg_straw': round(total_annual_cost / total_annual_straw, 2) if total_annual_straw > 0 else 0,
        },
        'production': {
            'effective_be': round(effective_be, 2),
            'contamination_rate': m['contamination_rate_pct'],
            'total_mushroom_kg': round(good_harvest_kg),
            'revenue': round(revenue),
            'profit': round(profit),
        },
        'throughput': {
            'batch_size_kg': m['batch_size_kg'],
            'batches_per_year': round(batches_per_year),
            'total_cycle_hours': m['total_cycle_hours'],
            'daily_capacity_kg': round(daily_capacity_kg),
            'days_to_process': round(days_to_process_all, 1),
        },
        'vs_steam': {
            'cost_savings': round(-savings_vs_steam),  # positive = we save money
            'cost_savings_pct': round((-savings_vs_steam / steam_annual_cost) * 100, 1) if steam_annual_cost > 0 else 0,
            'profit_advantage': round(profit_advantage),
            'boiler_eliminated': boiler_eliminated,
            'boiler_equipment_savings': boiler_savings,
        },
        'all_methods_comparison': _compare_all_methods(
            total_annual_straw, total_water_liters, be_pct, mushroom_price, labor_per_hour, cooperative_size
        ),
    }


def _compare_all_methods(total_straw, total_water, be_pct, price, labor_rate, coop_size):
    """Generate comparison data for all 4 methods (used for charts)."""
    method_keys = ['steam', 'lime', 'h2o2', 'fermentation']
    method_names = ['🔥 Steam', '🧪 Lime', '🧴 H₂O₂', '💧 Fermentation']
    
    results = []
    for key, name in zip(method_keys, method_names):
        m = {
            'steam': {'equip': 50000, 'life': 10, 'fuel_batch': 150, 'chem_per_kg': 0,
                     'labor_h': 4, 'batch_kg': 100, 'contam': 3, 'be_mod': 1.0, 'cycle_h': 11},
            'lime': {'equip': 5000, 'life': 5, 'fuel_batch': 0, 'chem_per_kg': 0.40,
                    'labor_h': 1.5, 'batch_kg': 500, 'contam': 5, 'be_mod': 0.98, 'cycle_h': 20},
            'h2o2': {'equip': 5000, 'life': 5, 'fuel_batch': 0, 'chem_per_kg': 1.60,
                    'labor_h': 1.5, 'batch_kg': 500, 'contam': 4, 'be_mod': 1.02, 'cycle_h': 20},
            'fermentation': {'equip': 3000, 'life': 10, 'fuel_batch': 0, 'chem_per_kg': 0,
                            'labor_h': 1, 'batch_kg': 1000, 'contam': 8, 'be_mod': 0.95, 'cycle_h': 264},
        }[key]
        
        batches = total_straw / m['batch_kg']
        cost = (
            m['equip'] / m['life'] +
            m['fuel_batch'] * batches +
            m['chem_per_kg'] * total_straw +
            total_water * 0.05 +
            m['labor_h'] * batches * labor_rate
        )
        
        eff_be = be_pct * m['be_mod']
        mushroom_kg = total_straw * (eff_be / 100) * (1 - m['contam'] / 100)
        revenue = mushroom_kg * price
        profit = revenue - cost
        
        results.append({
            'name': name,
            'key': key,
            'annual_cost': round(cost),
            'mushroom_kg': round(mushroom_kg),
            'revenue': round(revenue),
            'profit': round(profit),
            'cost_per_kg_straw': round(cost / total_straw, 2) if total_straw > 0 else 0,
            'contamination': m['contam'],
            'be': round(eff_be, 2),
        })
    
    return results


# ================================================================
# ROUND 10: VALUE-ADDED & OPTIMIZATION ENGINES (Labs 37-42)
# ================================================================

# ── LAB 37: SOLAR DRYING & VALUE-ADDED ──
def compute_solar_drying(
    annual_harvest_kg: float = 1000,
    pct_fresh: float = 50,
    pct_dried: float = 35,
    pct_powder: float = 15,
    fresh_price: float = 60,
    dried_price: float = 400,
    powder_price: float = 600,
    dryer_cost: float = 52000,
    dryer_lifespan: int = 10,
    cooperative_size: int = 10,
) -> Dict:
    """Solar drying ROI — fresh vs dried vs powder revenue comparison.
    Sources: Tridge.com Thai prices, tci-thaijo.org solar dryer costs, CGIAR drying ROI."""
    
    total_harvest = annual_harvest_kg * cooperative_size
    
    fresh_kg = total_harvest * (pct_fresh / 100)
    to_dry_kg = total_harvest * (pct_dried / 100)
    to_powder_kg = total_harvest * (pct_powder / 100)
    
    # Fresh mushrooms are 90% water → 10:1 drying ratio
    dried_kg = to_dry_kg / 10
    powder_kg = to_powder_kg / 10
    
    rev_fresh = fresh_kg * fresh_price
    rev_dried = dried_kg * dried_price
    rev_powder = powder_kg * powder_price
    total_rev = rev_fresh + rev_dried + rev_powder
    
    # Baseline: sell everything fresh
    baseline_rev = total_harvest * fresh_price
    
    # Costs
    annual_dryer_cost = dryer_cost / dryer_lifespan
    packaging_cost = (dried_kg + powder_kg) * 20  # ฿20/kg for vacuum seal bags
    labor_cost = (to_dry_kg + to_powder_kg) * 0.5  # ฿0.5/kg sorting + loading
    total_cost = annual_dryer_cost + packaging_cost + labor_cost
    
    benefit = total_rev - baseline_rev - total_cost
    
    return {
        'total_harvest': round(total_harvest),
        'products': {
            'fresh': {'kg': round(fresh_kg), 'revenue': round(rev_fresh)},
            'dried': {'kg_input': round(to_dry_kg), 'kg_output': round(dried_kg), 'revenue': round(rev_dried)},
            'powder': {'kg_input': round(to_powder_kg), 'kg_output': round(powder_kg), 'revenue': round(rev_powder)},
        },
        'total_revenue': round(total_rev),
        'baseline_revenue': round(baseline_rev),
        'revenue_gain': round(total_rev - baseline_rev),
        'revenue_multiplier': round(total_rev / baseline_rev, 2) if baseline_rev > 0 else 0,
        'costs': {
            'dryer_annual': round(annual_dryer_cost),
            'packaging': round(packaging_cost),
            'labor': round(labor_cost),
            'total': round(total_cost),
        },
        'net_benefit': round(benefit),
        'per_farmer': round(benefit / cooperative_size) if cooperative_size > 0 else 0,
        'payback_months': round((dryer_cost / (benefit / 12)) if benefit > 0 else 999, 1),
        'shelf_life': {'fresh_days': 5, 'dried_months': 12, 'powder_months': 18},
    }


# ── LAB 38: VERTICAL MULTI-TIER CULTIVATION ──
def compute_vertical_tiers(
    polyhouse_m2: float = 20,
    n_tiers: int = 4,
    bags_per_m2_per_tier: float = 5,
    bag_weight_kg: float = 2.5,
    be_pct: float = 25,
    cycles_per_year: int = 5,
    mushroom_price: float = 60,
    shelf_cost_per_tier: float = 500,
    cooperative_size: int = 10,
) -> Dict:
    """Vertical multi-tier bag stacking ROI.
    Sources: Veshenka-expert.info, WikiFarmer, CultivationAg."""
    
    # Baseline: single layer
    baseline_bags = polyhouse_m2 * bags_per_m2_per_tier * 1
    baseline_substrate = baseline_bags * bag_weight_kg
    baseline_yield_cycle = baseline_substrate * (be_pct / 100)
    baseline_annual = baseline_yield_cycle * cycles_per_year
    baseline_revenue = baseline_annual * mushroom_price
    
    # Multi-tier
    tier_bags = polyhouse_m2 * bags_per_m2_per_tier * n_tiers
    tier_substrate = tier_bags * bag_weight_kg
    tier_yield_cycle = tier_substrate * (be_pct / 100)
    tier_annual = tier_yield_cycle * cycles_per_year
    tier_revenue = tier_annual * mushroom_price
    
    # Costs
    shelf_investment = shelf_cost_per_tier * n_tiers * (polyhouse_m2 / 4)  # shelf units per 4m²
    extra_substrate_cost = (tier_substrate - baseline_substrate) * cycles_per_year * 1  # ฿1/kg straw
    extra_spawn_cost = (tier_bags - baseline_bags) * cycles_per_year * 3  # ฿3/bag spawn
    annual_extra_cost = extra_substrate_cost + extra_spawn_cost
    shelf_annual = shelf_investment / 5  # 5-year depreciation
    total_extra_annual = annual_extra_cost + shelf_annual
    
    extra_revenue = tier_revenue - baseline_revenue
    net_benefit = extra_revenue - total_extra_annual
    
    # Scale to cooperative
    coop_benefit = net_benefit * cooperative_size
    coop_investment = shelf_investment * cooperative_size
    
    return {
        'polyhouse_m2': polyhouse_m2,
        'n_tiers': n_tiers,
        'baseline': {
            'bags': round(baseline_bags), 'yield_annual_kg': round(baseline_annual),
            'revenue': round(baseline_revenue),
        },
        'multi_tier': {
            'bags': round(tier_bags), 'yield_annual_kg': round(tier_annual),
            'revenue': round(tier_revenue),
        },
        'yield_multiplier': round(n_tiers, 1),
        'extra_revenue': round(extra_revenue),
        'costs': {
            'shelf_investment': round(shelf_investment),
            'shelf_annual': round(shelf_annual),
            'extra_substrate': round(extra_substrate_cost),
            'extra_spawn': round(extra_spawn_cost),
            'total_annual': round(total_extra_annual),
        },
        'net_benefit': round(net_benefit),
        'per_farmer': round(net_benefit),
        'coop_benefit': round(coop_benefit),
        'payback_months': round((shelf_investment / (net_benefit / 12)) if net_benefit > 0 else 999, 1),
        'yield_per_m2': round(tier_annual / polyhouse_m2, 1),
    }


# ── LAB 39: SPAWN SELF-PRODUCTION ──
def compute_spawn_production(
    annual_bags: int = 2000,
    bought_spawn_per_bag: float = 3,
    bought_spawn_price_per_bag: float = 15,
    grain_cost_per_kg: float = 12,
    grain_per_bag: float = 0.3,
    lab_setup_cost: float = 15000,
    lab_lifespan: int = 10,
    pressure_cooker_cost: float = 3000,
    sab_cost: float = 500,
    consumables_annual: float = 3000,
    labor_hours_per_week: float = 4,
    cooperative_size: int = 10,
) -> Dict:
    """DIY spawn production vs buying — cost comparison.
    Sources: GroCycle, LivingWebFarms, BellaBora."""
    
    total_bags = annual_bags * cooperative_size
    
    # Buying spawn
    buy_cost = total_bags * bought_spawn_price_per_bag
    
    # DIY spawn
    grain_cost = total_bags * grain_per_bag * grain_cost_per_kg
    lab_annual = lab_setup_cost / lab_lifespan
    equipment_annual = (pressure_cooker_cost + sab_cost) / lab_lifespan
    labor_annual = labor_hours_per_week * 52 * (370 / 8)  # min wage hourly
    diy_cost = grain_cost + lab_annual + equipment_annual + consumables_annual + labor_annual
    
    savings = buy_cost - diy_cost
    savings_pct = (savings / buy_cost * 100) if buy_cost > 0 else 0
    
    total_investment = lab_setup_cost + pressure_cooker_cost + sab_cost
    
    return {
        'total_bags': total_bags,
        'buying': {
            'cost_per_bag': bought_spawn_price_per_bag,
            'annual_cost': round(buy_cost),
        },
        'diy': {
            'grain_cost': round(grain_cost),
            'lab_annual': round(lab_annual),
            'equipment_annual': round(equipment_annual),
            'consumables': consumables_annual,
            'labor': round(labor_annual),
            'annual_cost': round(diy_cost),
            'cost_per_bag': round(diy_cost / total_bags, 2) if total_bags > 0 else 0,
        },
        'savings': round(savings),
        'savings_pct': round(savings_pct, 1),
        'per_farmer': round(savings / cooperative_size) if cooperative_size > 0 else 0,
        'total_investment': total_investment,
        'payback_months': round((total_investment / (savings / 12)) if savings > 0 else 999, 1),
        'risks': {
            'contamination_risk': 'Medium — requires sterile technique training',
            'skill_required': 'Moderate — 2-3 day training recommended',
            'space_needed_m2': 5,
        },
    }


# ── LAB 40: E-COMMERCE CHANNELS ──
def compute_ecommerce_channels(
    annual_harvest_kg: float = 1000,
    pct_wet_market: float = 50,
    pct_shopee_lazada: float = 25,
    pct_line_direct: float = 15,
    pct_grow_kits: float = 10,
    wet_market_price: float = 60,
    online_dried_price: float = 400,
    line_fresh_price: float = 120,
    grow_kit_price: float = 250,
    grow_kit_cost: float = 50,
    packaging_cost_per_order: float = 15,
    shipping_cost_per_order: float = 40,
    platform_fee_pct: float = 5,
    avg_order_kg: float = 0.5,
    cooperative_size: int = 10,
) -> Dict:
    """E-commerce channel ROI — wet market vs online vs direct.
    Sources: Shopee.co.th, Lazada.co.th, EarthlingMushroomFarm."""
    
    total_harvest = annual_harvest_kg * cooperative_size
    
    # Wet market (baseline)
    wet_kg = total_harvest * (pct_wet_market / 100)
    wet_rev = wet_kg * wet_market_price
    
    # Shopee/Lazada (dried products)
    online_kg = total_harvest * (pct_shopee_lazada / 100)
    online_dried_output = online_kg / 10  # 10:1 fresh-to-dried
    online_orders = online_dried_output / avg_order_kg
    online_gross = online_dried_output * online_dried_price
    online_fees = online_gross * (platform_fee_pct / 100)
    online_packaging = online_orders * packaging_cost_per_order
    online_shipping = online_orders * shipping_cost_per_order
    online_net = online_gross - online_fees - online_packaging - online_shipping
    
    # LINE/Facebook direct (fresh premium)
    line_kg = total_harvest * (pct_line_direct / 100)
    line_orders = line_kg / avg_order_kg
    line_gross = line_kg * line_fresh_price
    line_packaging = line_orders * packaging_cost_per_order
    line_shipping = line_orders * shipping_cost_per_order
    line_net = line_gross - line_packaging - line_shipping
    
    # Grow kits
    kit_kg = total_harvest * (pct_grow_kits / 100)
    n_kits = kit_kg / 1  # 1kg substrate per kit
    kit_gross = n_kits * grow_kit_price
    kit_material = n_kits * grow_kit_cost
    kit_shipping = n_kits * shipping_cost_per_order
    kit_net = kit_gross - kit_material - kit_shipping
    
    total_rev = wet_rev + online_net + line_net + kit_net
    baseline = total_harvest * wet_market_price
    benefit = total_rev - baseline
    
    channels = [
        {'name': '🏪 Wet Market', 'kg': round(wet_kg), 'revenue': round(wet_rev), 'price_per_kg': wet_market_price},
        {'name': '🛒 Shopee/Lazada', 'kg': round(online_dried_output), 'revenue': round(online_net), 'price_per_kg': round(online_net / online_dried_output) if online_dried_output > 0 else 0},
        {'name': '📱 LINE Direct', 'kg': round(line_kg), 'revenue': round(line_net), 'price_per_kg': round(line_net / line_kg) if line_kg > 0 else 0},
        {'name': '🎁 Grow Kits', 'kg': round(kit_kg), 'revenue': round(kit_net), 'price_per_kg': round(kit_net / kit_kg) if kit_kg > 0 else 0},
    ]
    
    setup_cost = 2000  # packaging, labels, photos
    
    return {
        'total_harvest': round(total_harvest),
        'channels': channels,
        'total_revenue': round(total_rev),
        'baseline_all_wet_market': round(baseline),
        'benefit': round(benefit),
        'per_farmer': round(benefit / cooperative_size) if cooperative_size > 0 else 0,
        'setup_cost': setup_cost,
        'payback_days': round((setup_cost / (benefit / 365)) if benefit > 0 else 999),
        'blended_price_per_kg': round(total_rev / total_harvest, 1) if total_harvest > 0 else 0,
    }


# ── LAB 41: SOLAR ENERGY INTEGRATION ──
def compute_solar_energy(
    system_kw: float = 3,
    cost_per_kw: float = 35000,
    daily_sun_hours: float = 5.5,
    electricity_price: float = 4.5,
    feed_in_tariff: float = 2.70,
    self_consumption_pct: float = 70,
    tax_deduction: float = 200000,
    tax_rate: float = 10,
    panel_lifespan: int = 25,
    degradation_pct: float = 0.5,
    cooperative_size: int = 10,
) -> Dict:
    """Solar panel ROI for mushroom farm operations.
    Sources: Namsang.co.th, PRD.go.th, PVKnowHow."""
    
    total_cost = system_kw * cost_per_kw
    
    # Annual generation
    annual_kwh = system_kw * daily_sun_hours * 365 * 0.85  # 85% system efficiency
    
    # Self-consumption savings
    self_kwh = annual_kwh * (self_consumption_pct / 100)
    self_savings = self_kwh * electricity_price
    
    # Sell surplus to grid
    surplus_kwh = annual_kwh * (1 - self_consumption_pct / 100)
    surplus_income = surplus_kwh * feed_in_tariff
    
    # Tax benefit (one-time)
    tax_benefit = min(total_cost, tax_deduction) * (tax_rate / 100)
    
    annual_benefit = self_savings + surplus_income
    total_benefit_year1 = annual_benefit + tax_benefit
    
    # 25-year projection
    total_25yr_benefit = sum([
        annual_benefit * (1 - degradation_pct / 100) ** yr
        for yr in range(panel_lifespan)
    ]) + tax_benefit
    
    # Uses: fan ventilation, solar drying heater, LED grow lights, water pump
    uses = {
        'ventilation_fans': {'power_w': 200, 'hours_day': 12, 'annual_kwh': round(200 * 12 * 365 / 1000)},
        'solar_dryer_fan': {'power_w': 150, 'hours_day': 8, 'annual_kwh': round(150 * 8 * 300 / 1000)},
        'led_grow_lights': {'power_w': 100, 'hours_day': 6, 'annual_kwh': round(100 * 6 * 365 / 1000)},
        'water_pump': {'power_w': 500, 'hours_day': 2, 'annual_kwh': round(500 * 2 * 365 / 1000)},
    }
    total_farm_demand = sum(u['annual_kwh'] for u in uses.values())
    
    return {
        'system_kw': system_kw,
        'total_cost': round(total_cost),
        'annual_generation_kwh': round(annual_kwh),
        'self_consumption': {
            'kwh': round(self_kwh), 'savings': round(self_savings),
        },
        'grid_surplus': {
            'kwh': round(surplus_kwh), 'income': round(surplus_income),
        },
        'tax_benefit': round(tax_benefit),
        'annual_benefit': round(annual_benefit),
        'total_25yr_benefit': round(total_25yr_benefit),
        'payback_years': round(total_cost / annual_benefit, 1) if annual_benefit > 0 else 999,
        'farm_uses': uses,
        'farm_demand_kwh': total_farm_demand,
        'self_sufficiency_pct': round(min(100, annual_kwh / total_farm_demand * 100), 1) if total_farm_demand > 0 else 0,
        'per_farmer': round(annual_benefit / cooperative_size) if cooperative_size > 0 else 0,
    }


# ── LAB 42: BETA-GLUCAN SUPPLEMENTS ──
def compute_beta_glucan(
    annual_mushroom_kg: float = 10000,
    pct_for_extraction: float = 20,
    extraction_yield_pct: float = 8,
    beta_glucan_price_per_kg: float = 1500,
    capsule_mg: float = 500,
    capsules_per_bottle: int = 60,
    bottle_price: float = 690,
    extraction_equipment_cost: float = 250000,
    equipment_lifespan: int = 10,
    fda_registration_cost: float = 50000,
    lab_testing_annual: float = 30000,
    packaging_per_bottle: float = 25,
    labor_monthly: float = 15000,
    cooperative_size: int = 10,
    sell_mode: str = 'wholesale',
) -> Dict:
    """Beta-glucan extraction and supplement production ROI.
    Sources: QualityPlus.co.th, ResearchGate, BangkokHospital."""
    
    input_kg = annual_mushroom_kg * (pct_for_extraction / 100)
    
    # Dried mushroom first (10:1 ratio)
    dried_kg = input_kg / 10
    
    # Beta-glucan extraction (alkaline method)
    beta_glucan_kg = dried_kg * (extraction_yield_pct / 100)
    
    # Revenue depends on sell mode
    if sell_mode == 'wholesale':
        revenue = beta_glucan_kg * beta_glucan_price_per_kg
        n_bottles = 0
    else:  # retail capsules
        total_mg = beta_glucan_kg * 1_000_000
        total_capsules = total_mg / capsule_mg
        n_bottles = total_capsules / capsules_per_bottle
        revenue = n_bottles * bottle_price
    
    # Costs
    equipment_annual = extraction_equipment_cost / equipment_lifespan
    fda_annual = fda_registration_cost / 5  # renew every 5 years
    raw_material_cost = input_kg * 10  # ฿10/kg opportunity cost of mushrooms
    labor_annual = labor_monthly * 12
    packaging_total = n_bottles * packaging_per_bottle if sell_mode == 'retail' else 0
    chemicals_annual = dried_kg * 50  # solvents, NaOH, etc.
    
    total_cost = equipment_annual + fda_annual + lab_testing_annual + raw_material_cost + labor_annual + packaging_total + chemicals_annual
    
    profit = revenue - total_cost
    total_investment = extraction_equipment_cost + fda_registration_cost
    
    return {
        'input_fresh_kg': round(input_kg),
        'dried_kg': round(dried_kg),
        'beta_glucan_kg': round(beta_glucan_kg, 1),
        'sell_mode': sell_mode,
        'n_bottles': round(n_bottles),
        'revenue': round(revenue),
        'costs': {
            'equipment_annual': round(equipment_annual),
            'fda': round(fda_annual),
            'lab_testing': lab_testing_annual,
            'raw_material': round(raw_material_cost),
            'labor': round(labor_annual),
            'packaging': round(packaging_total),
            'chemicals': round(chemicals_annual),
            'total': round(total_cost),
        },
        'profit': round(profit),
        'total_investment': total_investment,
        'payback_years': round(total_investment / profit, 1) if profit > 0 else 999,
        'per_farmer': round(profit / cooperative_size) if cooperative_size > 0 else 0,
        'science': {
            'extraction_method': 'Alkaline (NaOH) extraction',
            'pleurotus_beta_glucan_pct': '23-25% of dry weight',
            'oyster_advantage': 'P. ostreatus has naturally high beta-glucan',
        },
    }


# ── LAB 43: PILOT PROGRAM ROADMAP ──
def compute_pilot_roadmap(
    cooperative_size: int = 10,
    rai_per_farmer: float = 15,
    straw_per_rai: float = 650,
    mushroom_price: float = 60,
    rice_net_income: float = 50000,
    training_quality: str = 'good',
    baac_loan_available: bool = True,
    months: int = 36,
) -> Dict:
    """Realistic month-by-month pilot program with phased optimization adoption.
    Models the actual journey from Day 0 to full operation over 36 months."""

    # ─── Phase definitions ───
    # Each phase: (start_month, name, optimizations_added, incremental_monthly_income, investment, description)
    phases = [
        {
            'month_start': 0, 'month_end': 2,
            'name': '🎓 Phase 0: Training & Setup',
            'description': 'Form cooperative, BAAC loan, buy basic equipment, 2-day training',
            'activity': 'Training, equipment procurement, polyhouse construction',
            'investment': 25000 if baac_loan_available else 40000,
            'monthly_income': 0,  # No production yet
            'cumulative_optimizations': ['Cooperative formed', 'Basic equipment'],
            'risk': 'Low — no production risk yet',
        },
        {
            'month_start': 3, 'month_end': 5,
            'name': '🍄 Phase 1: First Harvest',
            'description': 'Basic oyster mushroom cultivation in polyhouse with lime pasteurization',
            'activity': 'First 1-2 cycles, learning, wet market sales',
            'investment': 0,
            'monthly_income': 0,  # Calculated below
            'cumulative_optimizations': ['Polyhouse', 'Lime pasteurization', 'Oyster mushroom', 'Wet market'],
            'risk': 'Medium — first-time contamination risk ~15%',
        },
        {
            'month_start': 6, 'month_end': 8,
            'name': '🏗️ Phase 2: Vertical Expansion',
            'description': 'Add 4-tier shelving, increase bag count 4×',
            'activity': 'Build bamboo shelving, scale up production',
            'investment': 8000,
            'monthly_income': 0,
            'cumulative_optimizations': ['+ Vertical 4-tier racks'],
            'risk': 'Low — proven technique, low cost',
        },
        {
            'month_start': 9, 'month_end': 14,
            'name': '🌞 Phase 3: Solar Drying',
            'description': 'Solar dryer + dried product line. Start Shopee/LINE sales.',
            'activity': 'Build solar dryer, create dried mushroom brand, list online',
            'investment': 52000,
            'monthly_income': 0,
            'cumulative_optimizations': ['+ Solar dryer', '+ Dried products', '+ E-commerce (Shopee/LINE)'],
            'risk': 'Medium — requires branding/packaging skills',
        },
        {
            'month_start': 15, 'month_end': 23,
            'name': '🧫 Phase 4: Spawn Independence',
            'description': 'DIY spawn lab operational. Cost reduction kicks in.',
            'activity': 'Spawn lab setup, training, first DIY batches',
            'investment': 15000,
            'monthly_income': 0,
            'cumulative_optimizations': ['+ DIY spawn production'],
            'risk': 'Medium-High — contamination risk if sloppy',
        },
        {
            'month_start': 24, 'month_end': 35,
            'name': '☀️ Phase 5: Full Optimization',
            'description': 'Solar panels + scale. All optimizations running.',
            'activity': 'Solar installation, grow kits, full e-commerce, considering beta-glucan partnership',
            'investment': 90000,
            'monthly_income': 0,
            'cumulative_optimizations': ['+ Solar panels', '+ Grow kits', '+ Full channel mix'],
            'risk': 'Low — proven operations, scaling existing model',
        },
    ]

    # ─── Realistic income model per phase ───
    # Training quality affects learning speed and contamination
    quality_modifier = {'poor': 0.6, 'average': 0.8, 'good': 1.0, 'excellent': 1.15}
    qm = quality_modifier.get(training_quality, 1.0)

    total_straw = rai_per_farmer * straw_per_rai  # kg/farmer/year

    # Phase 1: Basic — 2 cycles, single layer, wet market, ~15% contamination
    # Realistic: ~200 bags × 2.5kg × 25% BE × 2 cycles × 0.85 success = ~213 kg/yr → ฿12,750/yr
    p1_annual = 200 * 2.5 * (0.25 * qm) * 2 * 0.85 * mushroom_price
    p1_monthly = p1_annual / 12

    # Phase 2: Vertical — 3× effective bags, better technique, ~8% contamination
    # ~600 bags × 2.5kg × 25% BE × 4 cycles × 0.92 = ~1,380 kg/yr → ฿82,800/yr
    p2_annual = 600 * 2.5 * (0.25 * qm) * 4 * 0.92 * mushroom_price
    p2_monthly = p2_annual / 12

    # Phase 3: Drying + E-commerce — blended 1.6× price, same yield
    blended_price_p3 = mushroom_price * 1.6
    p3_annual = 600 * 2.5 * (0.25 * qm) * 5 * 0.94 * blended_price_p3
    p3_monthly = p3_annual / 12

    # Phase 4: Spawn savings — same revenue + cost reduction
    spawn_savings_monthly = (2000 * 15 * 0.85) / 12  # 85% spawn cost savings
    p4_monthly = p3_monthly + spawn_savings_monthly

    # Phase 5: Full optimization — better pricing, solar savings
    blended_price_p5 = mushroom_price * 2.0
    p5_annual = 800 * 2.5 * (0.25 * qm) * 5 * 0.96 * blended_price_p5
    solar_savings_monthly = 18000 / 12
    p5_monthly = p5_annual / 12 + solar_savings_monthly + spawn_savings_monthly

    phase_incomes = [0, p1_monthly, p2_monthly, p3_monthly, p4_monthly, p5_monthly]

    # Update phases with calculated incomes
    for i, phase in enumerate(phases):
        phase['monthly_income'] = round(phase_incomes[i])

    # ─── Build month-by-month timeline ───
    timeline = []
    cumulative_investment = 0
    cumulative_income = 0

    for month in range(months):
        # Find current phase
        current_phase = phases[0]
        for phase in phases:
            if phase['month_start'] <= month <= phase['month_end']:
                current_phase = phase
                break
            elif month > phase['month_end']:
                current_phase = phase

        monthly = current_phase['monthly_income']

        # Ramp-up: first 2 months of each phase at 50% income (learning curve)
        months_in_phase = month - current_phase['month_start']
        if months_in_phase == 0:
            monthly = round(monthly * 0.3)
            cumulative_investment += current_phase['investment']
        elif months_in_phase == 1:
            monthly = round(monthly * 0.6)

        cumulative_income += monthly
        rice_monthly = rice_net_income / 12

        timeline.append({
            'month': month,
            'phase': current_phase['name'],
            'mushroom_income': monthly,
            'rice_income': round(rice_monthly),
            'total_income': round(monthly + rice_monthly),
            'cumulative_income': round(cumulative_income),
            'cumulative_investment': round(cumulative_investment),
            'net_cumulative': round(cumulative_income - cumulative_investment),
        })

    # ─── Find breakeven month ───
    breakeven_month = None
    for t in timeline:
        if t['net_cumulative'] > 0 and breakeven_month is None:
            breakeven_month = t['month']

    # ─── Summary for cooperative ───
    month_6 = timeline[5] if len(timeline) > 5 else timeline[-1]
    month_12 = timeline[11] if len(timeline) > 11 else timeline[-1]
    month_24 = timeline[23] if len(timeline) > 23 else timeline[-1]
    month_36 = timeline[35] if len(timeline) > 35 else timeline[-1]

    total_investment = sum(p['investment'] for p in phases)

    return {
        'phases': phases,
        'timeline': timeline,
        'breakeven_month': breakeven_month,
        'total_investment': total_investment,
        'milestones': {
            'month_6': month_6,
            'month_12': month_12,
            'month_24': month_24,
            'month_36': month_36,
        },
        'cooperative_size': cooperative_size,
        'training_quality': training_quality,
        'final_monthly': month_36['total_income'],
        'income_multiplier': round(month_36['total_income'] / (rice_net_income / 12), 1),
    }


# ── LAB 44: WATER & HUMIDITY MANAGEMENT ──
def compute_water_management(
    polyhouse_m2: float = 20,
    n_bags: int = 800,
    cycles_per_year: int = 5,
    target_humidity_pct: float = 85,
    misting_method: str = 'manual',
    rainwater_harvesting: bool = True,
    roof_area_m2: float = 30,
    annual_rainfall_mm: float = 1200,
    water_price_per_m3: float = 15,
    cooperative_size: int = 10,
) -> Dict:
    """Water and humidity management costs for mushroom cultivation.
    Sources: FAO water guides, Thai Met Dept rainfall data."""

    # Water needs per cycle
    substrate_soaking_L = n_bags * 2.5 * 1.5  # 1.5L per kg substrate for soaking
    daily_misting_L = polyhouse_m2 * 2  # 2L/m² daily for humidity
    days_per_cycle = 45
    misting_per_cycle_L = daily_misting_L * days_per_cycle

    total_per_cycle = substrate_soaking_L + misting_per_cycle_L
    annual_water_L = total_per_cycle * cycles_per_year
    annual_water_m3 = annual_water_L / 1000

    # Misting system costs
    methods = {
        'manual': {'equipment': 500, 'daily_labor_min': 30, 'efficiency_pct': 60, 'name': '💧 Manual spraying'},
        'drip': {'equipment': 3000, 'daily_labor_min': 5, 'efficiency_pct': 85, 'name': '💦 Drip irrigation'},
        'fogger': {'equipment': 8000, 'daily_labor_min': 2, 'efficiency_pct': 95, 'name': '🌫️ Ultrasonic fogger'},
        'auto_mist': {'equipment': 15000, 'daily_labor_min': 0, 'efficiency_pct': 98, 'name': '🤖 Auto mist + sensor'},
    }
    m = methods[misting_method]

    # Effective water use (less efficient = more water wasted)
    effective_water_m3 = annual_water_m3 / (m['efficiency_pct'] / 100)

    # Rainwater harvesting
    if rainwater_harvesting:
        collected_L = roof_area_m2 * annual_rainfall_mm * 0.8  # 80% collection efficiency
        collected_m3 = collected_L / 1000
        tank_cost = 5000  # 2000L tank
    else:
        collected_m3 = 0
        tank_cost = 0

    purchased_water_m3 = max(0, effective_water_m3 - collected_m3)
    water_cost = purchased_water_m3 * water_price_per_m3

    # Labor cost (min wage)
    labor_cost = m['daily_labor_min'] * (370 / 480) * days_per_cycle * cycles_per_year  # 370 baht / 480 min day

    total_annual = water_cost + labor_cost + m['equipment'] / 5  # 5yr depreciation
    tank_annual = tank_cost / 10 if rainwater_harvesting else 0

    # Compare all methods
    comparisons = []
    for key, method in methods.items():
        eff_water = annual_water_m3 / (method['efficiency_pct'] / 100)
        pw = max(0, eff_water - collected_m3) if rainwater_harvesting else eff_water
        wc = pw * water_price_per_m3
        lc = method['daily_labor_min'] * (370 / 480) * days_per_cycle * cycles_per_year
        tc = wc + lc + method['equipment'] / 5
        comparisons.append({
            'method': method['name'], 'key': key,
            'equipment': method['equipment'],
            'water_cost': round(wc), 'labor_cost': round(lc),
            'total_annual': round(tc),
            'efficiency': method['efficiency_pct'],
        })

    return {
        'annual_water_need_m3': round(effective_water_m3, 1),
        'rainwater_collected_m3': round(collected_m3, 1),
        'purchased_water_m3': round(purchased_water_m3, 1),
        'water_cost': round(water_cost),
        'labor_cost': round(labor_cost),
        'equipment_cost': m['equipment'],
        'total_annual': round(total_annual + tank_annual),
        'selected_method': m['name'],
        'comparisons': comparisons,
        'humidity': {
            'target_pct': target_humidity_pct,
            'below_80_risk': 'Caps dry out, yield drops 30-50%',
            'above_95_risk': 'Bacterial blotch, green mold risk',
            'optimal': '80-90% RH with air exchange 4-6 times/hr',
        },
        'per_farmer': round((total_annual + tank_annual) / cooperative_size) if cooperative_size > 0 else 0,
    }


# ── LAB 45: CLIMATE CHANGE RESILIENCE ──
def compute_climate_resilience(
    region: str = 'isaan',
    scenario: str = 'moderate',
    current_year: int = 2025,
    projection_year: int = 2040,
    polyhouse: bool = True,
) -> Dict:
    """Climate change impact on mushroom growing windows 2025-2040.
    Sources: Thai Meteorological Dept, IPCC AR6, SEA START RC."""

    regions = {
        'isaan': {'name': 'Isaan (Northeast)', 'current_avg_temp': [22, 24, 28, 30, 29, 28, 27, 27, 27, 26, 24, 22],
                  'current_growing_months': 5, 'rainy_months': [5, 6, 7, 8, 9, 10]},
        'central': {'name': 'Central Plains', 'current_avg_temp': [26, 28, 30, 31, 30, 29, 29, 28, 28, 27, 27, 26],
                    'current_growing_months': 7, 'rainy_months': [5, 6, 7, 8, 9, 10]},
        'north': {'name': 'Northern (Chiang Mai)', 'current_avg_temp': [20, 22, 26, 28, 27, 26, 26, 25, 25, 24, 22, 20],
                  'current_growing_months': 4, 'rainy_months': [5, 6, 7, 8, 9]},
        'south': {'name': 'Southern', 'current_avg_temp': [27, 27, 28, 28, 28, 28, 27, 27, 27, 27, 27, 27],
                  'current_growing_months': 10, 'rainy_months': [4, 5, 6, 7, 8, 9, 10, 11]},
    }

    scenarios = {
        'optimistic': {'name': 'SSP1-2.6 (Best case)', 'temp_rise_per_decade': 0.15, 'rainfall_change_pct': -3},
        'moderate': {'name': 'SSP2-4.5 (Middle road)', 'temp_rise_per_decade': 0.25, 'rainfall_change_pct': -5},
        'severe': {'name': 'SSP5-8.5 (Worst case)', 'temp_rise_per_decade': 0.40, 'rainfall_change_pct': -10},
    }

    reg = regions[region]
    sc = scenarios[scenario]
    decades = (projection_year - current_year) / 10

    temp_rise = sc['temp_rise_per_decade'] * decades
    polyhouse_bonus = 4 if polyhouse else 0

    # V. volvacea: 28-35°C optimal, >25°C needed
    # P. ostreatus: 20-30°C optimal, >15°C needed
    min_temp_volvacea = 25
    min_temp_ostreatus = 15

    # Project monthly temps
    current_temps = reg['current_avg_temp']
    projected_temps = [t + temp_rise for t in current_temps]
    polyhouse_temps = [t + polyhouse_bonus for t in projected_temps]

    # Count growing months
    def count_months(temps, min_t):
        return sum(1 for t in temps if t >= min_t)

    months_data = []
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i in range(12):
        months_data.append({
            'month': month_names[i],
            'current_temp': current_temps[i],
            'projected_temp': round(projected_temps[i], 1),
            'polyhouse_temp': round(polyhouse_temps[i], 1) if polyhouse else None,
            'straw_ok_current': current_temps[i] >= min_temp_volvacea,
            'straw_ok_projected': projected_temps[i] >= min_temp_volvacea,
            'oyster_ok_current': current_temps[i] >= min_temp_ostreatus,
            'oyster_ok_projected': (polyhouse_temps[i] if polyhouse else projected_temps[i]) >= min_temp_ostreatus,
            'is_rainy': (i + 1) in reg['rainy_months'],
        })

    current_straw_months = count_months(current_temps, min_temp_volvacea)
    projected_straw_months = count_months(projected_temps, min_temp_volvacea)
    current_oyster_months = count_months([t + polyhouse_bonus for t in current_temps] if polyhouse else current_temps, min_temp_ostreatus)
    projected_oyster_months = count_months(polyhouse_temps if polyhouse else projected_temps, min_temp_ostreatus)

    # Rainfall
    projected_rainfall_pct = sc['rainfall_change_pct'] * decades / 10

    # Revenue impact
    current_cycles = min(current_oyster_months, 8)  # max 8 cycles
    projected_cycles = min(projected_oyster_months, 8)
    cycle_change = projected_cycles - current_cycles

    return {
        'region': reg['name'],
        'scenario': sc['name'],
        'temp_rise': round(temp_rise, 1),
        'projection_year': projection_year,
        'months_data': months_data,
        'growing_season': {
            'straw_current': current_straw_months,
            'straw_projected': projected_straw_months,
            'oyster_current': current_oyster_months,
            'oyster_projected': projected_oyster_months,
        },
        'cycles': {
            'current': current_cycles,
            'projected': projected_cycles,
            'change': cycle_change,
        },
        'rainfall_change_pct': round(projected_rainfall_pct, 1),
        'adaptation': {
            'polyhouse': '+4°C buffer extends season by 2-3 months',
            'oyster_advantage': 'P. ostreatus tolerates 15°C vs V. volvacea 25°C — much more resilient',
            'water_storage': f'Rainfall may drop {abs(round(projected_rainfall_pct, 1))}% — rainwater harvesting essential',
            'heat_stress': 'Above 35°C reduces yield — shade cloth + misting helps',
        },
        'verdict': 'Warming HELPS mushroom growing season' if cycle_change >= 0 else 'Warming REDUCES growing season — adaptation needed',
    }


# ── LAB 46: LABOR ALLOCATION MODEL ──
def compute_labor_allocation(
    cooperative_size: int = 10,
    n_bags: int = 800,
    cycles_per_year: int = 5,
    vertical_tiers: int = 4,
    has_solar_drying: bool = True,
    has_ecommerce: bool = True,
    has_spawn_lab: bool = False,
    family_workers: int = 2,
    hired_workers: int = 0,
    daily_wage: float = 370,
) -> Dict:
    """Labor allocation model — who does what, hours per task, family vs hired.
    Sources: Thai agricultural labor studies, farmer surveys."""

    # Tasks and time per cycle (hours)
    tasks = {
        'substrate_prep': {'name': '🌾 Substrate Prep', 'hours_per_cycle': n_bags * 0.03, 'skill': 'Low', 'when': 'Start of cycle'},
        'pasteurization': {'name': '🧪 Lime Pasteurization', 'hours_per_cycle': n_bags * 0.01, 'skill': 'Low', 'when': 'Day 1-2'},
        'bagging_spawning': {'name': '📦 Bagging & Spawning', 'hours_per_cycle': n_bags * 0.05, 'skill': 'Medium', 'when': 'Day 2-3'},
        'incubation_care': {'name': '🌡️ Incubation Monitoring', 'hours_per_cycle': 30 * 0.5, 'skill': 'Low', 'when': 'Day 3-33 (30 days)'},
        'harvest': {'name': '🍄 Harvesting', 'hours_per_cycle': n_bags * 0.02 * 3, 'skill': 'Low', 'when': '3 flushes over 3 weeks'},
        'watering': {'name': '💧 Misting/Watering', 'hours_per_cycle': 30 * 0.5, 'skill': 'Low', 'when': 'Daily during fruiting'},
        'rack_maintenance': {'name': '🏗️ Rack Maintenance', 'hours_per_cycle': 4, 'skill': 'Low', 'when': 'Between cycles'},
    }

    if has_solar_drying:
        tasks['drying'] = {'name': '🌞 Solar Drying', 'hours_per_cycle': n_bags * 0.015, 'skill': 'Low', 'when': 'Post-harvest'}
        tasks['packaging'] = {'name': '📦 Packaging & Labeling', 'hours_per_cycle': n_bags * 0.01, 'skill': 'Medium', 'when': 'Post-drying'}

    if has_ecommerce:
        tasks['ecommerce'] = {'name': '📱 Online Sales', 'hours_per_cycle': 10, 'skill': 'Medium', 'when': 'Ongoing'}
        tasks['delivery'] = {'name': '🚗 Delivery/Shipping', 'hours_per_cycle': 8, 'skill': 'Low', 'when': 'Weekly'}

    if has_spawn_lab:
        tasks['spawn'] = {'name': '🧫 Spawn Production', 'hours_per_cycle': 20, 'skill': 'High', 'when': 'Continuous'}

    # Calculate totals
    total_hours_cycle = sum(t['hours_per_cycle'] for t in tasks.values())
    total_hours_year = total_hours_cycle * cycles_per_year
    total_hours_day = total_hours_year / 300  # ~300 working days

    # Available labor
    family_hours_day = family_workers * 4  # 4 hrs/day part-time (alongside rice)
    hired_hours_day = hired_workers * 8  # full-time
    available_hours_day = family_hours_day + hired_hours_day

    labor_sufficiency = available_hours_day / total_hours_day if total_hours_day > 0 else 999

    # Cost
    family_labor_cost = 0  # unpaid
    hired_labor_cost = hired_workers * daily_wage * 300
    total_labor_cost = hired_labor_cost

    # Task breakdown for output
    task_list = []
    for key, t in tasks.items():
        annual_hours = t['hours_per_cycle'] * cycles_per_year
        task_list.append({
            'name': t['name'],
            'hours_per_cycle': round(t['hours_per_cycle'], 1),
            'annual_hours': round(annual_hours),
            'pct_of_total': round(annual_hours / total_hours_year * 100, 1) if total_hours_year > 0 else 0,
            'skill': t['skill'],
            'when': t['when'],
        })

    task_list.sort(key=lambda x: x['annual_hours'], reverse=True)

    return {
        'total_hours_per_cycle': round(total_hours_cycle, 1),
        'total_hours_per_year': round(total_hours_year),
        'avg_hours_per_day': round(total_hours_day, 1),
        'tasks': task_list,
        'labor': {
            'family_workers': family_workers,
            'family_hours_day': family_hours_day,
            'hired_workers': hired_workers,
            'hired_hours_day': hired_hours_day,
            'available_hours_day': available_hours_day,
            'needed_hours_day': round(total_hours_day, 1),
            'sufficiency_pct': round(labor_sufficiency * 100, 1),
            'verdict': '✅ Sufficient' if labor_sufficiency >= 1 else f'⚠️ Need {round(total_hours_day - available_hours_day, 1)} more hrs/day',
        },
        'costs': {
            'family': 0,
            'hired': round(hired_labor_cost),
            'total': round(total_labor_cost),
            'cost_per_kg': round(total_labor_cost / (n_bags * 2.5 * 0.25 * cycles_per_year), 2) if n_bags > 0 else 0,
        },
    }


# ── LAB 47: HUB-AT-MILL COMPARISON ──
def compute_hub_at_mill(
    tier: str = 'balanced',
    n_farmers: int = 30,
    rai_per_farmer: float = 15,
    straw_per_rai: float = 650,
    straw_buy_price: float = 3,
    mushroom_price: float = 60,
    dried_price: float = 400,
    pct_dried: float = 30,
    pct_powder: float = 10,
    cycles_per_year: int = 5,
    hired_workers: int = 1,
    daily_wage: float = 370,
) -> Dict:
    """Hub-at-Mill 3-tier comparison: Lean MVP, Balanced, Full Build.
    Models centralized mushroom production at rice mill."""

    tiers = {
        'lean': {
            'name': '🌱 Lean MVP', 'investment': 50500,
            'bags_per_cycle': 500, 'be_pct': 22, 'contamination_pct': 12,
            'blended_multiplier': 1.3, 'hired': 0, 'family_workers': 2,
            'has_dryer': True, 'has_spawn_lab': False, 'has_solar': False,
            'polyhouse': 'Mill shed + plastic', 'shelving': 'Bamboo DIY',
            'dryer': 'DIY bamboo+plastic', 'misting': 'Manual spray',
        },
        'balanced': {
            'name': '⚖️ Balanced', 'investment': 250000,
            'bags_per_cycle': 2000, 'be_pct': 25, 'contamination_pct': 8,
            'blended_multiplier': 1.6, 'hired': 1, 'family_workers': 1,
            'has_dryer': True, 'has_spawn_lab': False, 'has_solar': False,
            'polyhouse': 'Bamboo frame 80m²', 'shelving': 'Bamboo+steel hybrid',
            'dryer': 'Semi-pro metal+fan', 'misting': 'Drip irrigation',
        },
        'full': {
            'name': '🏭 Full Build', 'investment': 751600,
            'bags_per_cycle': 5000, 'be_pct': 25, 'contamination_pct': 5,
            'blended_multiplier': 2.0, 'hired': 2, 'family_workers': 0,
            'has_dryer': True, 'has_spawn_lab': True, 'has_solar': True,
            'polyhouse': 'Steel 200m²', 'shelving': 'Full metal 6-tier',
            'dryer': 'Commercial 100kg/day', 'misting': 'Auto-mist + sensors',
        },
    }

    t = tiers[tier]
    total_straw = n_farmers * rai_per_farmer * straw_per_rai

    # Production
    bags_year = t['bags_per_cycle'] * cycles_per_year
    substrate_kg = bags_year * 2.5
    mushroom_kg = substrate_kg * (t['be_pct'] / 100) * (1 - t['contamination_pct'] / 100)

    # Revenue split — use blended multiplier for fresh (market mix premium)
    fresh_pct = (100 - pct_dried - pct_powder) / 100
    fresh_kg = mushroom_kg * fresh_pct
    dried_kg = mushroom_kg * (pct_dried / 100) / 10  # 10:1 drying ratio
    powder_kg = mushroom_kg * (pct_powder / 100) / 10

    blended_fresh_price = mushroom_price * t['blended_multiplier']
    rev_fresh = fresh_kg * blended_fresh_price
    rev_dried = dried_kg * dried_price
    rev_powder = powder_kg * 600
    total_revenue = rev_fresh + rev_dried + rev_powder

    # Costs — hub gets bulk discounts
    straw_needed_kg = substrate_kg * 0.7  # straw is ~70% of substrate (rest is water, lime)
    straw_cost = straw_needed_kg * straw_buy_price
    spawn_per_bag = 3 if t['has_spawn_lab'] else 8  # bulk discount at hub scale vs ฿15 retail
    spawn_cost = bags_year * spawn_per_bag
    labor_cost = t['hired'] * daily_wage * 300
    supplies_cost = bags_year * 1.5  # bags, rubber bands
    electricity = 0 if t['has_solar'] else bags_year * 0.3
    total_costs = straw_cost + spawn_cost + labor_cost + supplies_cost + electricity

    profit = total_revenue - total_costs
    roi = profit / t['investment'] if t['investment'] > 0 else 0
    breakeven_months = round(t['investment'] / (profit / 12)) if profit > 0 else 999

    # Farmer income (straw payment)
    straw_used = min(substrate_kg, total_straw)
    farmer_straw_income = (straw_used * straw_buy_price) / n_farmers

    # Compare all tiers
    all_tiers = []
    for key, ti in tiers.items():
        by = ti['bags_per_cycle'] * cycles_per_year
        sk = by * 2.5
        mk = sk * (ti['be_pct'] / 100) * (1 - ti['contamination_pct'] / 100)
        fk = mk * 0.6; dk = mk * 0.3 / 10; pk = mk * 0.1 / 10
        bfp = mushroom_price * ti['blended_multiplier']
        rev = fk * bfp + dk * dried_price + pk * 600
        sc = sk * 0.7 * straw_buy_price
        spc = by * (3 if ti['has_spawn_lab'] else 8)
        lc = ti['hired'] * daily_wage * 300
        sup = by * 1.5; el = 0 if ti['has_solar'] else by * 0.3
        tc = sc + spc + lc + sup + el
        pr = rev - tc
        all_tiers.append({
            'key': key, 'name': ti['name'],
            'investment': ti['investment'],
            'revenue': round(rev), 'costs': round(tc),
            'profit': round(pr),
            'roi': round(pr / ti['investment'], 1) if ti['investment'] > 0 else 0,
            'breakeven': round(ti['investment'] / (pr / 12)) if pr > 0 else 999,
            'bags_year': by, 'mushroom_kg': round(mk),
        })

    return {
        'tier': t,
        'production': {
            'bags_year': bags_year, 'mushroom_kg': round(mushroom_kg),
            'fresh_kg': round(fresh_kg), 'dried_kg': round(dried_kg), 'powder_kg': round(powder_kg),
        },
        'revenue': {
            'fresh': round(rev_fresh), 'dried': round(rev_dried), 'powder': round(rev_powder),
            'total': round(total_revenue),
        },
        'costs': {
            'straw': round(straw_cost), 'spawn': round(spawn_cost),
            'labor': round(labor_cost), 'supplies': round(supplies_cost),
            'electricity': round(electricity), 'total': round(total_costs),
        },
        'profit': round(profit),
        'roi': round(roi, 1),
        'breakeven_months': breakeven_months,
        'farmer_straw_income': round(farmer_straw_income),
        'all_tiers': all_tiers,
        'n_farmers': n_farmers,
    }
