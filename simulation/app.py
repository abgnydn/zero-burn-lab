"""
Zero-Burn Blueprint — Scientific Simulation Workbench
Run with: source .venv/bin/activate && streamlit run simulation/app.py
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from engines import (
    compute_steam_energy, compute_fuel_requirement, compute_temperature_profile,
    compute_heat_transfer_adequacy, optimize_coil_length, compute_scale_profile,
    compute_mushroom_yield, compute_contamination_risk,
    compute_economics, compute_sensitivity_matrix, monte_carlo_profit,
    compute_carbon_credits, compute_regional_impact, optimize_system,
    DEFAULT_COSTS,
    CP_WATER, CP_VAPOR, LV, T_BOIL, T_AMBIENT, BIOMASS_LHV,
    DEFAULT_COIL_LENGTH, DEFAULT_TUBE_OD, DEFAULT_TUBE_ID,
    DEFAULT_COIL_DIAM, DEFAULT_FLOW_RATE, STRAW_PER_RAI_DEFAULT,
    CH4_EF, N2O_EF, GWP_CH4, GWP_N2O,
)

st.set_page_config(
    page_title="Zero-Burn Simulation Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# SIDEBAR — Lab Navigation
# ================================================================
st.sidebar.markdown("## 🔬 Zero-Burn Lab")
st.sidebar.markdown("*Scientific Simulation Workbench*")
st.sidebar.divider()

lab = st.sidebar.radio("Select Lab:", [
    "🌡️ Boiler Engineering",
    "🍄 Mushroom Yield Lab",
    "💰 Economic Simulator",
    "🎲 Monte Carlo Analysis",
    "🌍 Carbon & Regional Scale",
    "⚙️ System Optimizer",
], index=0)

st.sidebar.divider()
st.sidebar.caption("All formulas from FEASIBILITY_STUDY.md v2.0")
st.sidebar.caption("Sources: IPCC 2019, TGO, USDA-ARS, CABI, MASU Journal")


# ================================================================
# LAB 1: BOILER ENGINEERING
# ================================================================
if lab == "🌡️ Boiler Engineering":
    st.title("🌡️ Boiler Engineering Lab")
    st.markdown("*Optimize the helical coil steam generator design using verified thermodynamic formulas.*")

    col_ctrl, col_results = st.columns([1, 2])

    with col_ctrl:
        st.subheader("Design Parameters")
        flow_rate = st.slider("Water flow rate (ml/s)", 10, 100, 45, 5,
                              help="Mass flow rate through the copper coil") / 1000  # convert to kg/s
        t_out = st.slider("Target outlet temperature (°C)", 100, 150, 120, 5,
                          help="Superheated steam target temperature")
        coil_length = st.slider("Coil length (meters)", 10, 30, 21, 1,
                                help="Total copper tube length (½\" Type L)")
        combustion_eff = st.slider("Combustion efficiency (%)", 20, 55, 35, 5,
                                  help="Firebox thermal efficiency") / 100
        u_value = st.slider("Heat transfer coefficient U (W/m²K)", 100, 1000, 300, 50,
                            help="Overall U-value. Literature: 269-997 for copper helical coils")
        water_hardness = st.slider("Water hardness (ppm CaCO₃)", 50, 500, 250, 50,
                                  help="Affects scale buildup rate")

    with col_results:
        # Energy calculation
        energy = compute_steam_energy(flow_rate=flow_rate, t_out=t_out)
        fuel = compute_fuel_requirement(energy['q_total_kw'], combustion_eff)
        ht = compute_heat_transfer_adequacy(coil_length=coil_length, u_value=u_value, t_out=t_out)

        # KPI row
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Power", f"{energy['q_total_kw']} kW")
        kpi2.metric("Fuel Rate", f"{fuel['fuel_rate_kg_hr']} kg/hr")
        kpi3.metric("Area Adequacy", f"{ht['adequacy_pct']}%",
                    delta="OK" if ht['is_adequate'] else "⚠️ UNDERSIZED",
                    delta_color="normal" if ht['is_adequate'] else "inverse")
        kpi4.metric("LMTD", f"{ht['lmtd_c']}°C")

        # Energy breakdown
        tab1, tab2, tab3 = st.tabs(["Temperature Profile", "Energy Breakdown", "Scale Degradation"])

        with tab1:
            positions, temps, pressures, zones = compute_temperature_profile(
                coil_length=coil_length, flow_rate=flow_rate, combustion_eff=combustion_eff
            )
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=positions, y=temps, mode='lines', name='Water/Steam Temp (°C)',
                                    line=dict(color='#10b981', width=3),
                                    fill='tozeroy', fillcolor='rgba(16,185,129,0.1)'))
            fig.add_trace(go.Scatter(x=positions, y=np.array(pressures) * 40, mode='lines',
                                    name='Pressure (bar × 40)', line=dict(color='#3b82f6', width=2, dash='dot')))
            fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="100°C (Pasteurization threshold)")
            fig.update_layout(title="Temperature & Pressure Along Helical Coil",
                            xaxis_title="Position along coil (m)", yaxis_title="Temperature (°C)",
                            template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig_energy = go.Figure(data=[
                go.Bar(name='Sensible (25→100°C)', x=['Energy Budget'], y=[energy['q_sensible_kw']], marker_color='#60a5fa'),
                go.Bar(name='Latent (phase change)', x=['Energy Budget'], y=[energy['q_latent_kw']], marker_color='#f59e0b'),
                go.Bar(name=f'Superheat (100→{t_out}°C)', x=['Energy Budget'], y=[energy['q_superheat_kw']], marker_color='#ef4444'),
            ])
            fig_energy.update_layout(barmode='stack', template="plotly_white", height=350,
                                    title="Energy Budget Breakdown (kW)",
                                    yaxis_title="Power (kW)")
            st.plotly_chart(fig_energy, use_container_width=True)

            st.markdown(f"""
            **Key Results:**
            - Fuel consumed per rai: **{fuel['fuel_per_treatment_kg']} kg** ({round(fuel['fuel_per_treatment_kg']/STRAW_PER_RAI_DEFAULT*100, 1)}% of straw)
            - Substrate remaining: **{STRAW_PER_RAI_DEFAULT - fuel['fuel_per_treatment_kg']} kg** available for mushrooms
            - Optimal coil length (15% margin): **{optimize_coil_length(u_value=u_value, t_out=t_out)} m**
            """)

        with tab3:
            scale_data = compute_scale_profile(hours=500, water_hardness_ppm=water_hardness,
                                              coil_length=coil_length, base_u=u_value)
            df_scale = pd.DataFrame(scale_data)
            fig_scale = go.Figure()
            fig_scale.add_trace(go.Scatter(x=df_scale['hours'], y=df_scale['efficiency_pct'],
                                          mode='lines', name='Efficiency %', line=dict(color='#6366f1', width=3)))
            fig_scale.add_trace(go.Scatter(x=df_scale['hours'], y=df_scale['scale_mm'] * 100,
                                          mode='lines', name='Scale (mm × 100)', line=dict(color='#f43f5e', width=2)))
            fig_scale.add_hline(y=80, line_dash="dash", line_color="orange",
                              annotation_text="Descale recommended (80% efficiency)")
            fig_scale.update_layout(title=f"Scale Buildup & Efficiency at {water_hardness} ppm hardness",
                                  xaxis_title="Operating Hours", yaxis_title="Efficiency (%)",
                                  template="plotly_white", height=400)
            st.plotly_chart(fig_scale, use_container_width=True)

            # Find when to descale
            descale_hr = next((d['hours'] for d in scale_data if d['efficiency_pct'] < 80), 500)
            st.info(f"💡 **Descaling recommended every ~{descale_hr} hours** at {water_hardness} ppm water hardness. Use 2% citric acid solution, 15 min contact time.")


# ================================================================
# LAB 2: MUSHROOM YIELD
# ================================================================
elif lab == "🍄 Mushroom Yield Lab":
    st.title("🍄 Mushroom Yield Laboratory")
    st.markdown("*Explore Volvariella volvacea yield under different conditions.*")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Cultivation Parameters")
        straw = st.slider("Straw per rai (kg)", 400, 900, 650, 25)
        be = st.slider("Biological Efficiency (%)", 1, 30, 12) / 100
        fuel_frac = st.slider("Fuel fraction (%)", 5, 20, 10) / 100
        price = st.slider("Selling price (฿/kg)", 20, 160, 45, 5)

        st.divider()
        st.subheader("Risk Factors")
        steam_temp = st.slider("Steam treatment temp (°C)", 60, 140, 120, 10)
        spawn_quality = st.selectbox("Spawn quality", ['certified', 'local', 'unknown'])
        sanitation = st.selectbox("Sanitation protocol", ['strict', 'standard', 'none'])

        supplement = st.checkbox("Add rice bran supplement (+2% BE)")
        supp_boost = 0.02 if supplement else 0.0

    with col2:
        yield_data = compute_mushroom_yield(straw, be, fuel_frac, supp_boost)
        econ = compute_economics(be, price, straw, fuel_frac, supplement_boost=supp_boost)
        risk = compute_contamination_risk(steam_temp, spawn_quality, sanitation)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Yield", f"{yield_data['fresh_yield_kg']} kg/rai")
        k2.metric("Revenue", f"฿{econ['revenue_thb']:,}")
        k3.metric("Net Profit", f"฿{econ['profit_thb']:,}",
                  delta="Profitable" if econ['is_profitable'] else "LOSS",
                  delta_color="normal" if econ['is_profitable'] else "inverse")
        k4.metric("Contamination Risk", risk['risk_level'],
                  delta=f"{risk['contamination_prob']*100:.1f}%",
                  delta_color="inverse" if risk['risk_level'] == 'HIGH' else "off")

        tab_y1, tab_y2, tab_y3 = st.tabs(["Yield Comparison", "Cost Breakdown", "Risk Analysis"])

        with tab_y1:
            # Compare burning vs mushroom
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(x=['Burning Straw', 'Mushroom Cultivation'],
                                     y=[0, econ['revenue_thb']],
                                     marker_color=['#ef4444', '#10b981'],
                                     text=[f'฿0', f'฿{econ["revenue_thb"]:,}'],
                                     textposition='auto'))
            fig_comp.update_layout(title="Revenue: Burning vs. Mushroom Cultivation (per rai)",
                                 yaxis_title="Revenue (฿)", template="plotly_white", height=350)
            st.plotly_chart(fig_comp, use_container_width=True)

            # BE comparison across substrates
            be_data = pd.DataFrame({
                'Substrate/Method': ['Rice straw (outdoor)', 'Rice straw + bran', 'Cotton waste compost',
                                    'Indoor controlled', 'Our system (est.)'],
                'BE (%)': [10, 14, 35, 20, yield_data['effective_be_pct']],
            })
            fig_be = px.bar(be_data, x='Substrate/Method', y='BE (%)', color='BE (%)',
                           color_continuous_scale='Greens', title="Biological Efficiency by Method")
            fig_be.update_layout(template="plotly_white", height=300)
            st.plotly_chart(fig_be, use_container_width=True)

        with tab_y2:
            costs_df = pd.DataFrame([
                {'Category': k, 'Cost (฿)': v} for k, v in DEFAULT_COSTS.items()
            ])
            fig_cost = px.pie(costs_df, values='Cost (฿)', names='Category',
                             title="Operating Cost Breakdown per Rai",
                             color_discrete_sequence=px.colors.qualitative.Set3)
            fig_cost.update_layout(height=400)
            st.plotly_chart(fig_cost, use_container_width=True)

            st.markdown(f"**Total cost: ฿{econ['total_cost_thb']:,}/rai** | Break-even: {econ['break_even_kg']} kg ({econ['break_even_be_pct']}% BE)")

        with tab_y3:
            st.markdown(f"""
            ### Trichoderma Contamination Risk Assessment
            
            | Factor | Value | Contribution |
            |--------|-------|-------------|
            | Steam temperature | {steam_temp}°C | {'✅ Good' if steam_temp >= 100 else '⚠️ Below pasteurization'} |
            | Spawn quality | {spawn_quality} | {'✅' if spawn_quality == 'certified' else '⚠️'} |
            | Sanitation protocol | {sanitation} | {'✅' if sanitation == 'strict' else '⚠️'} |
            | **Estimated contamination probability** | **{risk['contamination_prob']*100:.1f}%** | {risk['risk_level']} |
            | **Expected yield loss (when contaminated)** | **80%** | Literature: 60-100% |
            
            *Source: Trichoderma risk data from LaMycosphere, NIH PMC*
            """)

            if risk['risk_level'] == 'HIGH':
                st.error("🚨 High contamination risk! Consider improving steam temperature, using certified spawn, and implementing strict sanitation.")
            elif risk['risk_level'] == 'MEDIUM':
                st.warning("⚠️ Medium contamination risk. Improvements recommended.")
            else:
                st.success("✅ Low contamination risk. Good practices in place.")


# ================================================================
# LAB 3: ECONOMIC SIMULATOR
# ================================================================
elif lab == "💰 Economic Simulator":
    st.title("💰 Economic Simulator")
    st.markdown("*Sensitivity analysis and scenario comparison for farm-level economics.*")

    # Sensitivity matrix
    be_vals, price_vals, matrix = compute_sensitivity_matrix()
    df_matrix = pd.DataFrame(matrix, index=[f"{b*100:.0f}% BE" for b in be_vals],
                            columns=[f"฿{p}/kg" for p in price_vals])

    st.subheader("Sensitivity Matrix — Net Profit per Rai (฿)")
    st.markdown("*Green = profitable, Red = loss*")

    fig_heat = px.imshow(matrix, x=[f"฿{p}" for p in price_vals],
                        y=[f"{b*100:.0f}%" for b in be_vals],
                        color_continuous_scale='RdYlGn', aspect='auto',
                        labels=dict(x="Price per kg", y="Biological Efficiency", color="Profit (฿)"),
                        text_auto=True)
    fig_heat.update_layout(title="Profit Heatmap: BE × Price", height=400, template="plotly_white")
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

    # Scenario comparison
    st.subheader("Scenario Comparison")
    scenarios = {
        'Very Conservative': {'be': 0.08, 'price': 45, 'label': '8% BE, ฿45 wholesale'},
        'Conservative': {'be': 0.08, 'price': 90, 'label': '8% BE, ฿90 retail'},
        'Moderate': {'be': 0.12, 'price': 45, 'label': '12% BE, ฿45 wholesale'},
        'Moderate-High': {'be': 0.12, 'price': 90, 'label': '12% BE, ฿90 retail'},
        'Optimistic': {'be': 0.15, 'price': 90, 'label': '15% BE, ฿90 retail'},
    }
    rows = []
    for name, s in scenarios.items():
        e = compute_economics(be=s['be'], price_per_kg=s['price'])
        rows.append({
            'Scenario': name,
            'Description': s['label'],
            'Yield (kg/rai)': e['yield_kg'],
            'Revenue (฿)': e['revenue_thb'],
            'Net Profit (฿)': e['profit_thb'],
            'Annual (×2) (฿)': e['profit_per_year_thb'],
            'Margin': f"{e['margin_pct']}%",
            'Profitable': '✅' if e['is_profitable'] else '❌',
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Income impact for 10-rai farm
    st.subheader("Impact on a 10-Rai Farm")
    farm_be = st.select_slider("Assumed BE", options=[5, 8, 10, 12, 15, 20], value=12)
    farm_price = st.select_slider("Price (฿/kg)", options=[30, 45, 60, 90, 120], value=45)
    farm_econ = compute_economics(be=farm_be/100, price_per_kg=farm_price)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rice-only income (10 rai)", "฿160,000/yr")
    c2.metric("+ Mushroom income", f"฿{farm_econ['profit_per_year_thb'] * 10:,}/yr")
    c3.metric("Total income", f"฿{160000 + farm_econ['profit_per_year_thb'] * 10:,}/yr",
             delta=f"+{round(farm_econ['profit_per_year_thb'] * 10 / 160000 * 100, 1)}%")


# ================================================================
# LAB 4: MONTE CARLO
# ================================================================
elif lab == "🎲 Monte Carlo Analysis":
    st.title("🎲 Monte Carlo Profit Simulation")
    st.markdown("*Run 10,000+ simulated farm seasons to understand risk distribution.*")

    col_mc1, col_mc2 = st.columns([1, 2])

    with col_mc1:
        st.subheader("Distribution Parameters")
        n_sims = st.slider("Number of simulations", 1000, 50000, 10000, 1000)
        be_mean = st.slider("Mean BE (%)", 5, 20, 10) / 100
        be_std = st.slider("BE Std Dev (%)", 1, 8, 3) / 100
        price_mean = st.slider("Mean price (฿/kg)", 30, 120, 55, 5)
        price_std = st.slider("Price Std Dev (฿)", 5, 30, 15, 5)
        contam_prob = st.slider("Contamination probability (%)", 0, 30, 8) / 100

    with col_mc2:
        mc = monte_carlo_profit(
            n_simulations=n_sims, be_mean=be_mean, be_std=be_std,
            price_mean=price_mean, price_std=price_std,
            contamination_prob=contam_prob,
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Probability of Profit", f"{mc['prob_profitable']}%")
        k2.metric("Mean Profit/rai", f"฿{mc['mean_profit']:,}")
        k3.metric("5th Percentile", f"฿{mc['p5']:,}",
                  delta="Worst 5%" if mc['p5'] < 0 else "", delta_color="inverse" if mc['p5'] < 0 else "off")
        k4.metric("95th Percentile", f"฿{mc['p95']:,}")

        # Distribution histogram
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Histogram(
            x=mc['profits'], nbinsx=80,
            marker_color=np.where(mc['profits'] >= 0, '#10b981', '#ef4444').tolist(),
            name='Profit distribution'
        ))
        fig_mc.add_vline(x=0, line_dash="dash", line_color="white", line_width=2)
        fig_mc.add_vline(x=mc['mean_profit'], line_dash="solid", line_color="#f59e0b",
                        annotation_text=f"Mean: ฿{mc['mean_profit']:,}")
        fig_mc.update_layout(
            title=f"Profit Distribution ({n_sims:,} simulations, {mc['n_contaminated']} contaminated)",
            xaxis_title="Net Profit per Rai (฿)", yaxis_title="Frequency",
            template="plotly_dark", height=450,
            bargap=0.05,
        )
        st.plotly_chart(fig_mc, use_container_width=True)

        # Summary stats
        st.markdown(f"""
        | Statistic | Value |
        |-----------|-------|
        | Simulations | {n_sims:,} |
        | Contamination events | {mc['n_contaminated']:,} ({mc['n_contaminated']/n_sims*100:.1f}%) |
        | Mean profit | ฿{mc['mean_profit']:,} |
        | Median profit | ฿{mc['median_profit']:,} |
        | Std deviation | ฿{mc['std_profit']:,} |
        | P5 (worst 5%) | ฿{mc['p5']:,} |
        | P25 | ฿{mc['p25']:,} |
        | P75 | ฿{mc['p75']:,} |
        | P95 (best 5%) | ฿{mc['p95']:,} |
        | **Probability of profit** | **{mc['prob_profitable']}%** |
        | Probability of loss > ฿500 | {mc['prob_loss_gt_500']}% |
        """)


# ================================================================
# LAB 5: CARBON & REGIONAL
# ================================================================
elif lab == "🌍 Carbon & Regional Scale":
    st.title("🌍 Carbon Credits & Regional Scale")

    tab_c, tab_r = st.tabs(["Carbon Credit Calculator", "Regional Impact Model"])

    with tab_c:
        st.subheader("IPCC-Based Carbon Credit Calculator")
        st.markdown("*Using IPCC 2019 non-CO₂ emission factors only (CH₄ + N₂O).*")

        c_price = st.slider("Carbon credit price (฿/tCO₂eq)", 50, 3000, 1000, 50,
                           help="T-VER: ฿175 avg, ฿1,000 ag sector, ฿2,076 premium")
        c_rai = st.slider("Total rai in program", 100, 50000, 5000, 500)

        cc = compute_carbon_credits(carbon_price_thb=c_price, n_rai=c_rai)

        c1, c2, c3 = st.columns(3)
        c1.metric("CO₂eq avoided/rai", f"{cc['total_co2eq_kg']} kg")
        c2.metric("Credit revenue/rai", f"฿{cc['revenue_per_rai_thb']:.0f}")
        c3.metric("Total program revenue", f"฿{cc['revenue_total_thb']:,.0f}")

        st.markdown(f"""
        ### Emission Factor Breakdown (per rai)
        | Gas | Emission (kg) | GWP | CO₂eq (kg) |
        |-----|-------------|-----|-----------|
        | CH₄ | {cc['straw_burned_tons']:.3f} × {CH4_EF} = {cc['straw_burned_tons']*CH4_EF:.3f} | ×{GWP_CH4} | {cc['ch4_co2eq_kg']} |
        | N₂O | {cc['straw_burned_tons']:.3f} × {N2O_EF} = {cc['straw_burned_tons']*N2O_EF:.4f} | ×{GWP_N2O} | {cc['n2o_co2eq_kg']} |
        | **Total** | | | **{cc['total_co2eq_kg']} kg = {cc['total_tco2eq']} tCO₂eq** |
        
        > ⚠️ CO₂ from biomass burning is treated as **biogenic (carbon-neutral)** per IPCC methodology. Only CH₄ and N₂O count toward carbon credits.
        """)

    with tab_r:
        st.subheader("Regional Impact Simulator")
        r_villages = st.slider("Number of villages", 1, 20, 4)
        r_farmers = st.slider("Farmers per village", 10, 100, 50)
        r_rai = st.slider("Average rai per farmer", 5, 25, 12)
        r_adoption = st.slider("Adoption rate (%)", 10, 100, 75) / 100
        r_be = st.slider("Achieved BE (%)", 5, 20, 12) / 100
        r_price = st.slider("Mushroom price (฿/kg)", 30, 120, 45, 5)

        regional = compute_regional_impact(r_villages, r_farmers, r_rai, r_adoption, r_be, r_price)

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Total Rai", f"{regional['total_rai']:,}")
        r2.metric("Farmers Reached", f"{regional['total_farmers']:,}")
        r3.metric("Annual Revenue", f"฿{regional['total_mushroom_revenue'] * 2:,.0f}")
        r4.metric("ROI on Equipment", f"{regional['roi_pct']}%")

        fig_reg = go.Figure(data=[
            go.Bar(x=['Mushroom Revenue', 'Carbon Credits', 'Equipment Cost'],
                   y=[regional['total_mushroom_revenue'] * 2, regional['total_carbon_revenue'] * 2, -regional['equipment_investment']],
                   marker_color=['#10b981', '#3b82f6', '#ef4444'],
                   text=[f"฿{regional['total_mushroom_revenue']*2:,.0f}", f"฿{regional['total_carbon_revenue']*2:,.0f}", f"-฿{regional['equipment_investment']:,.0f}"],
                   textposition='auto')
        ])
        fig_reg.update_layout(title="Annual Economics (Regional)", yaxis_title="฿ THB",
                            template="plotly_white", height=400)
        st.plotly_chart(fig_reg, use_container_width=True)

        st.markdown(f"""
        **Regional Summary:**
        - Steam-Blast units needed: **{regional['units_needed']}** (at ฿26,550 each)
        - Equipment investment: **฿{regional['equipment_investment']:,}**
        - CO₂eq avoided annually: **{regional['total_co2eq_avoided_tons']} tons**
        - **First-year ROI: {regional['roi_pct']}%**
        """)


# ================================================================
# LAB 6: SYSTEM OPTIMIZER
# ================================================================
elif lab == "⚙️ System Optimizer":
    st.title("⚙️ System Optimizer")
    st.markdown("*Use scipy optimization to find the best design parameters.*")

    st.subheader("1. Minimum Coil Length")
    opt_u = st.slider("Assumed U-value (W/m²K)", 100, 1000, 300, 50, key="opt_u")
    opt_temp = st.slider("Target outlet temp (°C)", 100, 140, 120, 5, key="opt_temp")
    opt_margin = st.slider("Safety margin (%)", 0, 30, 15, 5, key="opt_margin")

    min_coil = optimize_coil_length(u_value=opt_u, t_out=opt_temp, safety_margin=1 + opt_margin/100)
    ht_check = compute_heat_transfer_adequacy(coil_length=min_coil, u_value=opt_u, t_out=opt_temp)

    st.success(f"✅ Optimal coil length: **{min_coil} m** (with {opt_margin}% safety margin)")
    st.markdown(f"Heat transfer adequacy at {min_coil}m: **{ht_check['adequacy_pct']}%**")

    st.divider()
    st.subheader("2. Optimal Flow Rate for Maximum Profit")

    try:
        opt_flow = optimize_system(target='max_profit_flow_rate')
        st.success(f"✅ Optimal flow rate: **{opt_flow['optimal_flow_rate_ml_s']} ml/s** → Profit: ฿{opt_flow['profit_at_optimal']:,}/rai")
    except Exception as e:
        st.warning(f"Optimization error: {e}")

    st.divider()
    st.subheader("3. Parameter Sweep — Coil Length vs. Flow Rate")

    coil_range = np.arange(12, 30, 1)
    flow_range = np.arange(0.02, 0.08, 0.005)
    profit_grid = np.zeros((len(coil_range), len(flow_range)))

    for i, cl in enumerate(coil_range):
        for j, fr in enumerate(flow_range):
            energy = compute_steam_energy(flow_rate=fr, t_out=120)
            fuel = compute_fuel_requirement(energy['q_total_kw'])
            fuel_frac = fuel['fuel_per_treatment_kg'] / STRAW_PER_RAI_DEFAULT
            if fuel_frac >= 1.0:
                profit_grid[i, j] = -5000
                continue
            ht = compute_heat_transfer_adequacy(coil_length=cl, t_out=120)
            if not ht['is_adequate']:
                profit_grid[i, j] = -2000
                continue
            econ = compute_economics(be=0.12, price_per_kg=45, fuel_fraction=min(fuel_frac, 0.99))
            profit_grid[i, j] = econ['profit_thb']

    fig_sweep = px.imshow(
        profit_grid.T, x=[f"{c}m" for c in coil_range], y=[f"{f*1000:.0f} ml/s" for f in flow_range],
        color_continuous_scale='RdYlGn', aspect='auto',
        labels=dict(x="Coil Length", y="Flow Rate", color="Profit (฿)"),
    )
    fig_sweep.update_layout(title="Profit Surface: Coil Length × Flow Rate (at 12% BE, ฿45/kg)",
                           template="plotly_white", height=500)
    st.plotly_chart(fig_sweep, use_container_width=True)

    st.caption("Green = profitable, Red = loss (insufficient heat transfer or excessive fuel use)")
