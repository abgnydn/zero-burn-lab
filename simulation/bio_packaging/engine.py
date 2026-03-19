"""Bio-Packaging Hub Engine — Standalone."""
import math
from typing import Dict

def compute_bio_packaging_hub(
    total_rai: float = 30,
    straw_per_rai: float = 650,
    straw_buy_price: float = 0,  # ฿0 = farmer's own waste
    second_crop: bool = True,  # 2nd rice season = +70% straw
    # Equipment tier
    tier: str = 'starter',
    # Product mix (pct of output)
    pct_plates: float = 40,
    pct_bowls: float = 30,
    pct_trays: float = 20,
    pct_containers: float = 10,
    auto_mix: bool = False,  # auto-optimize mix for max revenue
    # Operations
    daily_wage: float = 370,
    days_per_year: int = 300,
    work_hours_per_day: float = 4,
    yield_boost: float = 0,  # 0-15% extra yield from longer soaking
    bulk_contract: bool = False,  # +50% pricing from hotel/chain contracts
    transport_km: float = 0,  # delivery distance (฿3/km)
    # ─── Cost optimizers ───
    opt_family_labor: bool = False,
    opt_solar_drying: bool = False,
    opt_biomass_fuel: bool = False,
    opt_automation: bool = False,
    opt_batch_schedule: bool = False,
    # ─── Revenue boosters (toggleable) ───
    opt_branding: bool = False,
    opt_export: bool = False,
    opt_certification: bool = False,
    opt_delivery: bool = False,
    # ─── Profit extras (small investment) ───
    opt_custom_molds: bool = False,
    opt_seed_trays: bool = False,
    opt_egg_cartons: bool = False,
    opt_coconut_blend: bool = False,
    opt_sell_training: bool = False,
    # ─── Process & coverage ───
    process_method: str = 'pulp',  # 'pulp', 'lime', 'direct'
    service_radius_km: float = 15,
    # ─── Platform owner ───
    financing_model: str = 'revenue_share',  # 'revenue_share', 'kit_sale', 'installment'
    revenue_share_pct: float = 35,  # platform owner's cut
    n_hubs: int = 1,
) -> Dict:
    """Bio-Packaging Center: comprehensive feasibility calculator."""

    tiers = {
        'micro': {
            'name': '🔧 Micro Hub', 'investment': 50000,
            'capacity_kg_day': 80, 'workers': 1,
            'yield_pct': 65, 'energy_per_kg': 1.0,
            'equipment': 'Cement mixer + car jack press + concrete molds + fan dryer',
            'hrs_per_day': 4, 'pieces_per_day': 200,
        },
        'starter': {
            'name': '🌱 Starter', 'investment': 140000,
            'capacity_kg_day': 200, 'workers': 2,
            'yield_pct': 72, 'energy_per_kg': 2,
            'equipment': 'Hydraulic press + manual pulper + solar dryer + 4 molds',
            'hrs_per_day': 5, 'pieces_per_day': 500,
        },
        'mid': {
            'name': '⚖️ Mid-Scale', 'investment': 500000,
            'capacity_kg_day': 500, 'workers': 4,
            'yield_pct': 78, 'energy_per_kg': 1.5,
            'equipment': 'Semi-auto pulper + 4-mold press + gas dryer + hot press',
            'hrs_per_day': 6, 'pieces_per_day': 1500,
        },
        'industrial': {
            'name': '🏭 Industrial', 'investment': 1500000,
            'capacity_kg_day': 2000, 'workers': 8,
            'yield_pct': 85, 'energy_per_kg': 1.0,
            'equipment': 'Full auto line + multi-mold + tunnel dryer + finishing',
            'hrs_per_day': 8, 'pieces_per_day': 5000,
        },
    }
    t = tiers[tier]

    # ─── Farm capacity vs Hub capacity ───
    import math
    straw_multiplier = 1.7 if second_crop else 1.0  # 2nd crop adds 70%
    total_straw = total_rai * straw_per_rai * straw_multiplier
    straw_cost_per_kg = straw_buy_price

    # Coverage area calculations (for Coverage tab)
    area_km2 = math.pi * service_radius_km ** 2
    area_rai = area_km2 * 625  # 1 km² = 625 rai
    farmland_rai = area_rai * 0.55  # ~55% rice fields
    n_farmers = max(1, round(total_rai / 15))  # estimated farmer count for display

    # ─── Production (scaled by work hours) ───
    base_hrs = t['hrs_per_day']
    hour_scale = work_hours_per_day / base_hrs
    effective_capacity = t['capacity_kg_day'] * hour_scale
    max_straw_per_year = effective_capacity * days_per_year
    straw_used = min(max_straw_per_year, total_straw)
    utilization = straw_used / max_straw_per_year if max_straw_per_year > 0 else 0

    # Pulp yield: straw → usable pulp (with optional yield boost)
    effective_yield = t['yield_pct'] + yield_boost  # yield_boost = 0-15%
    pulp_kg = straw_used * (effective_yield / 100)
    # Finished product (some loss in molding/trimming)
    finished_kg = pulp_kg * 0.9

    # ─── Product mix & pricing ───
    price_mult = 1.50 if bulk_contract else 1.0  # bulk = +50% pricing
    products = {
        'plates': {
            'pct': pct_plates / 100, 'price_per_kg': 18 * price_mult,
            'pieces_per_kg': 25, 'price_per_piece': 0.72 * price_mult,
            'emoji': '🍽️', 'name_th': 'จาน', 'name_en': 'Plates',
        },
        'bowls': {
            'pct': pct_bowls / 100, 'price_per_kg': 22 * price_mult,
            'pieces_per_kg': 20, 'price_per_piece': 1.10 * price_mult,
            'emoji': '🥣', 'name_th': 'ถ้วย', 'name_en': 'Bowls',
        },
        'trays': {
            'pct': pct_trays / 100, 'price_per_kg': 15 * price_mult,
            'pieces_per_kg': 10, 'price_per_piece': 1.50 * price_mult,
            'emoji': '📦', 'name_th': 'ถาด', 'name_en': 'Trays',
        },
        'containers': {
            'pct': pct_containers / 100, 'price_per_kg': 25 * price_mult,
            'pieces_per_kg': 15, 'price_per_piece': 1.67 * price_mult,
            'emoji': '🥡', 'name_th': 'กล่อง', 'name_en': 'Containers',
        },
    }
    # Auto-optimize mix: maximize revenue by favoring highest price/kg
    if auto_mix:
        # Sort by price_per_kg descending, allocate: 50% best, 25% 2nd, 15% 3rd, 10% 4th
        sorted_keys = sorted(products.keys(), key=lambda k: products[k]['price_per_kg'], reverse=True)
        auto_pcts = [50, 25, 15, 10]
        for i, k in enumerate(sorted_keys):
            products[k]['pct'] = auto_pcts[i] / 100

    total_revenue = 0
    product_details = []
    for key, p in products.items():
        kg = finished_kg * p['pct']
        pieces = kg * p['pieces_per_kg']
        rev = kg * p['price_per_kg']
        total_revenue += rev
        product_details.append({
            'key': key, 'emoji': p['emoji'],
            'name_en': p['name_en'], 'name_th': p['name_th'],
            'kg': round(kg), 'pieces': round(pieces),
            'revenue': round(rev), 'price_per_piece': p['price_per_piece'],
        })

    # ─── Costs (with optimizers) ───
    raw_material_cost = straw_used * straw_cost_per_kg

    # Labor
    workers_needed = t['workers']
    if opt_automation and workers_needed > 1:
        workers_needed -= 1  # automation replaces 1 worker
    if opt_family_labor:
        labor_cost = 0  # family runs it, no hired wages
    else:
        labor_cost = workers_needed * daily_wage * days_per_year

    # Energy — savings applied multiplicatively (compound, not additive)
    base_energy = straw_used * t['energy_per_kg']
    remaining_energy = base_energy
    if opt_solar_drying:
        remaining_energy *= 0.40  # sun replaces 60% of energy
    if opt_biomass_fuel:
        remaining_energy *= 0.70  # burn waste saves 30% of what's left
    if opt_batch_schedule:
        remaining_energy *= 0.85  # batch scheduling saves 15% of what's left
    energy_savings = base_energy - remaining_energy
    energy_cost = remaining_energy

    # FIX: Chemical cost depends on process method (was applying AFTER total_costs)
    if process_method == 'lime':
        chemicals_cost = pulp_kg * 0.06  # lime ฿5/kg ÷ 80 uses = ฿0.06/kg
    elif process_method == 'direct':
        chemicals_cost = finished_kg * 1.5  # tapioca starch only
    else:
        chemicals_cost = pulp_kg * 0.5  # NaOH + starch + sizing

    extra_invest = 0
    if opt_solar_drying:
        extra_invest += 30000
    if opt_automation:
        extra_invest += 50000
    maintenance_cost = (t['investment'] + extra_invest) * 0.05
    packaging_cost = finished_kg * 0.3
    transport_cost = transport_km * 3 * days_per_year  # ฿3/km/day
    total_costs = (raw_material_cost + labor_cost + energy_cost +
                   chemicals_cost + maintenance_cost + packaging_cost + transport_cost)

    # Track savings for display
    base_labor = t['workers'] * daily_wage * days_per_year
    labor_saved = base_labor - labor_cost
    energy_saved = energy_savings
    total_saved = labor_saved + energy_saved




    # ─── Revenue boosters (user-toggled) ───
    base_revenue = total_revenue
    revenue_boosts = []
    if opt_branding:
        boost = total_revenue * 0.40
        total_revenue += boost
        extra_invest += 25000
        revenue_boosts.append({'name': '🏷️ Brand Printing', 'boost': round(boost), 'invest': 25000,
            'desc': 'Print logos/designs on products. Restaurants pay 40% more for branded packaging.'})
    if opt_export:
        boost = base_revenue * 0.20 * 2
        total_revenue += boost
        revenue_boosts.append({'name': '🇯🇵 Export Market', 'boost': round(boost), 'invest': 0,
            'desc': 'Sell 20% of output to Japan/EU at 3× price via export aggregator.'})
    if opt_certification:
        boost = base_revenue * 0.25
        total_revenue += boost
        extra_invest += 15000
        revenue_boosts.append({'name': '📜 Compostable Cert', 'boost': round(boost), 'invest': 15000,
            'desc': 'OK Compost / TIS certification. Hotels & chains require it — unlocks premium contracts.'})
    if opt_delivery:
        boost = base_revenue * 0.30
        total_revenue += boost
        revenue_boosts.append({'name': '🛵 Delivery Partner', 'boost': round(boost), 'invest': 0,
            'desc': 'Partner with Grab/LINE MAN/Robinhood. They supply you restaurants, you supply them packaging.'})

    # ─── Small-investment profit extras (user-toggled) ───
    if opt_custom_molds:
        boost = base_revenue * 0.15  # premium shapes = 15% more
        total_revenue += boost
        extra_invest += 3000
        revenue_boosts.append({'name': '🎨 Custom Mold Shapes', 'boost': round(boost), 'invest': 3000,
            'desc': 'Lotus/leaf/heart shapes. One ฿3K mold = premium 2× pricing for hotels & events. Weld rebar into shape, cast in concrete.'})
    if opt_seed_trays:
        seed_kg = finished_kg * 0.10
        boost = seed_kg * 35  # ฿35/kg
        total_revenue += boost
        extra_invest += 2000
        revenue_boosts.append({'name': '🌱 Seed Starter Trays', 'boost': round(boost), 'invest': 2000,
            'desc': 'Biodegradable seedling pots for nurseries. ฿2K mold investment. Higher margin than plates (฿35/kg vs ฿18/kg). Plant shops love them.'})
        product_details.append({
            'key': 'seed_trays', 'emoji': '🌱', 'name_en': 'Seed Trays', 'name_th': 'ถาดเพาะพันธุ์',
            'kg': round(seed_kg), 'pieces': round(seed_kg * 8), 'revenue': round(boost),
            'price_per_piece': round(35 / 8, 2),
        })
    if opt_egg_cartons:
        egg_kg = finished_kg * 0.10
        boost = egg_kg * 40  # ฿40/kg — highest margin
        total_revenue += boost
        extra_invest += 5000
        revenue_boosts.append({'name': '🥚 Egg Cartons', 'boost': round(boost), 'invest': 5000,
            'desc': 'Every market & farm needs egg cartons. ฿5K mold, highest margin (฿40/kg). Sell to local poultry farms & wet markets.'})
        product_details.append({
            'key': 'egg_cartons', 'emoji': '🥚', 'name_en': 'Egg Cartons', 'name_th': 'กล่องไข่',
            'kg': round(egg_kg), 'pieces': round(egg_kg * 6), 'revenue': round(boost),
            'price_per_piece': round(40 / 6, 2),
        })
    if opt_coconut_blend:
        boost = base_revenue * 0.08  # stronger product = 8% premium
        total_revenue += boost
        revenue_boosts.append({'name': '🥥 Coconut Husk Blend', 'boost': round(boost), 'invest': 0,
            'desc': 'Mix 20% coconut husk fiber (free waste) into pulp. Stronger, unique texture. Premium for restaurants wanting \"artisan\" look.'})
    if opt_sell_training:
        boost = 50000  # 10 farmers × ฿5K/training
        total_revenue += boost
        revenue_boosts.append({'name': '📚 Sell Training', 'boost': round(boost), 'invest': 0,
            'desc': 'Train 10 farmers/yr at ฿5K each. Your knowledge is a product. 2-day workshop covers process, equipment, marketing.'})

    # ─── Zero-cost boosters (ALWAYS active — standard plan) ───
    zero_cost_boosts = []
    # 1. Compost from waste
    compost_boost = finished_kg * 0.15 * 10  # 15% waste × ฿10/kg compost
    total_revenue += compost_boost
    zero_cost_boosts.append({'name': '♻️ Compost from Waste', 'boost': round(compost_boost), 'invest': 0,
        'desc': 'Trimming scraps + wash sludge → dry & bag as organic compost. Sell to nurseries at ฿10/kg.'})
    # 2. Off-cut recycling (saves straw volume, not cost)
    offcut_straw_saved = straw_used * 0.10  # 10% straw recovered
    offcut_value = offcut_straw_saved * 1.5  # ฿1.5/kg value of straw (replacement cost)
    total_costs -= offcut_value
    zero_cost_boosts.append({'name': '♻️ Off-Cut Recycling', 'boost': round(offcut_value), 'invest': 0,
        'desc': f'Recover {offcut_straw_saved:,.0f} kg straw from trimming waste. Worth ฿{offcut_value:,.0f}/yr in saved material.'})
    # 3. Festival premium
    festival_boost = base_revenue * 0.05
    total_revenue += festival_boost
    zero_cost_boosts.append({'name': '🎎 Festival Pricing', 'boost': round(festival_boost), 'invest': 0,
        'desc': 'Charge 2× during Songkran, Loy Krathong, New Year. +5% annual revenue.'})
    # 4. Excess straw sales
    excess_straw = max(0, total_straw - straw_used)
    straw_sale_boost = excess_straw * 2
    if straw_sale_boost > 0:
        total_revenue += straw_sale_boost
        zero_cost_boosts.append({'name': '🌾 Excess Straw Sales', 'boost': round(straw_sale_boost), 'invest': 0,
            'desc': f'Sell {excess_straw:,.0f} kg unused straw as mulch/feed at ฿2/kg.'})
    # 5. Government anti-burning subsidy
    subsidy = total_rai * 200  # ฿200/rai for not burning
    total_revenue += subsidy
    zero_cost_boosts.append({'name': '🏛️ Anti-Burn Subsidy', 'boost': round(subsidy), 'invest': 0,
        'desc': f'Government pays ฿200/rai for not burning straw. {total_rai} rai × ฿200 = ฿{subsidy:,.0f}/yr.'})

    # ─── Realism adjustments ───
    qc_reject_rate = 0.05  # 5% pieces fail QC
    finished_after_qc = finished_kg * (1 - qc_reject_rate)
    qc_loss = finished_kg * qc_reject_rate
    # QC rejects go back to mixer (like off-cuts)
    water_cost = straw_used * 0.05  # ฿0.05/kg for soaking water
    depreciation = (t['investment'] + extra_invest) / 7  # 7-year equipment life
    total_costs += water_cost + depreciation
    # Adjust revenue for QC (fewer sellable pieces)
    total_revenue *= (1 - qc_reject_rate)

    profit = total_revenue - total_costs
    total_invest = t['investment'] + extra_invest
    roi = profit / total_invest if total_invest > 0 else 0
    breakeven_months = round(total_invest / (profit / 12)) if profit > 0 else 999

    # ─── Seasonal Calendar (scaled to days_per_year) ───
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    farm_busy =    [0.2, 0.1, 0.1, 0.1, 0.3, 0.9, 0.9, 0.7, 0.5, 0.2, 0.8, 0.9]
    straw_avail =  [1.0, 1.0, 0.7, 0.5, 0.4, 0.0, 0.0, 0.3, 0.8, 1.0, 1.0, 1.0]
    solar_good =   [0.8, 0.9, 1.0, 1.0, 0.9, 0.4, 0.3, 0.4, 0.4, 0.7, 0.8, 0.8]

    pieces_per_kg_avg = sum(p['pieces_per_kg'] for p in products.values()) / 4
    annual_pieces = round(finished_after_qc * pieces_per_kg_avg)

    # Compute raw weights for each month, then normalize
    raw_weights = []
    for i in range(12):
        pack_avail = 1.0 - farm_busy[i]
        raw_weights.append(pack_avail * straw_avail[i])
    total_weight = sum(raw_weights) or 1

    seasonal = []
    total_work_days = 0
    total_work_hrs = 0
    total_pieces_yr = 0
    avg_days_per_mo = days_per_year / 12
    for i, mo in enumerate(months):
        # Proportional days based on weight
        fraction = raw_weights[i] / total_weight
        days_this_mo = round(days_per_year * fraction)
        hrs_this_mo = round(days_this_mo * work_hours_per_day)
        pieces = round(annual_pieces * fraction)
        revenue_mo = round(total_revenue * fraction)
        total_work_days += days_this_mo
        total_work_hrs += hrs_this_mo
        total_pieces_yr += pieces
        seasonal.append({
            'month': mo, 'farm_busy': farm_busy[i],
            'pack_days': days_this_mo, 'work_hrs': hrs_this_mo,
            'pieces': pieces, 'straw': straw_avail[i], 'solar': solar_good[i],
            'revenue': revenue_mo,
        })

    # ─── Coverage & Demand ───
    straw_in_radius = farmland_rai * straw_per_rai
    hub_needs = straw_used
    coverage_pct = (hub_needs / straw_in_radius * 100) if straw_in_radius > 0 else 0
    restaurants_in_radius = round(area_km2 * 0.5)
    demand_pieces_mo = restaurants_in_radius * 2000
    actual_supply_pcs_mo = round(finished_after_qc * pieces_per_kg_avg / 12)
    demand_met_pct = min(100, round(actual_supply_pcs_mo / max(demand_pieces_mo, 1) * 100))

    # ─── Work Hours Summary ───
    actual_total_hrs = days_per_year * work_hours_per_day
    baht_per_hr = round(profit / max(actual_total_hrs, 1)) if profit > 0 else 0

    # ─── Health Impact ───
    straw_diverted_tons = straw_used / 1000
    co2_prevented = straw_diverted_tons * 1.5
    pm25_prevented = straw_diverted_tons * 0.013
    people_health_benefit = round(straw_diverted_tons * 5)
    healthcare_savings = straw_diverted_tons * 15000
    carbon_credit_value = co2_prevented * 1000

    # ─── Farmer Income (deduct platform share) ───
    rice_income = total_rai * 3333
    # Farmer's packaging profit = total profit minus platform owner's cut
    if financing_model == 'revenue_share':
        platform_cut = profit * (revenue_share_pct / 100)
    elif financing_model == 'installment_distro':
        # Year 1: farmer pays back equipment (10 months) + distro margin (2 months)
        monthly_payment = total_invest / 10
        payback = monthly_payment * 10  # full equipment cost
        distro_margin_yr1 = total_revenue * 0.15 * (2 / 12)  # 15% margin, 2 months
        platform_cut = payback + distro_margin_yr1
    else:
        platform_cut = 0
    farmer_packaging = profit - platform_cut
    farmer_total = rice_income + farmer_packaging
    farmer_monthly = farmer_total / 12
    farmer_income = {
        'mode': 'owner',
        'rice_income': round(rice_income),
        'packaging_profit': round(farmer_packaging),
        'platform_cut': round(platform_cut),
        'total': round(farmer_total),
        'monthly': round(farmer_monthly),
        'total_rai': total_rai,
        'straw_from_farm': round(total_straw),
        'hub_needs': round(straw_used),
        'farm_utilization': round(straw_used / max(total_straw, 1) * 100),
        'qc_reject_pct': round(qc_reject_rate * 100),
    }

    # ─── Compare all tiers (WITH same optimizers applied) ───
    # Use weighted average price from actual product mix
    avg_price_per_kg = total_revenue / max(finished_after_qc, 1) if finished_after_qc > 0 else 18
    all_tiers = []
    for key, ti in tiers.items():
        ti_hrs = ti['hrs_per_day']
        ti_hour_scale = work_hours_per_day / ti_hrs
        cap = ti['capacity_kg_day'] * ti_hour_scale * days_per_year
        su = min(cap, total_straw)
        ey = ti['yield_pct'] + yield_boost
        pk = su * (ey / 100) * 0.9 * (1 - qc_reject_rate)
        rev = pk * avg_price_per_kg  # use actual weighted price, not flat ฿18
        # Apply same optimizer savings
        t_labor = 0 if opt_family_labor else ti['workers'] * daily_wage * days_per_year
        t_energy = su * ti['energy_per_kg'] * 0.15  # 85% savings
        t_chem = pk * 0.06 if process_method == 'lime' else pk * 0.5
        t_maint = ti['investment'] * 0.05
        t_pkg = pk * 0.3
        t_water = su * 0.05
        t_depr = ti['investment'] / 7
        tc = t_labor + t_energy + t_chem + t_maint + t_pkg + t_water + t_depr
        pr = rev - tc
        all_tiers.append({
            'key': key, 'name': ti['name'],
            'investment': ti['investment'],
            'capacity': f"{round(ti['capacity_kg_day'] * ti_hour_scale)} kg/day",
            'revenue': round(rev), 'costs': round(tc),
            'profit': round(pr),
            'roi': round(pr / ti['investment'], 1) if ti['investment'] > 0 else 0,
            'workers': ti['workers'],
        })

    return {
        'tier': t, 'investment': total_invest,
        'base_investment': t['investment'], 'extra_investment': extra_invest,
        'production': {
            'straw_used': round(straw_used),
            'pulp_kg': round(pulp_kg),
            'finished_kg': round(finished_kg),
            'finished_after_qc': round(finished_after_qc),
            'qc_reject_pct': round(qc_reject_rate * 100),
            'utilization': round(utilization * 100),
            'effective_capacity_day': round(effective_capacity),
        },
        'products': product_details,
        'revenue': round(total_revenue),
        'costs': {
            'straw': round(raw_material_cost),
            'labor': round(labor_cost),
            'energy': round(energy_cost),
            'chemicals': round(chemicals_cost),
            'maintenance': round(maintenance_cost),
            'packaging': round(packaging_cost),
            'water': round(water_cost),
            'depreciation': round(depreciation),
            'transport': round(transport_cost),
            'total': round(total_costs),
        },
        'savings': {
            'labor': round(labor_saved),
            'energy': round(energy_saved),
            'total': round(total_saved),
            'base_labor': round(base_labor),
            'base_energy': round(base_energy) if 'base_energy' in dir() else round(straw_used * t['energy_per_kg']),
        },
        'profit': round(profit),
        'roi': round(roi, 1),
        'breakeven_months': breakeven_months,
        'health': {
            'straw_diverted_tons': round(straw_diverted_tons, 1),
            'co2_prevented': round(co2_prevented, 1),
            'pm25_prevented_kg': round(pm25_prevented * 1000, 1),
            'people_benefit': people_health_benefit,
            'healthcare_savings': round(healthcare_savings),
            'carbon_credit': round(carbon_credit_value),
        },
        'farmer_income': farmer_income,
        'all_tiers': all_tiers,
        'n_farmers': n_farmers,
        'total_straw_available': round(total_straw),
        'revenue_boosts': revenue_boosts,
        'zero_cost_boosts': zero_cost_boosts,
        'process_method': process_method,
        'seasonal': seasonal,
        'work_hours': {
            'total_days': days_per_year,
            'total_hrs': actual_total_hrs,
            'total_pieces': total_pieces_yr,
            'hrs_per_day': work_hours_per_day,
            'baht_per_hr': baht_per_hr,
        },
        'coverage': {
            'radius_km': service_radius_km,
            'area_km2': round(area_km2),
            'farmland_rai': round(farmland_rai),
            'straw_in_radius': round(straw_in_radius),
            'hub_needs': round(hub_needs),
            'coverage_pct': round(coverage_pct, 2),
            'restaurants': restaurants_in_radius,
            'demand_pieces_mo': round(demand_pieces_mo),
            'supply_pieces_mo': actual_supply_pcs_mo,
            'demand_met_pct': demand_met_pct,
            'max_farmers': n_farmers,
        },
        'platform': _calc_platform_income(
            financing_model, revenue_share_pct, n_hubs,
            total_revenue, profit, total_invest,
        ),
    }


def _calc_platform_income(model, share_pct, n_hubs, hub_revenue, hub_profit, hub_invest):
    """Calculate platform owner's income from multiple hubs.

    Models:
    - revenue_share: You invest in equipment, take ongoing % of profit
    - installment_distro: Farmer pays back equipment in 10 months,
      then you earn ongoing income as distributor (buy wholesale, sell retail)
    """
    kit_cost = hub_invest
    distro_margin = 0.15  # 15% distribution margin on revenue

    if model == 'revenue_share':
        owner_per_hub = hub_profit * (share_pct / 100)
        farmer_per_hub = hub_profit - owner_per_hub
        owner_invest_per_hub = kit_cost
        owner_description = f"You provide equipment, take {share_pct:.0f}% of profit each year"
    else:  # installment_distro
        monthly_payment = kit_cost / 10
        # Year 1: payback + distribution income (starts month 11)
        payback_income = monthly_payment * 10  # = full kit cost recovered
        distro_income_yr1 = hub_revenue * distro_margin * (2 / 12)  # only 2 months of distro in yr 1
        owner_per_hub = payback_income + distro_income_yr1
        # Farmer: profit minus payments (10 months) minus distro margin (2 months)
        farmer_per_hub = hub_profit - payback_income - distro_income_yr1
        owner_invest_per_hub = kit_cost
        owner_description = (f"Farmer pays ฿{monthly_payment:,.0f}/mo × 10 months → "
                           f"then you distribute at {distro_margin*100:.0f}% margin forever")

    total_owner_invest = owner_invest_per_hub * n_hubs
    total_owner_income = owner_per_hub * n_hubs
    total_farmer_income = max(0, farmer_per_hub) * n_hubs
    owner_roi = total_owner_income / max(total_owner_invest, 1)
    owner_payback = round(total_owner_invest / max(total_owner_income / 12, 1)) if total_owner_income > 0 else 999

    # 5-year projection with 10% annual price growth
    projection = []
    cumulative = -total_owner_invest
    for yr in range(1, 6):
        price_growth = 1.10 ** (yr - 1)
        if model == 'installment_distro':
            if yr == 1:
                yr_income = total_owner_income  # payback + partial distro
            else:
                # Year 2+: full year distribution income only
                yr_income = round(hub_revenue * distro_margin * n_hubs * price_growth)
        else:
            yr_income = round(total_owner_income * price_growth)
        cumulative += yr_income
        projection.append({
            'year': yr, 'income': round(yr_income),
            'cumulative': round(cumulative),
            'hubs': n_hubs,
        })

    # Steady-state Year 2+ values (for installment_distro)
    if model == 'installment_distro':
        distro_income_full_yr = hub_revenue * distro_margin  # annual distro income
        farmer_yr2 = hub_profit - distro_income_full_yr  # farmer keeps everything minus distro margin
    else:
        distro_income_full_yr = 0
        farmer_yr2 = farmer_per_hub

    return {
        'model': model,
        'is_one_time': False,
        'description': owner_description,
        'n_hubs': n_hubs,
        'per_hub': {
            'owner_income': round(owner_per_hub),  # Year 1 total
            'farmer_income': round(max(0, farmer_per_hub)),  # Year 1 total
            'owner_invest': round(owner_invest_per_hub),
            'distro_income_yr': round(distro_income_full_yr),  # Year 2+ annual
            'farmer_income_yr2': round(max(0, farmer_yr2)),  # Year 2+ annual
        },
        'total': {
            'invest': round(total_owner_invest),
            'income': round(total_owner_income),
            'farmer_total': round(total_farmer_income),
            'roi': round(owner_roi, 1),
            'payback_months': owner_payback,
            'distro_income_yr': round(distro_income_full_yr * n_hubs),
            'farmer_total_yr2': round(max(0, farmer_yr2) * n_hubs),
        },
        'projection': projection,
    }

