"""
Zero-Burn Blueprint — Advanced Labs v3.0 (Complete)
15 Streamlit labs: Round 1 (Physics) + Round 2 (Biology) + Round 3 (Environment) + Round 4 (Economics)
Run with: source .venv/bin/activate && cd simulation && streamlit run app_v3.py
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from engines_v3 import (
    compute_reynolds, compute_dean_number, compute_critical_reynolds_helical,
    compute_nusselt_helical, compute_overall_u, compute_pressure_drop_helical,
    compute_flow_rate_sweep,
    compute_trichoderma_kill, compute_kill_curve_data, compute_time_to_kill,
    compute_growth_curve, compute_substrate_comparison,
    compute_seasonal_windows, compute_competitive_comparison,
    compute_spawn_rate_optimization, compute_moisture_optimization,
    compute_indoor_outdoor_comparison, compute_harvest_labor_model,
    compute_straw_degradation, compute_rainfall_impact, compute_temperature_corridor,
    compute_cooperative_model, compute_market_absorption, compute_year_round_operations,
    compute_carbon_credits_v2, compute_iot_monitoring, compute_tractor_operations,
    compute_autonomous_tractor_roi,
    compute_contamination_stress_test, compute_market_saturation,
    compute_straw_variety_comparison, compute_adoption_curve, compute_full_sensitivity,
    compute_pm25_emissions, compute_health_cost_impact, compute_regional_pollution_impact,
    compute_multi_species_comparison, compute_circular_economy_cascade,
    compute_biochar_carbon_credits,
    compute_enzymatic_pretreatment, compute_mycelium_materials,
    compute_drone_operations, compute_cold_pasteurization,
    DEFAULT_TUBE_ID, DEFAULT_TUBE_OD, DEFAULT_COIL_DIAM,
)
from references import render_references
from engines import (
    compute_steam_energy, compute_fuel_requirement, compute_heat_transfer_adequacy,
    compute_economics, monte_carlo_profit, compute_mushroom_yield,
    STRAW_PER_RAI_DEFAULT, DEFAULT_COSTS,
)

st.set_page_config(
    page_title="Zero-Burn Lab v3.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# SIDEBAR
# ================================================================
st.sidebar.markdown("## 🧬 Zero-Burn Lab v3.0")
st.sidebar.markdown("*Deep Scientific Simulation*")
st.sidebar.divider()

st.sidebar.markdown("### Round 1: Physics")
lab = st.sidebar.radio("Select Lab:", [
    "🔬 Advanced Heat Transfer",
    "🦠 Sterilization Science",
    "📈 Growth Kinetics",
    "🌿 Substrate Optimizer",
    "🗓️ Seasonal Planner",
    "⚔️ Competitive Analysis",
    "🎲 Advanced Monte Carlo",
    "─── Round 2: Biology ───",
    "🧫 Spawn Rate Optimizer",
    "💧 Moisture & Soaking",
    "🏠 Indoor vs Outdoor",
    "👷 Harvest Labor Model",
    "─── Round 3: Environment ───",
    "🌾 Straw Degradation",
    "🌡️ Temperature Corridor",
    "─── Round 4: Economics ───",
    "🤝 Cooperative Model",
    "🏪 Market Absorption",
    "📅 Year-Round Planner",
    "─── Round 5: Technology ───",
    "🌍 Carbon Credits (T-VER)",
    "📡 IoT Monitoring & MRV",
    "🚜 Tractor Operations",
    "🤖 Autonomous Tractor ROI",
    "─── Round 6: Risk Validation ───",
    "🧪 Contamination Stress Test",
    "📉 Market Saturation",
    "🌾 Rice Variety Straw",
    "📈 Adoption S-Curve",
    "🎯 Sensitivity Tornado",
    "─── Round 7: Health & Pollution ───",
    "💨 PM2.5 Emissions",
    "🏥 Healthcare Cost Impact",
    "🌍 Regional Pollution Impact",
    "─── Round 8: Breakthrough Science ───",
    "🦄 Multi-Species Comparison",
    "♻️ Circular Economy Cascade",
    "🔥 Biochar + Carbon Credits",
    "🧬 Enzymatic Pre-treatment",
    "🧱 Mycelium Materials",
    "─── Round 9: Drone Tech ───",
    "🛸 Drone Operations & ROI",
    "🧪 Drone Cold Pasteurization",
], index=0)

st.sidebar.divider()
st.sidebar.caption("v3.5 — All 9 Research Rounds")
st.sidebar.caption("Physics • Biology • Env • Econ • Tech • Risk • Health • Breakthrough • Drones")


# ================================================================
# LAB 1: ADVANCED HEAT TRANSFER (ROUND 1)
# ================================================================
if lab == "🔬 Advanced Heat Transfer":
    st.title("🔬 Advanced Heat Transfer Analysis")
    st.markdown("*Helical coil heat transfer using Dean number correlations (Schmidt 1967, Seban & McLaughlin 1963).*")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Design Parameters")
        flow_ml = st.slider("Flow rate (ml/s)", 5, 100, 45, 5)
        tube_id_mm = st.slider("Tube inner diameter (mm)", 8.0, 20.0, round(DEFAULT_TUBE_ID*1000, 1), 0.5)
        coil_d_mm = st.slider("Coil diameter (mm)", 100, 400, int(DEFAULT_COIL_DIAM*1000), 10)
        coil_length = st.slider("Coil length (m)", 10, 35, 21, 1)
        h_outer = st.slider("Flue gas h (W/m²K)", 20, 150, 50, 10, help="Outer heat transfer coefficient")
        scale_mm = st.slider("Scale buildup (mm)", 0.0, 2.0, 0.0, 0.1)

    with col2:
        flow_kg = flow_ml / 1000
        tube_id = tube_id_mm / 1000
        tube_od = tube_id + 0.00152
        coil_d = coil_d_mm / 1000

        nu_data = compute_nusselt_helical(flow_kg, tube_id, coil_d)
        u_data = compute_overall_u(nu_data['h_coil_w_m2k'], h_outer, tube_id, tube_od, scale_thickness_mm=scale_mm)
        dp_data = compute_pressure_drop_helical(flow_kg, coil_length, tube_id, coil_d)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Dean Number", f"{nu_data['dean_number']:,.0f}", delta=nu_data['flow_regime'])
        k2.metric("Enhancement", f"{nu_data['enhancement_ratio']}×", delta="vs straight tube")
        k3.metric("U-overall", f"{u_data['U_overall_w_m2k']} W/m²K", delta=f"Bottleneck: {u_data['bottleneck']}")
        k4.metric("Pressure Drop", f"{dp_data['dp_coil_bar']} bar",
                  delta="OK" if dp_data['is_acceptable'] else "⚠️ HIGH",
                  delta_color="normal" if dp_data['is_acceptable'] else "inverse")

        tab1, tab2, tab3 = st.tabs(["Flow Rate Sweep", "Resistance Breakdown", "Detailed Numbers"])

        with tab1:
            sweep = compute_flow_rate_sweep(list(range(5, 101, 5)), coil_length, tube_id, coil_d)
            df_sweep = pd.DataFrame(sweep)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_sweep['flow_ml_s'], y=df_sweep['nusselt'],
                                    mode='lines+markers', name='Nusselt (coil)',
                                    line=dict(color='#10b981', width=3)))
            fig.add_trace(go.Scatter(x=df_sweep['flow_ml_s'], y=df_sweep['enhancement'],
                                    mode='lines', name='Enhancement ratio',
                                    line=dict(color='#f59e0b', width=2, dash='dot'), yaxis='y2'))
            fig.update_layout(title="Nusselt Number & Enhancement Ratio vs Flow Rate",
                            xaxis_title="Flow Rate (ml/s)", yaxis_title="Nusselt Number",
                            yaxis2=dict(title="Enhancement Ratio", overlaying='y', side='right'),
                            template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)
            re_crit = compute_critical_reynolds_helical(tube_id, coil_d)
            st.info(f"💡 **Regime transition:** Re_crit = {re_crit:,.0f} (vs 2,300 for straight pipe). "
                   f"Helical coils delay turbulence by {re_crit/2300:.1f}×.")

        with tab2:
            fig_resist = go.Figure(data=[
                go.Bar(name='Outer (flue gas)', x=['Resistance'], y=[u_data['pct_outer_resistance']], marker_color='#ef4444'),
                go.Bar(name='Tube wall', x=['Resistance'], y=[u_data['pct_wall_resistance']], marker_color='#f59e0b'),
                go.Bar(name='Inner (water)', x=['Resistance'], y=[u_data['pct_inner_resistance']], marker_color='#3b82f6'),
                go.Bar(name='Scale', x=['Resistance'], y=[u_data['pct_scale_resistance']], marker_color='#6b7280'),
            ])
            fig_resist.update_layout(barmode='stack', template="plotly_white", height=300,
                                    title="Thermal Resistance Distribution (%)", yaxis_title="% of Total")
            st.plotly_chart(fig_resist, use_container_width=True)

        with tab3:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""| Parameter | Value |
|-----------|-------|
| Reynolds | {nu_data['reynolds']:,.0f} |
| Dean Number | {nu_data['dean_number']:,.0f} |
| Regime | {nu_data['flow_regime']} |
| Velocity | {dp_data['velocity_m_s']} m/s |""")
            with col_b:
                st.markdown(f"""| Parameter | Value |
|-----------|-------|
| Nu (coil) | {nu_data['nusselt_coil']} |
| Enhancement | {nu_data['enhancement_ratio']}× |
| h_inner | {nu_data['h_coil_w_m2k']} W/m²K |
| U_overall | {u_data['U_overall_w_m2k']} W/m²K |""")


# ================================================================
# LAB 2: STERILIZATION SCIENCE (ROUND 1)
# ================================================================
    render_references("🌡️ Heat Transfer")

elif lab == "🦠 Sterilization Science":
    st.title("🦠 Sterilization Science Lab")
    st.markdown("*Trichoderma thermal kill kinetics using Bigelow (1921) D-value model.*")
    col1, col2 = st.columns([1, 2])
    with col1:
        temp = st.slider("Steam temperature (°C)", 40, 140, 120, 5)
        time_min = st.slider("Exposure time (min)", 1, 120, 45, 1)
        st.divider()
        st.latex(r"D(T) = D_{ref} \times 10^{\frac{T_{ref} - T}{z}}")
        st.markdown("- D_ref = 10 min at T_ref = 60°C\n- z = 15°C (fungal spores)")

    with col2:
        kill = compute_trichoderma_kill(temp, time_min)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Log Reductions", f"{kill['log_reductions']}")
        k2.metric("Kill %", f"{kill['kill_pct']}%")
        k3.metric("Safety Factor", f"{kill['safety_factor']}×", delta=kill['assessment'].split('—')[0].strip())
        k4.metric("D-value", f"{kill['d_value_min']:.4f} min")

        curve = compute_kill_curve_data(list(range(40, 141, 2)), time_min)
        df_curve = pd.DataFrame(curve)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_curve['temperature_c'], y=df_curve['log_reductions'],
                                mode='lines', line=dict(color='#ef4444', width=3),
                                fill='tozeroy', fillcolor='rgba(239,68,68,0.1)'))
        fig.add_hline(y=6, line_dash="dash", line_color="#10b981", annotation_text="6-log (commercial)")
        fig.add_vline(x=temp, line_color="#3b82f6", annotation_text=f"Our: {temp}°C")
        fig.update_layout(title=f"Kill Curve at {time_min} min", xaxis_title="Temperature (°C)",
                         yaxis_title="Log Reductions", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)


# ================================================================
# LAB 3: GROWTH KINETICS (ROUND 1)
# ================================================================
    render_references("🦠 Sterilization Science")

elif lab == "📈 Growth Kinetics":
    st.title("📈 V. volvacea Growth Kinetics Lab")
    col1, col2 = st.columns([1, 2])
    with col1:
        be_max = st.slider("Maximum BE (%)", 5, 25, 12) / 100
        temp = st.slider("Growing temperature (°C)", 15, 42, 32, 1)
        humidity = st.slider("Humidity (%)", 40, 100, 85, 5)
        days = st.slider("Observation period (days)", 14, 40, 30)
        supplement = st.selectbox("Supplement", ['none', 'rice_bran_2pct', 'rice_bran_5pct', 'cotton_seed', 'wheat_bran'],
            format_func=lambda x: {'none': 'None', 'rice_bran_2pct': 'Rice bran 2% (+30%)',
                'rice_bran_5pct': 'Rice bran 5% (+25%)', 'cotton_seed': 'Cotton seed (+15%)',
                'wheat_bran': 'Wheat bran (+20%)'}[x])

    with col2:
        growth = compute_growth_curve(days, be_max, temp, humidity, supplement_type=supplement)
        df_growth = pd.DataFrame(growth)
        final = df_growth.iloc[-1]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Yield", f"{final['cumulative_yield_kg']:.1f} kg")
        k2.metric("Effective BE", f"{final['cumulative_be_pct']:.1f}%")
        k3.metric("Peak Day", f"Day {df_growth.loc[df_growth['daily_yield_kg'].idxmax(), 'day']}")
        k4.metric("Temp", f"{temp}°C", delta="Optimal" if 30 <= temp <= 35 else "Suboptimal",
                  delta_color="normal" if 30 <= temp <= 35 else "inverse")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_growth['day'], y=df_growth['daily_yield_kg'],
                            name='Daily yield', marker_color='#10b981', opacity=0.6))
        fig.add_trace(go.Scatter(x=df_growth['day'], y=df_growth['cumulative_yield_kg'],
                                mode='lines', name='Cumulative', line=dict(color='#3b82f6', width=3), yaxis='y2'))
        fig.update_layout(title="Growth & Yield", xaxis_title="Day", yaxis_title="Daily (kg)",
                         yaxis2=dict(title="Cumulative (kg)", overlaying='y', side='right'),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)


# ================================================================
# LAB 4: SUBSTRATE OPTIMIZER (ROUND 1)
# ================================================================
    render_references("📈 Growth Kinetics")

elif lab == "🌿 Substrate Optimizer":
    st.title("🌿 Substrate Formulation Optimizer")
    substrates = compute_substrate_comparison()
    df_sub = pd.DataFrame(substrates)
    fig_sub = go.Figure()
    fig_sub.add_trace(go.Bar(x=df_sub['substrate'], y=df_sub['be_typical'], name='Typical BE (%)',
                            marker_color='#10b981',
                            error_y=dict(type='data', symmetric=False,
                                        array=df_sub['be_max'] - df_sub['be_typical'],
                                        arrayminus=df_sub['be_typical'] - df_sub['be_min'])))
    fig_sub.update_layout(title="Biological Efficiency by Substrate", yaxis_title="BE (%)",
                         template="plotly_white", height=400)
    st.plotly_chart(fig_sub, use_container_width=True)

    price = st.slider("Mushroom sale price (฿/kg)", 30, 120, 45, 5, key="sub_price")
    roi_data = []
    for s in substrates:
        yield_kg = 585 * (s['be_typical'] / 100)
        revenue = yield_kg * price
        total_cost = sum(DEFAULT_COSTS.values()) + s['cost_per_rai']
        profit = revenue - total_cost
        roi_data.append({'Substrate': s['substrate'], 'Yield': round(yield_kg, 1),
                        'Revenue': round(revenue), 'Profit': round(profit), 'Notes': s['notes']})
    st.dataframe(pd.DataFrame(roi_data), use_container_width=True, hide_index=True)


# ================================================================
# LAB 5: SEASONAL PLANNER (ROUND 1)
# ================================================================
    render_references("🌿 Substrate Optimizer")

elif lab == "🗓️ Seasonal Planner":
    st.title("🗓️ Seasonal Cultivation Planner")
    region = st.radio("Region", ['isaan', 'central', 'chiang_mai'],
                      format_func=lambda x: {'isaan': 'Isaan (Northeast)', 'central': 'Central Plain', 'chiang_mai': 'Chiang Mai (North)'}[x],
                      horizontal=True)
    months = compute_seasonal_windows(region)
    df_m = pd.DataFrame(months)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_m['month'], y=df_m['avg_temp'], name='Temp (°C)', marker_color='#ef4444', opacity=0.7))
    fig.add_trace(go.Scatter(x=df_m['month'], y=df_m['mushroom_suitability'], mode='lines+markers',
                            name='Suitability', line=dict(color='#10b981', width=4), yaxis='y2'))
    fig.update_layout(title=f"Suitability — {'Isaan' if region == 'isaan' else 'Central Plain'}",
                     yaxis_title="Temp (°C)", yaxis2=dict(title="Suitability", overlaying='y', side='right'),
                     template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(4)
    for i, m in enumerate(months):
        with cols[i % 4]:
            st.markdown(f"**{m['month']}** {m['recommendation'].split(' ')[0]}\n- {m['avg_temp']}°C / {m['humidity']}% RH\n- {m['recommendation']}")


# ================================================================
# LAB 6: COMPETITIVE ANALYSIS (ROUND 1)
# ================================================================
    render_references("🗓️ Seasonal Planner")

elif lab == "⚔️ Competitive Analysis":
    st.title("⚔️ Competitive Analysis")
    comp = compute_competitive_comparison()
    df_comp = pd.DataFrame(comp)
    colors = ['#ef4444', '#10b981', '#f59e0b', '#6366f1', '#8b5cf6', '#6b7280']
    fig = go.Figure()
    for i, row in df_comp.iterrows():
        fig.add_trace(go.Bar(x=[row['method']], y=[row['net_impact_per_rai']],
                            marker_color=colors[i], text=f"฿{row['net_impact_per_rai']:,}", textposition='auto'))
    fig.add_hline(y=0, line_color="black", line_width=2)
    fig.update_layout(title="Net Economic Impact per Rai", yaxis_title="฿/rai",
                     template="plotly_white", height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    display_df = df_comp[['method', 'cost_per_rai', 'revenue_per_rai', 'net_impact_per_rai', 'time_days', 'equipment_cost', 'environmental']].copy()
    display_df.columns = ['Method', 'Cost/rai', 'Revenue/rai', 'Net Impact', 'Days', 'Equipment ฿', 'Environmental']
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ================================================================
# LAB 7: ADVANCED MONTE CARLO (ROUND 1)
# ================================================================
    render_references("⚔️ Competitive Analysis")

elif lab == "🎲 Advanced Monte Carlo":
    st.title("🎲 Advanced Monte Carlo with Seasonal & Contamination Risk")
    col1, col2 = st.columns([1, 2])
    with col1:
        n_sims = st.slider("Simulations", 1000, 50000, 10000, 1000)
        be_mean = st.slider("Mean BE (%)", 5, 20, 12) / 100
        be_std = st.slider("BE Std Dev (%)", 1, 8, 3) / 100
        price_mean = st.slider("Mean price (฿/kg)", 30, 120, 55, 5)
        price_std = st.slider("Price volatility (฿)", 5, 40, 15)
        contam = st.slider("Contamination risk (%)", 0, 30, 5) / 100
        st.divider()
        supplement = st.checkbox("Apply rice bran supplement (+30% BE)", value=True)
        if supplement:
            be_mean *= 1.30
            st.info(f"Adjusted mean BE: {be_mean*100:.1f}%")

    with col2:
        mc = monte_carlo_profit(n_sims, be_mean, be_std, price_mean, price_std, contamination_prob=contam)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("P(Profit)", f"{mc['prob_profitable']}%",
                  delta="Strong" if mc['prob_profitable'] > 85 else "Risky")
        k2.metric("Mean Profit", f"฿{mc['mean_profit']:,}")
        k3.metric("P5 (worst 5%)", f"฿{mc['p5']:,}")
        k4.metric("P95 (best 5%)", f"฿{mc['p95']:,}")

        profits = mc['profits']
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=profits, nbinsx=100,
                                  marker_color=np.where(profits >= 0, '#10b981', '#ef4444').tolist()))
        fig.add_vline(x=mc['mean_profit'], line_color="#f59e0b", annotation_text=f"Mean: ฿{mc['mean_profit']:,}")
        fig.add_vline(x=mc['p5'], line_dash="dot", line_color="#ef4444", annotation_text=f"P5: ฿{mc['p5']:,}")
        fig.add_vline(x=mc['p95'], line_dash="dot", line_color="#10b981", annotation_text=f"P95: ฿{mc['p95']:,}")
        fig.update_layout(title=f"Profit Distribution ({n_sims:,} runs)", xaxis_title="Net Profit (฿)",
                         yaxis_title="Frequency", template="plotly_dark", height=450)
        st.plotly_chart(fig, use_container_width=True)


# ================================================================
# ROUND 2 SEPARATOR
# ================================================================
elif lab == "─── Round 2: Biology ───":
    st.title("🧬 Round 2: Biological Science")
    st.markdown("""
    ### Research Areas
    | Lab | Focus | Key Question |
    |-----|-------|-------------|
    | 🧫 Spawn Rate | How much spawn per rai? | Optimal rate vs cost tradeoff |
    | 💧 Moisture | Soaking time vs BE | How long to soak rice straw? |
    | 🏠 Indoor/Outdoor | Environment comparison | Is shelter worth the cost? |
    | 👷 Harvest Labor | Labor cost per flush | Is Flush 3 worth picking? |
    """)


# ================================================================
# LAB 8: SPAWN RATE OPTIMIZER (ROUND 2)
# ================================================================
    render_references("🎲 Advanced Monte Carlo")

elif lab == "🧫 Spawn Rate Optimizer":
    st.title("🧫 Spawn Rate Optimization Lab")
    st.markdown("*Find the optimal spawn rate for maximum ROI — not too little (contamination), not too much (waste).*")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Parameters")
        substrate_kg = st.slider("Substrate per rai (kg)", 300, 800, 585, 25)
        spawn_cost = st.slider("Spawn cost (฿/kg)", 40, 200, 80, 10,
                              help="Grain spawn typically ฿60-100/kg in Thailand")

    with col2:
        spawn_data = compute_spawn_rate_optimization(substrate_kg, spawn_cost_per_kg=spawn_cost)
        df_spawn = pd.DataFrame(spawn_data)

        # Find optimal
        optimal = df_spawn.loc[df_spawn['profit_after_spawn'].idxmax()]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Optimal Rate", f"{optimal['spawn_rate_pct']}%")
        k2.metric("Spawn Cost", f"฿{optimal['spawn_cost_baht']:,.0f}")
        k3.metric("Colonization", f"{optimal['colonization_days']} days")
        k4.metric("Profit", f"฿{optimal['profit_after_spawn']:,.0f}", delta=f"ROI {optimal['roi_on_spawn']:.0f}×")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_spawn['spawn_rate_pct'], y=df_spawn['profit_after_spawn'],
                            name='Profit after spawn cost', marker_color='#10b981', opacity=0.7))
        fig.add_trace(go.Scatter(x=df_spawn['spawn_rate_pct'], y=df_spawn['colonization_days'],
                                mode='lines+markers', name='Colonization days',
                                line=dict(color='#ef4444', width=3), yaxis='y2'))
        fig.add_trace(go.Scatter(x=df_spawn['spawn_rate_pct'], y=df_spawn['contamination_risk_pct'],
                                mode='lines', name='Contamination risk %',
                                line=dict(color='#f59e0b', width=2, dash='dash'), yaxis='y2'))
        fig.update_layout(title="Spawn Rate vs Profit & Colonization Speed",
                         xaxis_title="Spawn Rate (%)", yaxis_title="Profit (฿)",
                         yaxis2=dict(title="Days / Risk %", overlaying='y', side='right'),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_spawn[['spawn_rate_pct', 'spawn_kg', 'spawn_cost_baht', 'colonization_days',
                               'effective_be_pct', 'yield_kg', 'profit_after_spawn', 'recommendation']],
                     use_container_width=True, hide_index=True)

        st.success(f"🎯 **Sweet spot: 2-5% spawn rate** — fast colonization, low contamination risk, best profit/spawn-cost ratio.")


# ================================================================
# LAB 9: MOISTURE & SOAKING (ROUND 2)
# ================================================================
    render_references("🧫 Spawn Rate Optimizer")

elif lab == "💧 Moisture & Soaking":
    st.title("💧 Moisture Content & Soaking Optimization")
    st.markdown("*The #1 beginner mistake: too wet or too dry substrate. Find the sweet spot.*")

    moisture_data = compute_moisture_optimization()
    df_moisture = pd.DataFrame(moisture_data['moisture_curve'])
    df_soak = pd.DataFrame(moisture_data['soak_curve'])

    tab1, tab2 = st.tabs(["Moisture vs BE", "Soaking Time"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_moisture['moisture_pct'], y=df_moisture['effective_be_pct'],
                                mode='lines', name='Effective BE (%)',
                                line=dict(color='#10b981', width=3), fill='tozeroy',
                                fillcolor='rgba(16,185,129,0.1)'))
        fig.add_trace(go.Scatter(x=df_moisture['moisture_pct'], y=df_moisture['contamination_risk_pct'],
                                mode='lines', name='Contamination risk (%)',
                                line=dict(color='#ef4444', width=2, dash='dash'), yaxis='y2'))
        fig.add_vrect(x0=55, x1=67, fillcolor='#10b981', opacity=0.1, annotation_text="OPTIMAL ZONE")
        fig.update_layout(title="How Moisture Content Affects Yield",
                         xaxis_title="Substrate Moisture (%)", yaxis_title="Effective BE (%)",
                         yaxis2=dict(title="Contamination Risk (%)", overlaying='y', side='right'),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Optimal range: 55-67% moisture.** Peak BE at 62%. Above 70% → anaerobic bacteria thrive.")

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_soak['soak_hours'], y=df_soak['final_moisture_pct'],
                                 mode='lines+markers', name='Final moisture',
                                 line=dict(color='#3b82f6', width=3)))
        fig2.add_hrect(y0=58, y1=65, fillcolor='#10b981', opacity=0.1, annotation_text="OPTIMAL")
        fig2.update_layout(title="Soaking Time vs Final Moisture Content",
                          xaxis_title="Soaking Time (hours)", yaxis_title="Final Moisture (%)",
                          template="plotly_white", height=350)
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(df_soak, use_container_width=True, hide_index=True)
        st.success("🎯 **12-24 hours soaking** achieves optimal 58-65% moisture. Squeeze-test: damp but no dripping.")


# ================================================================
# LAB 10: INDOOR VS OUTDOOR (ROUND 2)
# ================================================================
    render_references("💧 Moisture & Soaking")

elif lab == "🏠 Indoor vs Outdoor":
    st.title("🏠 Indoor vs Outdoor Cultivation Comparison")
    st.markdown("*Research shows indoor yields are 2.7-3× outdoor. But is the investment worth it?*")

    grow_area = st.slider("Growing area (m²)", 5, 100, 20, 5)
    scenarios = compute_indoor_outdoor_comparison(grow_area_m2=grow_area)
    df_io = pd.DataFrame(scenarios)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Best Annual Profit", f"฿{max(s['annual_profit'] for s in scenarios):,.0f}")
    k2.metric("Best Yield/m²", f"{max(s['yield_per_m2'] for s in scenarios)} kg/m²")
    k3.metric("Lowest Risk", f"{min(s['contamination_risk_pct'] for s in scenarios)}%")
    k4.metric("Most Cycles/yr", f"{max(s['cycles_per_year'] for s in scenarios)}")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_io['method'], y=df_io['annual_profit'],
                        name='Annual Profit ฿', marker_color='#10b981'))
    fig.add_trace(go.Scatter(x=df_io['method'], y=df_io['setup_cost'],
                            mode='lines+markers', name='Setup Cost ฿',
                            line=dict(color='#ef4444', width=3), yaxis='y2'))
    fig.update_layout(title="Annual Profit vs Setup Cost", yaxis_title="Annual Profit (฿)",
                     yaxis2=dict(title="Setup Cost (฿)", overlaying='y', side='right'),
                     template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_io[['method', 'yield_per_m2', 'be_pct', 'setup_cost', 'cycles_per_year',
                        'annual_yield_kg', 'annual_profit', 'payback_cycles', 'contamination_risk_pct']],
                 use_container_width=True, hide_index=True)
    st.success("🎯 **For Thai farmers: Polyhouse is the best ROI** — 8 cycles/year, manageable ฿25k investment, only 10% contamination risk.")


# ================================================================
# LAB 11: HARVEST LABOR MODEL (ROUND 2)
# ================================================================
    render_references("🏠 Indoor vs Outdoor")

elif lab == "👷 Harvest Labor Model":
    st.title("👷 Harvest Labor Cost Analysis")
    st.markdown("*Is it worth harvesting Flush 3? How much labor is needed per flush?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        total_yield = st.slider("Total mushroom yield (kg)", 20, 120, 57, 5)
        labor_rate = st.slider("Daily labor rate (฿)", 200, 600, 350, 25,
                              help="Thai minimum wage ~350 ฿/day in Isaan")
        flushes = st.slider("Number of flushes to harvest", 1, 3, 3)

    with col2:
        labor_data = compute_harvest_labor_model(total_yield, flushes, labor_rate)
        df_labor = pd.DataFrame(labor_data)

        total_profit = sum(f['flush_profit'] for f in labor_data)
        total_labor_cost = sum(f['labor_cost_baht'] for f in labor_data)
        total_revenue = sum(f['revenue_baht'] for f in labor_data)

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Revenue", f"฿{total_revenue:,.0f}")
        k2.metric("Total Labor Cost", f"฿{total_labor_cost:,.0f}")
        k3.metric("Net Profit (labor)", f"฿{total_profit:,.0f}")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=[f"Flush {f['flush']}" for f in labor_data],
                            y=[f['revenue_baht'] for f in labor_data],
                            name='Revenue', marker_color='#10b981'))
        fig.add_trace(go.Bar(x=[f"Flush {f['flush']}" for f in labor_data],
                            y=[f['labor_cost_baht'] for f in labor_data],
                            name='Labor Cost', marker_color='#ef4444'))
        fig.update_layout(title="Revenue vs Labor Cost per Flush", barmode='group',
                         yaxis_title="฿", template="plotly_white", height=350)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_labor, use_container_width=True, hide_index=True)

        flush3 = [f for f in labor_data if f['flush'] == 3]
        if flush3:
            if flush3[0]['worth_harvesting']:
                st.success(f"✅ Flush 3 WORTH harvesting: ฿{flush3[0]['flush_profit']:,.0f} profit")
            else:
                st.warning(f"⚠️ Flush 3 NOT worth harvesting: ฿{flush3[0]['flush_profit']:,.0f} loss. Skip it unless family labor (free).")


# ================================================================
# ROUND 3 SEPARATOR
# ================================================================
elif lab == "─── Round 3: Environment ───":
    st.title("🌍 Round 3: Environmental Factors")
    st.markdown("""
    | Lab | Focus | Key Question |
    |-----|-------|-------------|
    | 🌾 Straw Degradation | Nutrient loss over storage | How fast does straw quality decline? |
    | 🌡️ Temperature Corridor | Shelter vs ambient | Can a plastic house extend the growing season? |
    """)


# ================================================================
# LAB 12: STRAW DEGRADATION (ROUND 3)
# ================================================================
    render_references("👷 Harvest Labor Model")

elif lab == "🌾 Straw Degradation":
    st.title("🌾 Rice Straw Storage Degradation")
    st.markdown("*Straw loses nutrients every week. Fresh is best — but how long is 'acceptable'?*")

    storage = st.selectbox("Storage method", ['open_field', 'covered_pile', 'baled_covered', 'indoor_dry'],
                          format_func=lambda x: {'open_field': '🔴 Open field (worst)',
                                                 'covered_pile': '🟡 Covered pile',
                                                 'baled_covered': '🟢 Baled & covered',
                                                 'indoor_dry': '🟢 Indoor dry (best)'}[x])

    degradation = compute_straw_degradation(storage_type=storage)
    df_deg = pd.DataFrame(degradation)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_deg['weeks'], y=df_deg['cellulose_pct'], mode='lines',
                            name='Cellulose', line=dict(color='#10b981', width=3)))
    fig.add_trace(go.Scatter(x=df_deg['weeks'], y=df_deg['hemicellulose_pct'], mode='lines',
                            name='Hemicellulose', line=dict(color='#f59e0b', width=2)))
    fig.add_trace(go.Scatter(x=df_deg['weeks'], y=df_deg['potassium_pct'], mode='lines',
                            name='Potassium', line=dict(color='#ef4444', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df_deg['weeks'], y=df_deg['be_quality_pct'], mode='lines',
                            name='BE Quality (yield impact)', line=dict(color='#3b82f6', width=4)))
    fig.add_hrect(y0=75, y1=100, fillcolor='#10b981', opacity=0.05, annotation_text="GOOD for mushrooms")
    fig.update_layout(title=f"Nutrient Degradation — {storage.replace('_', ' ').title()}",
                     xaxis_title="Weeks Stored", yaxis_title="% Remaining",
                     template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

    # Find storage window
    acceptable = [d for d in degradation if d['be_quality_pct'] >= 75]
    max_weeks = acceptable[-1]['weeks'] if acceptable else 0
    st.metric("Maximum acceptable storage time", f"{max_weeks} weeks")
    st.info(f"💡 **Potassium is lost fastest** — 93.5% in first month for open storage. Use stored straw within {max_weeks} weeks or supplement with potassium-rich additives.")


# ================================================================
# LAB 13: TEMPERATURE CORRIDOR (ROUND 3)
# ================================================================
    render_references("🌾 Straw Degradation")

elif lab == "🌡️ Temperature Corridor":
    st.title("🌡️ Temperature Corridor Analysis")
    st.markdown("*Can shelters extend the growing season by modifying temperature?*")

    shelters = ['none', 'shade_cloth', 'plastic_house', 'indoor']
    labels = {'none': 'No shelter', 'shade_cloth': 'Shade cloth', 'plastic_house': 'Plastic house', 'indoor': 'Indoor (controlled)'}

    fig = go.Figure()
    colors = ['#6b7280', '#f59e0b', '#10b981', '#3b82f6']
    for i, shelter in enumerate(shelters):
        data = compute_temperature_corridor(shelter_type=shelter)
        df = pd.DataFrame(data)
        fig.add_trace(go.Scatter(x=df['ambient_c'], y=df['growth_pct'], mode='lines',
                                name=labels[shelter], line=dict(color=colors[i], width=3 if i > 0 else 1)))

    fig.add_vrect(x0=25, x1=38, fillcolor='#10b981', opacity=0.05, annotation_text="V. volvacea viable range")
    fig.add_hline(y=70, line_dash="dash", line_color="#10b981", annotation_text="70% = good growth")
    fig.update_layout(title="Growth Factor vs Ambient Temperature by Shelter Type",
                     xaxis_title="Ambient Temperature (°C)", yaxis_title="Growth Factor (%)",
                     template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    ### Key Findings
    - **Plastic house** extends viable range down to ~21°C (adds +4°C greenhouse effect)
    - **Shade cloth** reduces peak temperatures by 2-3°C (helps in hot season)
    - **Indoor controlled** is always optimal but costly
    - For Isaan's cool season (Dec-Jan: 23-24°C), a **plastic house makes the difference** between failure and success
    """)


# ================================================================
# ROUND 4 SEPARATOR
# ================================================================
elif lab == "─── Round 4: Economics ───":
    st.title("💰 Round 4: Advanced Economics")
    st.markdown("""
    | Lab | Focus | Key Question |
    |-----|-------|-------------|
    | 🤝 Cooperative | Equipment sharing | How much cheaper if farmers share? |
    | 🏪 Market | Local absorption | Can markets handle the supply? |
    | 📅 Year-Round | Multi-cycle planning | How many cycles per year? |
    """)


# ================================================================
# LAB 14: COOPERATIVE MODEL (ROUND 4)
# ================================================================
    render_references("🌡️ Temperature Corridor")

elif lab == "🤝 Cooperative Model":
    st.title("🤝 Village Cooperative Economics")
    st.markdown("*Share the boiler, save 50%+ on investment. Based on Thai BAAC cooperative lending data.*")

    col1, col2 = st.columns([1, 2])
    with col1:
        num_farmers = st.slider("Farmers in cooperative", 3, 30, 10, 1)
        rai_per_farmer = st.slider("Rai per farmer", 5, 40, 15, 5)

    with col2:
        coop = compute_cooperative_model(num_farmers, rai_per_farmer)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Individual Cost", f"฿{coop['individual']['equipment_cost']:,.0f}")
        k2.metric("Co-op Cost/farmer", f"฿{coop['cooperative']['per_farmer_cost']:,.0f}",
                  delta=f"Save {coop['cooperative']['savings_pct']}%")
        k3.metric("Co-op Payback", f"{coop['cooperative']['payback_years']} yrs")
        k4.metric("Monthly Payment", f"฿{coop['cooperative']['monthly_payment']:,.0f}",
                  delta=f"BAAC 4.5% rate")

        # Comparison bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['Equipment Cost/Farmer', 'Monthly Loan Payment', 'Payback Period (months)'],
                            y=[coop['individual']['equipment_cost'], coop['individual']['monthly_payment'],
                               coop['individual']['payback_years'] * 12],
                            name='Individual', marker_color='#ef4444'))
        fig.add_trace(go.Bar(x=['Equipment Cost/Farmer', 'Monthly Loan Payment', 'Payback Period (months)'],
                            y=[coop['cooperative']['per_farmer_cost'], coop['cooperative']['monthly_payment'],
                               coop['cooperative']['payback_years'] * 12],
                            name='Cooperative', marker_color='#10b981'))
        fig.update_layout(title="Individual vs Cooperative Economics", barmode='group',
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        ### Village Impact ({num_farmers} farmers × {rai_per_farmer} rai)
        | Metric | Value |
        |--------|-------|
        | Total rai | {coop['total_village']['total_rai']} |
        | Village savings | ฿{coop['total_village']['village_savings']:,} |
        | Annual village profit | ฿{coop['total_village']['annual_village_profit']:,} |
        | Monthly mushroom output | {coop['total_village']['monthly_mushroom_kg']:,} kg |
        """)


# ================================================================
# LAB 15: MARKET ABSORPTION (ROUND 4)
# ================================================================
    render_references("🤝 Cooperative Model")

elif lab == "🏪 Market Absorption":
    st.title("🏪 Market Absorption Analysis")
    st.markdown("*Can local markets absorb your mushroom production? Where to sell for best price?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        monthly_kg = st.slider("Monthly production (kg)", 50, 2000, 500, 50)
        village_pop = st.slider("Village population", 100, 2000, 500, 100)
        nearby = st.slider("Nearby villages", 1, 10, 3)
        town_pop = st.slider("Market town population", 1000, 20000, 5000, 500)

    with col2:
        market = compute_market_absorption(monthly_kg, village_pop, nearby, town_pop)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Local Demand", f"{market['local_demand_kg_month']:,.0f} kg/mo")
        k2.metric("Absorption", f"{market['absorption_pct']:.0f}%")
        k3.metric("Blended Price", f"฿{market['blended_price_per_kg']:.0f}/kg")
        k4.metric("Status", market['market_status'].split(' ', 1)[1] if ' ' in market['market_status'] else market['market_status'])

        # Channel allocation
        alloc = market['optimal_allocation']
        df_alloc = pd.DataFrame(alloc)
        fig = go.Figure()
        colors_ch = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#6b7280']
        fig.add_trace(go.Bar(x=df_alloc['channel'], y=df_alloc['allocated_kg'],
                            name='Allocated kg', marker_color=colors_ch[:len(df_alloc)]))
        fig.add_trace(go.Scatter(x=df_alloc['channel'], y=df_alloc['price_per_kg'],
                                mode='lines+markers', name='Price ฿/kg',
                                line=dict(color='#ef4444', width=3), yaxis='y2'))
        fig.update_layout(title="Optimal Sales Channel Allocation",
                         yaxis_title="kg allocated", yaxis2=dict(title="Price ฿/kg", overlaying='y', side='right'),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Total Monthly Revenue", f"฿{market['total_monthly_revenue']:,}")
        st.info(f"💡 **Sell to village market first** (highest price ฿60/kg), then nearby markets, then wholesale. "
               f"Cannery is last resort at ฿15/kg but guaranteed volume.")


# ================================================================
# LAB 16: YEAR-ROUND PLANNER (ROUND 4)
# ================================================================
elif lab == "📅 Year-Round Planner":
    st.title("📅 Year-Round Operations Planner")
    st.markdown("*How many cycles can you run per year with stored straw?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        rai = st.slider("Available rai", 5, 40, 15, 5)
        region = st.selectbox("Region", ['isaan', 'central', 'chiang_mai'],
                             format_func=lambda x: {'isaan': 'Isaan (Northeast)', 'central': 'Central Plain', 'chiang_mai': 'Chiang Mai (North)'}[x])

    with col2:
        ops = compute_year_round_operations(rai, region)
        df_ops = pd.DataFrame(ops)

        summary = ops[0]  # all rows have summary
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Cycles/yr", f"{summary['total_cycles']}")
        k2.metric("Annual Yield", f"{summary['annual_total_yield']:,.0f} kg")
        k3.metric("Annual Revenue", f"฿{summary['annual_total_revenue']:,.0f}")
        k4.metric("Annual Profit", f"฿{summary['annual_total_profit']:,.0f}")

        fig = go.Figure()
        grow_months = [r['month'] for r in ops if r['can_grow']]
        no_grow = [r['month'] for r in ops if not r['can_grow']]

        fig.add_trace(go.Bar(x=df_ops['month'], y=df_ops['monthly_yield_kg'],
                            name='Monthly Yield (kg)', marker_color=df_ops['can_grow'].map({True: '#10b981', False: '#ef4444'})))
        fig.add_trace(go.Scatter(x=df_ops['month'], y=df_ops['monthly_revenue'],
                                mode='lines+markers', name='Revenue ฿', yaxis='y2',
                                line=dict(color='#f59e0b', width=3)))
        fig.update_layout(title=f"Year-Round Production — {region.title()} ({rai} rai)",
                         xaxis_title="Month", yaxis_title="Yield (kg)",
                         yaxis2=dict(title="Revenue (฿)", overlaying='y', side='right'),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_ops[['month', 'avg_temp', 'can_grow', 'straw_source', 'cycles', 'monthly_yield_kg', 'monthly_revenue']],
                     use_container_width=True, hide_index=True)

        st.success(f"🎯 With stored straw: **{summary['total_cycles']} cycles/year** in {region.title()}, "
                  f"generating **฿{summary['annual_total_profit']:,.0f} annual profit** from {rai} rai.")


# ================================================================
# ROUND 5 SEPARATOR
# ================================================================
elif lab == "─── Round 5: Technology ───":
    st.title("🔧 Round 5: Technology & Scale")
    st.markdown("""
    | Lab | Focus | Key Question |
    |-----|-------|-------------|
    | 🌍 Carbon Credits | T-VER pricing & MRV | Is carbon credit revenue viable at village scale? |
    | 📡 IoT Monitoring | Sensor + gateway BOM | How much does automated MRV cost? |
    | 🚜 Tractor Ops | Scheduling & capacity | How many tractors serve 150 rai in 14 days? |
    | 🤖 Autonomous ROI | Manual → GPS → Autonomous | When does automation pay for itself? |
    """)


# ================================================================
# LAB 17: CARBON CREDITS (ROUND 5)
# ================================================================
    render_references("🏪 Market Absorption")

elif lab == "🌍 Carbon Credits (T-VER)":
    st.title("🌍 Carbon Credit Integration (T-VER)")
    st.markdown("*Thailand Voluntary Emission Reduction program — IPCC methodology, only CH₄ + N₂O count.*")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Parameters")
        n_rai = st.slider("Rai per farmer", 5, 40, 15, 5)
        coop_size = st.slider("Cooperative size", 3, 30, 10)
        carbon_price = st.slider("T-VER price (฿/tCO₂eq)", 50, 2100, 175, 25,
                                help="Avg Q1 FY2025: ฿175. Ag sector: ฿300-2,076")
        st.divider()
        include_bc = st.checkbox("Include black carbon", help="Short-lived climate forcer — requires special TGO methodology")
        include_soil = st.checkbox("Include soil carbon", help="SMS incorporation sequesters carbon — requires soil sampling")
        verification = st.radio("MRV method", ['iot', 'manual', 'satellite'],
                               format_func=lambda x: {'iot': '📡 IoT (recommended)', 'manual': '📋 Manual', 'satellite': '🛰 Satellite'}[x])

    with col2:
        cc = compute_carbon_credits_v2(n_rai, carbon_price, cooperative_size=coop_size,
                                       include_black_carbon=include_bc, include_soil_carbon=include_soil,
                                       verification_method=verification)
        per_rai = cc['per_rai']
        coop = cc['cooperative']

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("CO₂eq per rai", f"{per_rai['total_co2eq_kg']:.1f} kg")
        k2.metric("Coop total", f"{coop['total_tco2eq']:.1f} tCO₂eq")
        k3.metric("Net revenue", f"฿{coop['net_revenue']:,}")
        k4.metric("Per farmer", f"฿{coop['revenue_per_farmer']:,}/yr")

        # Price tier comparison
        df_tiers = pd.DataFrame(cc['price_scenarios'])
        fig = go.Figure()
        colors = ['#ef4444' if not v else '#10b981' for v in df_tiers['viable']]
        fig.add_trace(go.Bar(x=df_tiers['tier'], y=df_tiers['net_revenue'],
                            marker_color=colors, text=df_tiers['net_revenue'].apply(lambda x: f"฿{x:,}"),
                            textposition='auto'))
        fig.add_hline(y=0, line_color='black', line_width=2)
        fig.update_layout(title="Net Carbon Revenue by T-VER Price Tier",
                         yaxis_title="Net Revenue (฿)", template="plotly_white", height=350)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_tiers[['tier', 'price_per_tco2eq', 'gross_revenue', 'net_revenue', 'per_rai', 'viable']],
                     use_container_width=True, hide_index=True)

        st.info(f"💡 **{cc['methodology_note']}**\n\n"
               f"Verification cost ({verification}): ฿{coop['verification_cost']:,}/yr. "
               f"At avg T-VER price (฿175), carbon credits are a **cooperative-level bonus**, not the primary revenue driver.")

        if include_bc:
            st.warning("⚠️ Black carbon counting requires specialized TGO methodology (not yet standard for T-VER). "
                      "Could increase credits 5× but needs Phase 3 regulatory engagement.")


# ================================================================
# LAB 18: IoT MONITORING (ROUND 5)
# ================================================================
    render_references("🌍 Carbon Credits (T-VER)")

elif lab == "📡 IoT Monitoring & MRV":
    st.title("📡 IoT Monitoring & MRV System")
    st.markdown("*Automated data collection for carbon credit verification and process optimization.*")

    col1, col2 = st.columns([1, 2])
    with col1:
        num_nodes = st.slider("Sensor nodes", 1, 20, 5, 1)
        gateway = st.radio("Communication", ['lora', 'wifi', '4g'],
                          format_func=lambda x: {'lora': '📡 LoRa (recommended)', 'wifi': '📶 WiFi (short range)',
                                                  '4g': '📱 4G (no gateway)'}[x])

    with col2:
        iot = compute_iot_monitoring(num_nodes, gateway)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Node cost", f"฿{iot['node_cost']:,}")
        k2.metric("Hardware total", f"฿{iot['hardware_total']:,}")
        k3.metric("Annual operating", f"฿{iot['annual_operating']:,}/yr")
        k4.metric("MRV savings", f"฿{iot['mrv_savings_annual']:,}/yr",
                  delta=f"Payback {iot['payback_months']} mo" if iot['payback_months'] < 999 else "N/A")

        tab1, tab2, tab3 = st.tabs(["Sensor BOM", "Data Quality", "Architecture"])

        with tab1:
            bom_df = pd.DataFrame([{'Component': k, 'Cost (฿)': v} for k, v in iot['node_bom'].items()])
            fig_bom = go.Figure(data=[go.Pie(labels=bom_df['Component'], values=bom_df['Cost (฿)'],
                                            hole=0.4, textinfo='label+value')])
            fig_bom.update_layout(title=f"Sensor Node BOM — ฿{iot['node_cost']:,}/node × {num_nodes} = ฿{iot['total_nodes_cost']:,}",
                                 template="plotly_white", height=400)
            st.plotly_chart(fig_bom, use_container_width=True)

        with tab2:
            comparison_df = pd.DataFrame(iot['data_comparison'])
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            st.success(f"📡 IoT provides **2,016× more data points** than manual logging, "
                      f"with ±0.5°C accuracy and cryptographic tamper-proofing for MRV compliance.")

        with tab3:
            st.markdown(f"""
            ### System Architecture
            ```
            [Sensor Node] ──── [{gateway.upper()}] ──── [LoRa Gateway] ──── [Cloud]
                │                                              │
                ├── DHT22 (temp/humidity)                      ├── MQTT Broker
                ├── PT100 (steam temp)                         ├── TimescaleDB
                ├── NEO-6M (GPS)                               ├── Grafana Dashboard
                └── Flow meter                                 └── T-VER Report Generator
            ```
            
            | Component | Cost | Notes |
            |-----------|------|-------|
            | {num_nodes} sensor nodes | ฿{iot['total_nodes_cost']:,} | Solar-powered, weatherproof |
            | Gateway ({gateway}) | ฿{iot['gateway_cost']:,} | {'10km range' if gateway == 'lora' else '50m range' if gateway == 'wifi' else 'Cellular'} |
            | Dashboard setup | ฿3,000 | One-time Grafana config |
            | **Total hardware** | **฿{iot['hardware_total']:,}** | 3-year amortization |
            | Monthly data costs | ฿{iot['monthly_operating']:,} | Cloud + data |
            """)


# ================================================================
# LAB 19: TRACTOR OPERATIONS (ROUND 5)
# ================================================================
    render_references("📡 IoT Monitoring & MRV")

elif lab == "🚜 Tractor Operations":
    st.title("🚜 Tractor Operations & Scheduling")
    st.markdown("*How many tractors are needed to treat the entire cooperative within the 14-day window?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        total_rai = st.slider("Total cooperative rai", 50, 500, 150, 25)
        num_tractors = st.slider("Number of tractors", 1, 5, 1)
        window = st.slider("Treatment window (days)", 7, 30, 14, 1)
        st.divider()
        treatment_time = st.slider("Treatment time (min/rai)", 30, 90, 45, 5)
        travel_time = st.slider("Travel time (min/rai)", 5, 30, 15, 5)

    with col2:
        tractor = compute_tractor_operations(total_rai, num_tractors,
                                             treatment_time_per_rai_min=treatment_time,
                                             travel_time_per_rai_min=travel_time,
                                             treatment_window_days=window)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Rai/day", f"{tractor['rai_per_day']}")
        k2.metric("Days needed", f"{tractor['days_needed']}", delta="ON TIME" if tractor['days_needed'] <= window else "⚠️ OVER",
                  delta_color="normal" if tractor['days_needed'] <= window else "inverse")
        k3.metric("Coverage", f"{tractor['coverage_pct']}%")
        k4.metric("Cost/rai", f"฿{tractor['cost_per_rai']}")

        if tractor['coverage_pct'] < 100:
            st.warning(f"⚠️ Need **{tractor['tractors_needed']} tractors** to cover all {total_rai} rai in {window} days. "
                      f"Currently {num_tractors} tractor(s) can only cover {tractor['coverage_pct']:.0f}%.")

        # Schedule chart
        df_sched = pd.DataFrame(tractor['schedule'])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_sched['day'], y=df_sched['rai_treated'],
                            name='Daily rai treated', marker_color='#10b981'))
        fig.add_trace(go.Scatter(x=df_sched['day'], y=df_sched['pct_complete'],
                                mode='lines+markers', name='% Complete', yaxis='y2',
                                line=dict(color='#3b82f6', width=3)))
        fig.add_shape(type="line", x0=df_sched['day'].iloc[0], x1=df_sched['day'].iloc[-1],
                      y0=100, y1=100, yref='y2', line=dict(dash="dash", color="#10b981"))
        fig.update_layout(title=f"Treatment Schedule — {num_tractors} tractor(s), {total_rai} rai",
                         xaxis_title="Day", yaxis_title="Rai/day",
                         yaxis2=dict(title="% Complete", overlaying='y', side='right', range=[0, 110]),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | Operating cost | ฿{tractor['total_operating_cost']:,} |
        | Fuel cost | ฿{tractor['fuel_total']:,} |
        | Operator wages | ฿{tractor['operator_total']:,} |
        | Equipment (amortized) | ฿{tractor['equipment_amortized']:,} |
        | **Mushroom revenue** | **฿{tractor['mushroom_revenue_total']:,}** |
        | **Net profit** | **฿{tractor['net_profit']:,}** |
        """)


# ================================================================
# LAB 20: AUTONOMOUS TRACTOR ROI (ROUND 5)
# ================================================================
    render_references("🚜 Tractor Operations")

elif lab == "🤖 Autonomous Tractor ROI":
    st.title("🤖 Autonomous Tractor ROI Analysis")
    st.markdown("*From manual operation → GPS auto-steer → semi-autonomous → fully autonomous. When does automation pay?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        total_rai = st.slider("Cooperative total rai", 50, 500, 150, 25, key="auto_rai")
        coop_size = st.slider("Farmers in cooperative", 3, 30, 10, key="auto_coop")
        gps_cost = st.slider("GPS auto-steer kit (฿)", 20000, 80000, 35000, 5000,
                            help="Chinese-made: ฿30k. Kubota/Topcon RTK: ฿220k")
        autonomous_cost = st.slider("Full autonomous upgrade (฿)", 100000, 500000, 250000, 25000,
                                   help="Concept pricing — expected to decrease by 2027")

    with col2:
        auto = compute_autonomous_tractor_roi(total_rai, coop_size,
                                              gps_autosteer_cost=gps_cost,
                                              full_autonomous_cost=autonomous_cost)
        df_auto = pd.DataFrame(auto)

        # Key comparison
        best = min(auto, key=lambda x: x['payback_years'])
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Best payback", f"{best['payback_years']} yrs", delta=best['mode'])
        k2.metric("GPS rai/day", f"{auto[1]['effective_rai_per_day']}", delta=f"+{auto[1]['effective_rai_per_day'] - auto[0]['effective_rai_per_day']:.0f} vs manual")
        k3.metric("Fully auto rai/day", f"{auto[3]['effective_rai_per_day']}", delta=f"+{auto[3]['effective_rai_per_day'] - auto[0]['effective_rai_per_day']:.0f} vs manual")
        k4.metric("Labor savings (auto)", f"{auto[3]['labor_savings_pct']}%")

        tab1, tab2 = st.tabs(["Investment & Profit", "Efficiency"])

        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_auto['mode'], y=df_auto['total_investment'],
                                name='Total Investment', marker_color='#ef4444'))
            fig.add_trace(go.Bar(x=df_auto['mode'], y=df_auto['annual_profit'],
                                name='Annual Profit', marker_color='#10b981'))
            fig.update_layout(title="Investment vs Annual Profit", barmode='group',
                             yaxis_title="฿", template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df_auto['mode'], y=df_auto['effective_rai_per_day'],
                                 name='Effective rai/day', marker_color='#3b82f6'))
            fig2.add_trace(go.Scatter(x=df_auto['mode'], y=df_auto['overlap_waste_pct'],
                                     mode='lines+markers', name='Overlap waste %',
                                     line=dict(color='#f59e0b', width=3), yaxis='y2'))
            fig2.update_layout(title="Treatment Speed & Efficiency",
                             yaxis_title="Rai/day", yaxis2=dict(title="Overlap waste %", overlaying='y', side='right'),
                             template="plotly_white", height=400)
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df_auto[['mode', 'per_farmer_cost', 'effective_rai_per_day', 'days_to_treat_coop',
                              'annual_operating', 'annual_profit', 'payback_years', 'fuel_savings_pct',
                              'labor_savings_pct', 'overlap_waste_pct']],
                     use_container_width=True, hide_index=True)

        st.success(f"🎯 **GPS auto-steer is the sweet spot** — ฿{auto[1]['per_farmer_cost']:,}/farmer, "
                  f"{auto[1]['payback_years']} yr payback, 30% labor savings. "
                  f"Full autonomous interesting but costs fall by ~2027.")


# ================================================================
# ROUND 6 SEPARATOR
# ================================================================
elif lab == "─── Round 6: Risk Validation ───":
    st.title("⚠️ Round 6: Risk Validation")
    st.markdown("""
    These labs address the **5 things we haven't field-tested** yet. 
    Each lab stress-tests a critical assumption with Monte Carlo simulation or scenario analysis.
    
    | Lab | Risk Factor | What Could Go Wrong? |
    |-----|-------------|---------------------|
    | 🧪 Contamination | Trichoderma, bacteria | Yield loss 40-100% per contaminated batch |
    | 📉 Market Saturation | Oversupply | Price crash if multiple coops produce simultaneously |
    | 🌾 Rice Variety | Straw quality | KDML105 vs RD6 may give different mushroom yields |
    | 📈 Adoption | Farmer willingness | Older farmers resist new tech, slow uptake |
    | 🎯 Sensitivity | All variables | Which factor kills profitability fastest? |
    """)


# ================================================================
# LAB 21: CONTAMINATION STRESS TEST (ROUND 6)
# ================================================================
    render_references("🤖 Autonomous Tractor ROI")

elif lab == "🧪 Contamination Stress Test":
    st.title("🧪 Contamination Stress Test")
    st.markdown("*What happens when Trichoderma or bacteria get into the substrate under real field conditions?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Conditions")
        steam_temp = st.slider("Steam temperature (°C)", 60, 140, 120, 10)
        sanitation = st.radio("Sanitation protocol", ['strict', 'standard', 'none'],
                             format_func=lambda x: {'strict': '🧤 Strict (gloves, clean tools, foot bath)',
                                                     'standard': '👐 Standard (basic cleaning)',
                                                     'none': '❌ None (field as-is)'}[x])
        spawn_q = st.radio("Spawn quality", ['certified', 'local', 'unknown'],
                           format_func=lambda x: {'certified': '✅ Certified lab spawn',
                                                    'local': '🏪 Local spawn supplier',
                                                    'unknown': '❓ Unknown source'}[x])
        environment = st.radio("Growing environment", ['outdoor', 'shade_cloth', 'polyhouse', 'indoor'],
                              format_func=lambda x: {'outdoor': '☀️ Outdoor',
                                                      'shade_cloth': '🏕 Shade cloth',
                                                      'polyhouse': '🏠 Polyhouse',
                                                      'indoor': '🏭 Indoor controlled'}[x])

    with col2:
        ct = compute_contamination_stress_test(steam_temp, sanitation, spawn_q, environment)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Contamination rate", f"{ct['effective_rate']}%")
        k2.metric("Mean profit/rai", f"฿{ct['mean_profit']:,}")
        k3.metric("Prob profitable", f"{ct['prob_profitable']}%")
        k4.metric("Worst case", f"฿{ct['worst_case']:,}")

        # Profit distribution
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=ct['profits'], nbinsx=50, marker_color='#3b82f6',
                                   name='Profit distribution'))
        fig.add_vline(x=0, line_color='red', line_width=2, annotation_text="Break-even")
        fig.add_vline(x=ct['mean_profit'], line_color='green', line_dash='dash',
                     annotation_text=f"Mean: ฿{ct['mean_profit']:,}")
        fig.update_layout(title=f"Profit Distribution — {ct['n_simulations']:,} simulations",
                         xaxis_title="Profit per rai (฿)", yaxis_title="Frequency",
                         template="plotly_white", height=350)
        st.plotly_chart(fig, use_container_width=True)

        # Scenario matrix
        st.subheader("📊 Environment × Sanitation Matrix")
        df_scen = pd.DataFrame(ct['scenario_matrix'])
        fig2 = px.scatter(df_scen, x='contamination_rate', y='expected_profit',
                         color='environment', symbol='sanitation', size='expected_yield',
                         labels={'contamination_rate': 'Contamination Rate (%)',
                                'expected_profit': 'Expected Profit (฿/rai)'},
                         title="Contamination Rate vs Profit by Setup")
        fig2.add_hline(y=0, line_color='red', line_dash='dash')
        fig2.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig2, use_container_width=True)

        st.info("🧬 **Key insight**: With polyhouse + standard sanitation + certified spawn, "
               "contamination stays below 3% and **97%+ batches are profitable**. "
               "Skip any one of these → risk jumps 3-5× .")


# ================================================================
# LAB 22: MARKET SATURATION (ROUND 6)
# ================================================================
    render_references("🧪 Contamination Stress Test")

elif lab == "📉 Market Saturation":
    st.title("📉 Market Saturation Analysis")
    st.markdown("*What happens when 5, 10, or 20 cooperatives start producing simultaneously?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        n_coops = st.slider("Max cooperatives to model", 2, 20, 10)
        prod_per_coop = st.slider("Monthly production per coop (kg)", 200, 2000, 500, 100)
        st.divider()
        st.markdown("**Local demand channels**")
        local_dem = st.slider("Wet market demand (kg/mo)", 500, 5000, 2000, 250)
        wholesale_dem = st.slider("Wholesale buyer capacity (kg/mo)", 500, 5000, 1500, 250)
        cannery_dem = st.slider("Cannery/processing capacity (kg/mo)", 1000, 10000, 3000, 500)

    with col2:
        mkt = compute_market_saturation(num_cooperatives=n_coops, production_per_coop_kg=prod_per_coop,
                                        local_demand_kg=local_dem, wholesale_capacity_kg=wholesale_dem,
                                        cannery_capacity_kg=cannery_dem)
        df_mkt = pd.DataFrame(mkt['scenarios'])

        k1, k2, k3 = st.columns(3)
        k1.metric("Max healthy coops", mkt['max_coops_healthy'])
        k2.metric("Saturation point", f"{mkt['saturation_point']} coops" if mkt['saturation_point'] else "Not reached")
        k3.metric("Total demand", f"{local_dem + wholesale_dem + cannery_dem + 500:,} kg/mo")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_mkt['cooperatives'], y=df_mkt['blended_price'],
                            name='Blended price (฿/kg)',
                            marker_color=df_mkt['status'].map({'🟢 Healthy': '#10b981',
                                                                '🟡 Pressure': '#f59e0b',
                                                                '🔴 Oversupply': '#ef4444'})))
        fig.add_trace(go.Scatter(x=df_mkt['cooperatives'], y=df_mkt['supply_ratio'] * 50,
                                mode='lines+markers', name='Supply ratio (×50)',
                                line=dict(color='#3b82f6', width=3), yaxis='y2'))
        fig.update_layout(title="Blended Price & Supply Ratio by # of Cooperatives",
                         xaxis_title="Number of cooperatives", yaxis_title="฿/kg",
                         yaxis2=dict(title="Supply ratio", overlaying='y', side='right'),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_mkt[['cooperatives', 'total_supply_kg', 'supply_ratio', 'price_drop_pct',
                            'blended_price', 'unsold_kg', 'revenue', 'status']],
                     use_container_width=True, hide_index=True)

        if mkt['saturation_point']:
            st.warning(f"⚠️ Market saturates at **{mkt['saturation_point']} cooperatives**. "
                      f"Beyond this, prices drop 15-50% and unsold inventory accumulates. "
                      f"**Diversify channels** (dried mushroom, cannery) before scaling past {mkt['max_coops_healthy']} coops.")


# ================================================================
# LAB 23: RICE VARIETY STRAW (ROUND 6)
# ================================================================
    render_references("📉 Market Saturation")

elif lab == "🌾 Rice Variety Straw":
    st.title("🌾 Rice Variety Straw Comparison")
    st.markdown("*Does KDML105 straw give different mushroom yields than RD6? Which variety is best for substrate?*")

    varieties = compute_straw_variety_comparison()
    df_var = pd.DataFrame(varieties)

    k1, k2, k3, k4 = st.columns(4)
    best_yield = max(varieties, key=lambda x: x['mushroom_yield_kg'])
    best_quality = max(varieties, key=lambda x: x['substrate_quality'])
    k1.metric("Best yield", best_yield['variety'].split(' ')[0], delta=f"{best_yield['mushroom_yield_kg']} kg/rai")
    k2.metric("Best substrate", best_quality['variety'].split(' ')[0], delta=f"Quality score {best_quality['substrate_quality']}")
    k3.metric("Highest straw", "RD41", delta="750 kg/rai")
    k4.metric("Year-round", "RD47", delta="Non-photoperiod")

    tab1, tab2 = st.tabs(["Yield & Revenue", "Composition"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_var['variety'], y=df_var['straw_yield_kg_rai'],
                            name='Straw yield (kg/rai)', marker_color='#f59e0b'))
        fig.add_trace(go.Bar(x=df_var['variety'], y=df_var['mushroom_yield_kg'],
                            name='Mushroom yield (kg/rai)', marker_color='#10b981'))
        fig.add_trace(go.Scatter(x=df_var['variety'], y=df_var['mushroom_revenue'],
                                mode='lines+markers', name='Revenue (฿)', yaxis='y2',
                                line=dict(color='#3b82f6', width=3)))
        fig.update_layout(title="Straw → Mushroom → Revenue by Rice Variety",
                         yaxis_title="kg/rai", yaxis2=dict(title="Revenue (฿)", overlaying='y', side='right'),
                         barmode='group', template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig2 = go.Figure()
        for comp in ['cellulose_pct', 'hemicellulose_pct', 'lignin_pct', 'silica_pct']:
            fig2.add_trace(go.Bar(x=df_var['variety'], y=df_var[comp],
                                 name=comp.replace('_pct', '').title()))
        fig2.update_layout(title="Straw Composition by Variety",
                         barmode='stack', yaxis_title="% of dry weight",
                         template="plotly_white", height=400)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df_var[['variety', 'region', 'grain_yield_kg_rai', 'straw_yield_kg_rai',
                         'substrate_quality', 'effective_be', 'mushroom_yield_kg', 'mushroom_revenue', 'notes']],
                 use_container_width=True, hide_index=True)

    st.success("🌾 **All 4 varieties work well as substrate.** Differences are small (±5% yield). "
              "RD41 has highest straw volume; KDML105 is most common in Isaan. "
              "**Focus on freshness & storage, not variety selection.**")


# ================================================================
# LAB 24: ADOPTION S-CURVE (ROUND 6)
# ================================================================
    render_references("🌾 Rice Variety Straw")

elif lab == "📈 Adoption S-Curve":
    st.title("📈 Farmer Adoption S-Curve")
    st.markdown("*Rogers' Diffusion of Innovation + Bass Model — how fast will Zero-Burn spread?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        total_farmers = st.slider("Farmers in district", 50, 1000, 200, 50)
        initial = st.slider("Initial pilot farmers", 1, 20, 5)
        years = st.slider("Years to model", 5, 20, 10)
        st.divider()
        demo_effect = st.slider("Demonstration effect", 0.1, 0.8, 0.3, 0.05,
                               help="How strongly neighbors influence each other")
        training = st.radio("Training quality", ['excellent', 'good', 'basic', 'none'],
                           format_func=lambda x: {'excellent': '🎓 Excellent (hands-on + follow-up)',
                                                    'good': '📚 Good (workshop + demo)',
                                                    'basic': '📋 Basic (pamphlet only)',
                                                    'none': '❌ None'}[x])

    with col2:
        adopt = compute_adoption_curve(total_farmers, initial, 0.15, demo_effect, training, years)
        df_adopt = pd.DataFrame(adopt['timeline'])

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("50% adoption", f"Year {adopt['year_to_50pct']}" if adopt['year_to_50pct'] else "Not reached")
        k2.metric("80% adoption", f"Year {adopt['year_to_80pct']}" if adopt['year_to_80pct'] else "Not reached")
        k3.metric("Final adoption", f"{adopt['final_adoption']}%")
        k4.metric("Year 10 profit", f"฿{df_adopt.iloc[-1]['annual_profit']:,}")

        fig = go.Figure()
        colors = df_adopt['category'].map({
            'Innovators': '#8b5cf6', 'Early Adopters': '#3b82f6',
            'Early Majority': '#10b981', 'Late Majority': '#f59e0b', 'Laggards': '#ef4444'
        })
        fig.add_trace(go.Bar(x=df_adopt['year'], y=df_adopt['new_adopters'],
                            name='New adopters', marker_color=colors))
        fig.add_trace(go.Scatter(x=df_adopt['year'], y=df_adopt['adoption_pct'],
                                mode='lines+markers', name='Adoption %', yaxis='y2',
                                line=dict(color='#3b82f6', width=3)))
        fig.update_layout(title="Adoption S-Curve (Rogers' Diffusion)",
                         xaxis_title="Year", yaxis_title="New Adopters",
                         yaxis2=dict(title="Cumulative %", overlaying='y', side='right', range=[0, 105]),
                         template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Impact table
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_adopt['year'], y=df_adopt['annual_profit'],
                             name='Annual profit (฿)', marker_color='#10b981'))
        fig2.add_trace(go.Scatter(x=df_adopt['year'], y=df_adopt['co2_avoided_tons'],
                                 mode='lines+markers', name='CO₂ avoided (tons)', yaxis='y2',
                                 line=dict(color='#ef4444', width=3)))
        fig2.update_layout(title="Economic & Environmental Impact Over Time",
                         xaxis_title="Year", yaxis_title="Annual Profit (฿)",
                         yaxis2=dict(title="CO₂ Avoided (tons)", overlaying='y', side='right'),
                         template="plotly_white", height=350)
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df_adopt, use_container_width=True, hide_index=True)

        st.info("💡 **Training quality is the #1 accelerator.** "
               f"'Excellent' training reaches 50% adoption ~2 years faster than 'basic'. "
               f"The demonstration effect matters — **one successful farmer convinces neighbors faster than any pamphlet.**")


# ================================================================
# LAB 25: SENSITIVITY TORNADO (ROUND 6)
# ================================================================
    render_references("📈 Adoption S-Curve")

elif lab == "🎯 Sensitivity Tornado":
    st.title("🎯 Sensitivity Tornado")
    st.markdown("*Which variable kills profitability fastest? Tornado chart reveals the critical risk factors.*")

    sens = compute_full_sensitivity()

    k1, k2, k3 = st.columns(3)
    k1.metric("Base profit/rai", f"฿{sens['base_profit_per_rai']:,}")
    k2.metric("Most sensitive", sens['most_sensitive'])
    k3.metric("Least sensitive", sens['least_sensitive'])

    df_sens = pd.DataFrame(sens['factors'])

    # Tornado chart
    fig = go.Figure()
    for _, row in df_sens.iterrows():
        fig.add_trace(go.Bar(y=[row['name']], x=[row['profit_low'] - row['profit_base']],
                            orientation='h', marker_color='#ef4444',
                            name=f"Low: {row['low']}", showlegend=False,
                            text=f"฿{row['profit_low']:,}", textposition='outside'))
        fig.add_trace(go.Bar(y=[row['name']], x=[row['profit_high'] - row['profit_base']],
                            orientation='h', marker_color='#10b981',
                            name=f"High: {row['high']}", showlegend=False,
                            text=f"฿{row['profit_high']:,}", textposition='outside'))

    fig.update_layout(title=f"Tornado Chart — Profit Sensitivity (Base: ฿{sens['base_profit_per_rai']:,}/rai)",
                     xaxis_title="Profit deviation from base (฿/rai)",
                     barmode='relative', template="plotly_white", height=450,
                     yaxis=dict(autorange='reversed'))
    fig.add_vline(x=0, line_color='black', line_width=2)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_sens[['rank', 'name', 'low', 'base', 'high', 'profit_low', 'profit_base', 'profit_high', 'swing']],
                 use_container_width=True, hide_index=True)

    st.success(f"🎯 **{sens['most_sensitive']}** has the biggest impact (฿{df_sens.iloc[0]['swing']:,} swing). "
              f"**{sens['least_sensitive']}** matters least. "
              f"Focus field pilot validation on the **top 3 factors** first.")


# ================================================================
# ROUND 7 SEPARATOR
# ================================================================
elif lab == "─── Round 7: Health & Pollution ───":
    st.title("💚 Round 7: Health & Pollution Impact")
    st.markdown("""
    **This is why we're doing this.** Rice straw burning kills **32,200 Thais every year** 
    and costs **฿3 billion** in healthcare. These labs quantify exactly what Zero-Burn prevents.
    
    | Stat | Thailand (2024) |
    |------|----------------|
    | Premature deaths from crop burning | **32,200/year** |
    | People affected by air pollution | **12.3 million** |
    | Healthcare costs (PM2.5) | **฿3 billion/year** |
    | Life expectancy reduction | **-2 years average** |
    | Hospital admissions (Mar 2023) | **200,000+** |
    
    *Sources: ThinkGlobalHealth, Nation Thailand, Borgen Project, MOPH*
    """)


# ================================================================
# LAB 26: PM2.5 EMISSIONS (ROUND 7)
# ================================================================
    render_references("🎯 Sensitivity Tornado")

elif lab == "💨 PM2.5 Emissions":
    st.title("💨 PM2.5 Emissions: Burning vs Zero-Burn")
    st.markdown("*IPCC emission factors applied to rice straw — how much pollution does one farmer's field produce?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        rai = st.slider("Rai of rice fields", 5, 100, 15, 5)
        straw_yield = st.slider("Straw yield (kg/rai)", 400, 900, 650, 50)
        burn_eff = st.slider("Burn efficiency (%)", 50, 95, 85, 5,
                            help="How much of the straw actually burns (vs left on field)")

    with col2:
        pm = compute_pm25_emissions(rai, straw_yield, burn_eff / 100)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("PM2.5 avoided", f"{pm['pm25_avoided_kg']:.1f} kg")
        k2.metric("CO₂ avoided", f"{pm['co2_avoided_kg']:.0f} kg")
        k3.metric("Cigarette equiv.", f"{pm['cigarette_equivalent']:,} 🚬",
                 help="PM2.5 avoided = equivalent to NOT smoking this many cigarettes")
        k4.metric("Straw burned", f"{pm['straw_burned_kg']:,} kg")

        df_poll = pd.DataFrame(pm['pollutant_list'])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_poll['pollutant'], y=df_poll['burning_kg'],
                            name='🔥 Burning', marker_color='#ef4444'))
        fig.add_trace(go.Bar(x=df_poll['pollutant'], y=df_poll['zero_burn_kg'],
                            name='🍄 Zero-Burn', marker_color='#10b981'))
        fig.update_layout(title=f"Emissions Comparison — {rai} rai",
                         yaxis_title="kg emitted", yaxis_type="log",
                         barmode='group', template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_poll[['pollutant', 'burning_kg', 'zero_burn_kg', 'avoided_kg', 'reduction_pct']],
                     use_container_width=True, hide_index=True)

        st.success(f"🌬️ Zero-Burn eliminates **{df_poll['reduction_pct'].mean():.0f}% of all pollutant emissions.** "
                  f"For {rai} rai, that's **{pm['pm25_avoided_kg']:.1f} kg less PM2.5** in the air — "
                  f"equivalent to **{pm['cigarette_equivalent']:,} fewer cigarettes** of secondhand smoke.")


# ================================================================
# LAB 27: HEALTHCARE COST IMPACT (ROUND 7)
# ================================================================
    render_references("💨 PM2.5 Emissions")

elif lab == "🏥 Healthcare Cost Impact":
    st.title("🏥 Healthcare Cost Impact")
    st.markdown("*What does burning ACTUALLY cost a farming family in medical bills, lost work, and shortened lives?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Family Profile")
        family_size = st.slider("Family members", 2, 8, 4)
        exposure = st.slider("Burning season (days)", 14, 60, 30)
        has_kids = st.checkbox("Has children under 12", value=True)
        has_old = st.checkbox("Has elderly (60+)", value=True)

    with col2:
        hc = compute_health_cost_impact(family_size, 15, exposure, has_kids, has_old)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Annual health cost", f"฿{hc['total_healthcare_cost']:,}", delta="from burning", delta_color="inverse")
        k2.metric("Lost workdays", f"{hc['lost_workdays']} days", delta=f"-฿{hc['lost_income']:,}", delta_color="inverse")
        k3.metric("Total annual cost", f"฿{hc['total_annual_cost']:,}", delta="burning costs you", delta_color="inverse")
        k4.metric("With Zero-Burn", f"฿{hc['total_zero_burn_cost']:,}", delta=f"Save ฿{hc['annual_savings']:,}")

        df_cond = pd.DataFrame(hc['conditions'])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_cond['condition'], y=df_cond['expected_cost'],
                            marker_color=['#ef4444' if c > 0 else '#d1d5db' for c in df_cond['expected_cost']],
                            text=[f"฿{c:,}" for c in df_cond['expected_cost']], textposition='outside'))
        fig.update_layout(title="Expected Annual Healthcare Cost by Condition",
                         yaxis_title="Expected cost (฿/year)", template="plotly_white",
                         height=350, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_cond[['condition', 'prob_per_season', 'cost_per_episode', 'episodes_per_season',
                             'expected_cost', 'affected']], use_container_width=True, hide_index=True)

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.error("### ⚰️ Long-term Impact of Burning")
            st.markdown(f"""
            - **Lung cancer risk**: {hc['long_term']['lung_cancer_risk_increase']}
            - **Life expectancy**: **-{hc['long_term']['life_expectancy_reduction_years']} years**
            - **Value of lost years**: ฿{hc['long_term']['value_of_lost_years']:,}
            """)
        with c2:
            st.success("### 💚 With Zero-Burn")
            st.markdown(f"""
            - Healthcare cost: **95% reduction**
            - Annual savings: **฿{hc['annual_savings']:,}**
            - Life expectancy: **Normal**
            - Children asthma: **Risk removed**
            """)


# ================================================================
# LAB 28: REGIONAL POLLUTION IMPACT (ROUND 7)
# ================================================================
    render_references("🏥 Healthcare Cost Impact")

elif lab == "🌍 Regional Pollution Impact":
    st.title("🌍 Regional Pollution Impact — District Scale")
    st.markdown("*If Zero-Burn scales across a district, how many lives are saved? How much pollution eliminated?*")

    col1, col2 = st.columns([1, 2])
    with col1:
        start_farmers = st.slider("Starting farmers (Year 1)", 10, 500, 100, 10)
        rai_per = st.slider("Rai per farmer", 5, 50, 15, 5)
        population = st.slider("District population", 10000, 200000, 50000, 10000)
        years = st.slider("Projection years", 5, 20, 10)

    with col2:
        reg = compute_regional_pollution_impact(start_farmers, rai_per, population, years)
        df_reg = pd.DataFrame(reg['yearly'])

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("PM2.5 avoided", f"{reg['total_pm25_avoided_kg']:,} kg", delta=f"Over {years} years")
        k2.metric("CO₂ avoided", f"{reg['total_co2_avoided_tons']:,} tons")
        k3.metric("Premature deaths avoided", f"{reg['total_deaths_avoided']:.1f}")
        k4.metric("Hospital visits avoided", f"{reg['total_hospital_visits_avoided']:,}")

        # Dual chart: PM2.5 + Health savings
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_reg['year'], y=df_reg['pm25_avoided_kg'],
                            name='PM2.5 avoided (kg)', marker_color='#ef4444', opacity=0.7))
        fig.add_trace(go.Bar(x=df_reg['year'], y=df_reg['co2_avoided_tons'],
                            name='CO₂ avoided (tons)', marker_color='#6b7280', opacity=0.7))
        fig.add_trace(go.Scatter(x=df_reg['year'], y=df_reg['people_protected'],
                                mode='lines+markers', name='People protected', yaxis='y2',
                                line=dict(color='#10b981', width=3)))
        fig.update_layout(title="Annual Pollution Reduction & Community Protection",
                         xaxis_title="Year", yaxis_title="kg / tons avoided",
                         yaxis2=dict(title="People protected", overlaying='y', side='right'),
                         barmode='group', template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Financial chart
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_reg['year'], y=df_reg['mushroom_income'],
                             name='Mushroom income (฿)', marker_color='#10b981'))
        fig2.add_trace(go.Bar(x=df_reg['year'], y=df_reg['health_savings'],
                             name='Health savings (฿)', marker_color='#3b82f6'))
        fig2.add_trace(go.Scatter(x=df_reg['year'], y=df_reg['cumulative_health_savings'],
                                 mode='lines+markers', name='Cumulative health savings', yaxis='y2',
                                 line=dict(color='#f59e0b', width=3)))
        fig2.update_layout(title="Economic Impact — Income + Healthcare Savings",
                         xaxis_title="Year", yaxis_title="Annual (฿)",
                         yaxis2=dict(title="Cumulative health savings (฿)", overlaying='y', side='right'),
                         barmode='stack', template="plotly_white", height=400)
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df_reg[['year', 'farmers', 'rai_treated', 'pm25_avoided_kg',
                            'co2_avoided_tons', 'deaths_avoided', 'hospital_visits_avoided',
                            'health_savings', 'mushroom_income']],
                     use_container_width=True, hide_index=True)

        st.success(f"🌍 **Over {years} years**, starting with just {start_farmers} farmers: "
                  f"**{reg['total_pm25_avoided_kg']:,} kg PM2.5 removed** from the air, "
                  f"**{reg['total_deaths_avoided']:.1f} premature deaths prevented**, "
                  f"and **฿{reg['total_health_savings']:,} in healthcare savings** — "
                  f"on top of **฿{reg['total_mushroom_income']:,} in mushroom income**.")


# ================================================================
# ROUND 8 SEPARATOR
# ================================================================
elif lab == "─── Round 8: Breakthrough Science ───":
    st.title("🚀 Round 8: Breakthrough Science")
    st.markdown("""
    **Can we 10x the profit?** These labs explore scientific breakthroughs 
    that could dramatically increase the value of rice straw beyond basic mushroom cultivation.
    
    | Pathway | Potential | Difficulty |
    |---------|----------|------------|
    | 🦄 Multi-Species Mushrooms | 1.5-14x price per kg | Easy to Hard |
    | ♻️ Circular Economy Cascade | +30-50% added value | Medium |
    | 🔥 Biochar + Carbon Credits | +20-40% | Medium |
    | 🧬 Enzymatic Pre-treatment | 2-3x yield boost | Research |
    | 🧱 Mycelium Materials | 10-100x value | Hard, long-term |
    """)


# ================================================================
# LAB 29: MULTI-SPECIES COMPARISON (ROUND 8)
# ================================================================
    render_references("🌍 Regional Pollution Impact")

elif lab == "🦄 Multi-Species Comparison":
    st.title("🦄 Multi-Species Mushroom Profit Comparison")
    st.markdown("*Which mushroom species makes the most money on rice straw? The answer may surprise you.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        rai = st.slider("Farm size (rai)", 5, 100, 15, 5)
        cycles = st.slider("Max cycles/year", 2, 8, 5)
        straw_yield = st.slider("Straw yield (kg/rai)", 400, 900, 650, 50,
                               help="kg of rice straw per rai")

    with col2:
        sp = compute_multi_species_comparison(rai, cycles, straw_yield)
        df_sp = pd.DataFrame(sp['species'])

        # Top metrics
        best = sp['species'][0]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🏆 Most Profitable", best['name'])
        k2.metric("Net Profit", f"฿{best['net_profit']:,}/yr")
        k3.metric("vs Straw Mushroom", f"{best['multiplier']}x")
        k4.metric("ROI", f"{best['roi_pct']}%")

        # Profit comparison chart
        colors = ['#10b981' if s['difficulty'] == 'Easy' else '#f59e0b' if s['difficulty'] == 'Medium' else '#ef4444'
                  for s in sp['species']]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"{s['emoji']} {s['name']}" for s in sp['species']],
            y=[s['net_profit'] for s in sp['species']],
            marker_color=colors,
            text=[f"฿{s['net_profit']:,}" for s in sp['species']],
            textposition='outside',
        ))
        fig.update_layout(title=f"Annual Net Profit by Species — {rai} rai",
                         yaxis_title="Net Profit (฿/year)",
                         template="plotly_white", height=400,
                         annotations=[dict(text="🟢 Easy  🟡 Medium  🔴 Hard",
                                          xref="paper", yref="paper", x=0.98, y=0.98,
                                          showarrow=False, font=dict(size=12))])
        st.plotly_chart(fig, use_container_width=True)

        # Detailed comparison
        tab1, tab2 = st.tabs(["📊 Detailed Comparison", "💡 Recommendations"])

        with tab1:
            # Revenue vs Cost breakdown
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=[f"{s['emoji']} {s['name']}" for s in sp['species']],
                y=[s['gross_revenue'] for s in sp['species']],
                name='Gross Revenue', marker_color='#10b981',
            ))
            fig2.add_trace(go.Bar(
                x=[f"{s['emoji']} {s['name']}" for s in sp['species']],
                y=[-s['total_cost'] for s in sp['species']],
                name='Total Cost', marker_color='#ef4444',
            ))
            fig2.update_layout(title="Revenue vs Cost Breakdown",
                             yaxis_title="฿ (negative = cost)",
                             barmode='relative', template="plotly_white", height=350)
            st.plotly_chart(fig2, use_container_width=True)

            st.dataframe(df_sp[['name', 'price_per_kg', 'bio_efficiency_avg', 'cycle_days',
                               'actual_cycles', 'annual_yield_kg', 'gross_revenue',
                               'total_cost', 'net_profit', 'multiplier', 'difficulty',
                               'straw_compatibility']],
                         use_container_width=True, hide_index=True)

        with tab2:
            easy_best = next((s for s in sp['species'] if s['difficulty'] == 'Easy'), sp['species'][0])
            med_best = next((s for s in sp['species'] if s['difficulty'] == 'Medium'), None)

            c1, c2 = st.columns(2)
            with c1:
                st.success(f"""### 🟢 Easy Win: {easy_best['emoji']} {easy_best['name']}
                - **Price**: ฿{easy_best['price_per_kg']}/kg
                - **Annual yield**: {easy_best['annual_yield_kg']:,} kg
                - **Net profit**: ฿{easy_best['net_profit']:,}/yr
                - **vs Straw mushroom**: **{easy_best['multiplier']}x**
                - **Straw compatibility**: {easy_best['straw_compatibility']}
                - {easy_best['notes']}
                """)
            with c2:
                if med_best:
                    st.warning(f"""### 🟡 Medium Upgrade: {med_best['emoji']} {med_best['name']}
                    - **Price**: ฿{med_best['price_per_kg']}/kg
                    - **Annual yield**: {med_best['annual_yield_kg']:,} kg
                    - **Net profit**: ฿{med_best['net_profit']:,}/yr
                    - **vs Straw mushroom**: **{med_best['multiplier']}x**
                    - **Straw compatibility**: {med_best['straw_compatibility']}
                    - {med_best['notes']}
                    """)

            if sp['best_species'] != easy_best['name']:
                st.info(f"🏆 **Overall best**: {best['emoji']} **{best['name']}** at ฿{best['net_profit']:,}/yr "
                       f"({best['multiplier']}x vs straw mushroom) — but it's **{best['difficulty']}** difficulty. "
                       f"Start with **{easy_best['name']}** first, then upgrade.")
            else:
                st.success(f"🏆 **{best['name']}** is BOTH the most profitable AND the easiest to grow! "
                          f"At **{best['multiplier']}x** the profit of straw mushroom, this is a no-brainer upgrade.")


# ================================================================
# LAB 30: CIRCULAR ECONOMY CASCADE (ROUND 8)
# ================================================================
    render_references("🦄 Multi-Species Comparison")

elif lab == "♻️ Circular Economy Cascade":
    st.title("♻️ Circular Economy Cascade")
    st.markdown("*Every kg of mushroom produces 5 kg of spent substrate. That 'waste' is worth money.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("🍄 Mushroom Output")
        m_yield = st.slider("Annual mushroom yield (kg)", 1000, 50000, 5000, 500,
                           help="Total kg of fresh mushrooms harvested per year")
        farm_rai = st.slider("Farm size (rai)", 5, 100, 15, 5, key="ce_rai")
        sms_r = st.slider("SMS ratio (kg waste / kg mushroom)", 3.0, 7.0, 5.0, 0.5)

        st.subheader("⚙️ Enable Streams")
        v_on = st.checkbox("🪱 Vermicompost", True)
        b_on = st.checkbox("⚡ Biogas Energy", True)
        a_on = st.checkbox("🐄 Animal Feed", True)
        c_on = st.checkbox("🌱 Compost / Soil", True)

    with col2:
        ce = compute_circular_economy_cascade(m_yield, sms_r, v_on, b_on, a_on, c_on, farm_rai)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total SMS", f"{ce['total_sms_kg']:,} kg")
        k2.metric("Added Revenue", f"฿{ce['total_net_revenue']:,}")
        k3.metric("Per kg Mushroom", f"+฿{ce['value_per_kg_mushroom']}/kg")
        k4.metric("Income Boost", f"+{ce['pct_increase']}%")

        if ce['streams']:
            # Revenue by stream
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"{s['emoji']} {s['name']}" for s in ce['streams']],
                y=[s['net_revenue'] for s in ce['streams']],
                marker_color=['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6'][:len(ce['streams'])],
                text=[f"฿{s['net_revenue']:,}" for s in ce['streams']],
                textposition='outside',
            ))
            fig.update_layout(title="Net Revenue by SMS Value Stream",
                             yaxis_title="฿ net revenue",
                             template="plotly_white", height=380)
            st.plotly_chart(fig, use_container_width=True)

            # Allocation pie
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = go.Figure(go.Pie(
                    labels=[f"{s['emoji']} {s['name']}" for s in ce['streams']],
                    values=[s['sms_input_kg'] for s in ce['streams']],
                    hole=0.4,
                    marker_colors=['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6'][:len(ce['streams'])],
                ))
                fig_pie.update_layout(title="SMS Allocation", height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

            with c2:
                st.markdown("### 📋 Stream Details")
                for s in ce['streams']:
                    with st.expander(f"{s['emoji']} {s['name']} — ฿{s['net_revenue']:,} net"):
                        st.markdown(f"""
                        - **Input**: {s['sms_input_kg']:,} kg SMS ({s['allocation_pct']}%)
                        - **Output**: {s['output_kg']:,} {s['output_unit']}
                        - **Revenue**: ฿{s['gross_revenue']:,} (cost: ฿{s['processing_cost']:,})
                        - **Processing**: {s['processing_days']} days | {s['difficulty']}
                        - **Market**: {s['market']}
                        - {s['description']}
                        """)

            # Total value summary
            mushroom_income = m_yield * 55
            total_with_cascade = mushroom_income + ce['total_net_revenue']
            st.divider()
            st.success(f"💰 **Mushroom income**: ฿{mushroom_income:,} + **SMS cascade**: ฿{ce['total_net_revenue']:,} "
                      f"= **Total**: ฿{total_with_cascade:,}/yr — "
                      f"that's **+{ce['pct_increase']}%** more income just from 'waste' that was previously thrown away!")
        else:
            st.warning("Enable at least one value stream to see results.")


# ================================================================
# LAB 31: BIOCHAR + CARBON CREDITS (ROUND 8)
# ================================================================
    render_references("♻️ Circular Economy Cascade")

elif lab == "🔥 Biochar + Carbon Credits":
    st.title("🔥 Biochar + Carbon Credits")
    st.markdown("*Turn excess rice straw into biochar — sequester carbon AND earn credits.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("⚗️ Pyrolysis Setup")
        straw_kg = st.slider("Straw for biochar (kg/yr)", 500, 10000, 3000, 250,
                            help="kg of rice straw to pyrolyze (excess not used for mushrooms)")
        pyro_temp = st.slider("Pyrolysis temperature (°C)", 300, 800, 500, 50,
                             help="Higher = less biochar but more carbon")
        bc_rai = st.slider("Farm size (rai)", 5, 100, 15, 5, key="bc_rai")

        st.subheader("💰 Market Prices")
        credit_price = st.slider("Carbon credit (฿/tCO₂)", 50, 2000, 175, 25,
                                help="T-VER average: ฿175, agriculture: up to ฿2,076")
        bc_price = st.slider("Biochar sale (฿/kg)", 5, 30, 12, 1)

    with col2:
        bc = compute_biochar_carbon_credits(straw_kg, pyro_temp, credit_price, bc_price, bc_rai)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("⬛ Biochar Output", f"{bc['biochar_kg']:,} kg")
        k2.metric("🌿 CO₂ Sequestered", f"{bc['total_carbon_benefit_tonnes']:.1f} t")
        k3.metric("💰 Net Profit", f"฿{bc['net_profit']:,}/yr")
        k4.metric("🌡️ Carbon Content", f"{bc['carbon_content_pct']}%")

        # Revenue breakdown
        tab1, tab2 = st.tabs(["📊 Revenue Breakdown", "📈 10-Year Projection"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                fig = go.Figure(go.Pie(
                    labels=[r['source'] for r in bc['revenue_breakdown']],
                    values=[r['amount'] for r in bc['revenue_breakdown']],
                    hole=0.4,
                    marker_colors=['#10b981', '#374151', '#f59e0b', '#8b5cf6'],
                ))
                fig.update_layout(title=f"Revenue Sources — ฿{bc['total_revenue']:,}/yr",
                                 height=350)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("### 📋 Breakdown")
                for r in bc['revenue_breakdown']:
                    st.markdown(f"{r['emoji']} **{r['source']}**: ฿{r['amount']:,}")
                st.divider()
                st.markdown(f"**Total Revenue**: ฿{bc['total_revenue']:,}")
                st.markdown(f"**Total Cost**: ฿{bc['total_cost']:,}")
                st.markdown(f"**Net Profit**: ฿{bc['net_profit']:,}")
                st.divider()
                st.info(f"⚗️ **Pyrolysis at {pyro_temp}°C**: {bc['conversion_rate']}% straw → biochar, "
                       f"{bc['carbon_content_pct']}% carbon content")

        with tab2:
            df_yr = pd.DataFrame(bc['yearly'])
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df_yr['year'], y=df_yr['carbon_revenue'],
                                name='Carbon Credits', marker_color='#10b981'))
            fig2.add_trace(go.Bar(x=df_yr['year'], y=df_yr['biochar_revenue'],
                                name='Biochar Sales', marker_color='#374151'))
            fig2.add_trace(go.Bar(x=df_yr['year'], y=df_yr['soil_value'] + df_yr['fert_savings'],
                                name='Soil + Fertilizer', marker_color='#f59e0b'))
            fig2.add_trace(go.Scatter(x=df_yr['year'], y=df_yr['net_profit'],
                                    name='Net Profit', line=dict(color='#ef4444', width=3),
                                    mode='lines+markers'))
            fig2.update_layout(title="10-Year Revenue Growth (Carbon credits +15%/yr)",
                             yaxis_title="฿", barmode='stack',
                             template="plotly_white", height=400)
            st.plotly_chart(fig2, use_container_width=True)

            cumulative_co2 = bc['yearly'][-1]['cumulative_co2']
            cumulative_profit = sum(y['net_profit'] for y in bc['yearly'])
            st.success(f"🌍 **Over 10 years**: **{cumulative_co2:.1f} tonnes CO₂** sequestered, "
                      f"**฿{cumulative_profit:,}** total profit from biochar + credits. "
                      f"Carbon credit prices at +15%/yr could reach "
                      f"฿{bc['yearly'][-1]['carbon_price']:,}/tCO₂ by year 10.")



# ================================================================
# LAB 32: ENZYMATIC PRE-TREATMENT (ROUND 8)
# ================================================================
    render_references("🔥 Biochar + Carbon Credits")

elif lab == "🧬 Enzymatic Pre-treatment":
    st.title("🧬 Enzymatic Pre-treatment")
    st.markdown("*Enzymes break down straw polymers → mycelium accesses more nutrients → yield skyrockets.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("🧪 Enzyme Setup")
        enz_species = st.selectbox("Mushroom species", ['oyster', 'king_oyster', 'shiitake', 'lions_mane', 'straw'],
                                   format_func=lambda x: {'oyster': '🦪 Oyster', 'king_oyster': '👑 King Oyster',
                                                          'shiitake': '🔶 Shiitake', 'lions_mane': "🦁 Lion's Mane",
                                                          'straw': '🍄 Straw'}[x])
        enz_type = st.selectbox("Enzyme type", ['cellulase_complex', 'laccase', 'xylanase', 'full_cocktail'],
                               format_func=lambda x: {'cellulase_complex': '🧬 Cellulase Complex',
                                                      'laccase': '🔬 Laccase (Lignin)',
                                                      'xylanase': '🧪 Xylanase',
                                                      'full_cocktail': '💉 Full Cocktail'}[x])
        enz_dose = st.slider("Enzyme dose (% of substrate)", 0.2, 2.0, 1.0, 0.1)
        enz_straw = st.slider("Straw substrate (kg/yr)", 2000, 20000, 9750, 250, key="enz_straw")
        enz_cycles = st.slider("Cycles per year", 2, 8, 5, 1, key="enz_cycles")

    with col2:
        ep = compute_enzymatic_pretreatment(enz_straw, enz_type, enz_dose, enz_species, enz_cycles)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("BE Boost", f"+{ep['be_boost_pct']}%")
        k2.metric("Extra Yield", f"+{ep['yield_increase_kg']:,} kg")
        k3.metric("Net Gain", f"฿{ep['net_gain']:,}")
        k4.metric("ROI", f"{ep['roi_pct']}%")

        tab1, tab2 = st.tabs(["📊 Before vs After", "🔬 Enzyme Comparison"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                fig = go.Figure()
                fig.add_trace(go.Bar(name='Without Enzyme', x=['Yield (kg)', 'Revenue (฿)'],
                                    y=[ep['base_yield_kg'], ep['base_revenue']],
                                    marker_color='#94a3b8'))
                fig.add_trace(go.Bar(name='With Enzyme', x=['Yield (kg)', 'Revenue (฿)'],
                                    y=[ep['treated_yield_kg'], ep['treated_revenue']],
                                    marker_color='#10b981'))
                fig.update_layout(title=f"{ep['species']} + {ep['enzyme']}",
                                 barmode='group', template="plotly_white", height=350)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown(f"""
                ### 📋 Impact Summary
                - **Species**: {ep['species']}
                - **Base BE**: {ep['base_be']} → **Treated BE**: {ep['treated_be']} (+ {ep['be_boost_pct']}%)
                - **Yield**: {ep['base_yield_kg']:,} → **{ep['treated_yield_kg']:,} kg** (+{ep['yield_increase_kg']:,})
                - **Revenue**: ฿{ep['base_revenue']:,} → **฿{ep['treated_revenue']:,}**
                - **Enzyme Cost**: ฿{ep['enzyme_cost']:,}
                - **Net Gain**: **฿{ep['net_gain']:,}** ({ep['roi_pct']}% ROI)
                """)

        with tab2:
            st.markdown("### Compare all enzyme types on same species")
            for c in ep['comparison']:
                pct_label = f"+{c['be_boost_pct']}% BE"
                st.markdown(f"{c['emoji']} **{c['type']}** — {pct_label} → ฿{c['net_gain']:,} net ({c['roi_pct']}% ROI)")
                st.progress(min(c['roi_pct'] / max(ep['comparison'][0]['roi_pct'], 1), 1.0))
                st.caption(c['desc'])

            best = ep['comparison'][0]
            st.success(f"🏆 **Best enzyme for {ep['species']}**: **{best['type']}** — "
                      f"฿{best['net_gain']:,} net gain with {best['roi_pct']}% ROI")


# ================================================================
# LAB 33: MYCELIUM MATERIALS (ROUND 8)
# ================================================================
    render_references("🧬 Enzymatic Pre-treatment")

elif lab == "🧱 Mycelium Materials":
    st.title("🧱 Mycelium Materials — The Moonshot")
    st.markdown("*Rice straw + mycelium = packaging, leather, insulation. This is where value goes 50-100x.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("🏭 Production Setup")
        my_product = st.selectbox("Product", ['packaging', 'leather', 'insulation'],
                                  format_func=lambda x: {'packaging': '📦 Packaging',
                                                         'leather': '👜 Mycelium Leather',
                                                         'insulation': '🧱 Building Insulation'}[x])
        my_scale = st.selectbox("Scale", ['small', 'medium', 'large'],
                               format_func=lambda x: {'small': '🏠 Cottage (฿50k setup)',
                                                      'medium': '🏢 Workshop (฿250k)',
                                                      'large': '🏭 Factory (฿2M)'}[x])
        my_straw = st.slider("Annual straw input (kg)", 1000, 20000, 5000, 500, key="my_straw")

    with col2:
        mm = compute_mycelium_materials(my_straw, my_product, my_scale)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(f"{mm['emoji']} Units", f"{mm['units_produced']:,}")
        k2.metric("Revenue", f"฿{mm['gross_revenue']:,}")
        k3.metric("Net Profit", f"฿{mm['net_profit']:,}")
        k4.metric("vs Straw Mushroom", f"{mm['multiplier_vs_straw']}x")

        tab1, tab2 = st.tabs(["📊 Product Comparison", "💡 Market Intel"])

        with tab1:
            fig = go.Figure()
            colors = ['#10b981', '#f59e0b', '#8b5cf6']
            for i, p in enumerate(mm['all_products']):
                fig.add_trace(go.Bar(
                    name=f"{p['emoji']} {p['product']}",
                    x=['Revenue', 'Cost', 'Profit'],
                    y=[p['revenue'], p['cost'], p['profit']],
                    marker_color=colors[i % 3],
                ))
            fig.update_layout(title="All Products at Same Scale",
                             barmode='group', template="plotly_white", height=380,
                             yaxis_title="฿")
            st.plotly_chart(fig, use_container_width=True)

            for p in mm['all_products']:
                with st.expander(f"{p['emoji']} {p['product']} — ฿{p['profit']:,} profit ({p['vs_mushroom']}x vs mushroom)"):
                    st.markdown(f"""
                    - **Units**: {p['units']:,} | **Revenue**: ฿{p['revenue']:,}
                    - **Cost**: ฿{p['cost']:,} | **Profit**: ฿{p['profit']:,}
                    - **Difficulty**: {p['difficulty']} | **Market**: {p['market']}
                    """)

        with tab2:
            st.markdown(f"""
            ### 🌍 {mm['product']} Market
            - **Market**: {mm['market_info']}
            - **Competitors**: {mm['competitors']}
            - **Growth Days**: {mm['growth_days']} per batch
            - **Scale**: {mm['scale']} ({mm['scale_label']})
            - **Setup Cost**: ฿{mm['setup_cost']:,}
            """)
            st.info("💡 **Global mycelium market**: $3.6B (2025). IKEA, Dell, Adidas, Hermès all buying. "
                   "Thailand can be the producer — rice straw is one of the best substrates.")
            if mm['multiplier_vs_straw'] >= 10:
                st.success(f"🚀 **MOONSHOT ACHIEVED**: At {mm['multiplier_vs_straw']}x the value of straw mushroom farming, "
                          f"mycelium materials represent a **paradigm shift** in rice straw value.")
            elif mm['multiplier_vs_straw'] >= 3:
                st.warning(f"⭐ **Strong potential**: {mm['multiplier_vs_straw']}x straw mushroom income. "
                          f"Scale up to unlock full potential.")

    render_references("🧱 Mycelium Materials")


# ================================================================
# ROUND 9 SECTION DIVIDER
# ================================================================
elif lab == "─── Round 9: Drone Tech ───":
    st.title("🛸 Round 9: Drone Technology")
    st.markdown("""
    **Agricultural drones are revolutionizing Thai farming.** DJI drone sales in Thailand 
    increased **50x** by end of 2024, with **10,000+ certified operators**.
    
    This round explores drone ROI for our zero-burn mushroom farming operation.
    
    | Lab | Focus | Key Question |
    |-----|-------|-------------|
    | 🛸 Drone Operations & ROI | Spray, Monitor, Verify | **Should farmers buy, share, or hire drones?** |
    
    **Thai Government Support:**
    - DEPA "One Drone, One Community" → **60% subsidy** on drone purchase
    - "Half-cost agricultural drone" scheme (Oct 2025)
    - Goal: 1.25 million rai covered by community drones
    """)


# ================================================================
# LAB 34: DRONE OPERATIONS & ROI (ROUND 9)
# ================================================================
    render_references("🧱 Mycelium Materials")

elif lab == "🛸 Drone Operations & ROI":
    st.title("🛸 Drone Operations & ROI Lab")
    st.markdown("*Buy, share, or hire? Compare drone strategies for spraying, monitoring, and burn detection.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("⚙️ Setup")
        drone_model = st.selectbox("Drone Strategy", [
            'service', 'thai_local', 'dji_t10', 'dji_t25', 'dji_t50'
        ], format_func=lambda x: {
            'service': '📞 Hire Service (฿0 investment)',
            'thai_local': '🇹🇭 Thai GCS-9 (฿75,000)',
            'dji_t10': '🤖 DJI Agras T10 (฿204,000)',
            'dji_t25': '🚀 DJI Agras T25 (฿385,000)',
            'dji_t50': '✈️ DJI Agras T50 (฿560,000)',
        }[x])
        
        coop_size = st.slider("Cooperative size", 1, 30, 10)
        n_rai = st.slider("Rai per farmer", 5, 50, 15)
        subsidy = st.slider("DEPA Subsidy %", 0, 60, 60)
        spray_cycles = st.slider("Spray cycles/year", 2, 12, 6)
        
        use_cases = st.multiselect("Use Cases", 
            ['spray', 'monitoring', 'burn_detection'],
            default=['spray', 'monitoring', 'burn_detection'],
            format_func=lambda x: {
                'spray': '💦 Precision Spraying',
                'monitoring': '📡 Crop Monitoring (NDVI)',
                'burn_detection': '🔥 Burn Detection & Carbon MRV',
            }[x]
        )

    result = compute_drone_operations(
        n_rai=n_rai,
        drone_model=drone_model,
        use_cases=use_cases,
        cooperative_size=coop_size,
        subsidy_pct=subsidy,
        spray_cycles_per_year=spray_cycles,
    )

    with col2:
        # ─── Key Metrics ───
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            inv = result['per_farmer']['investment']
            st.metric("💰 Per Farmer Investment", f"฿{inv:,.0f}")
        with m2:
            ben = result['per_farmer']['annual_benefit']
            st.metric("📈 Annual Benefit/Farmer", f"฿{ben:,.0f}")
        with m3:
            roi = result['roi']['roi_pct']
            st.metric("🎯 ROI", f"{roi:.0f}%" if roi < 10000 else "∞")
        with m4:
            payback = result['roi']['payback_years']
            st.metric("⏱️ Payback", f"{payback:.1f} yr" if payback < 50 else "Instant")

        st.divider()

        # ─── Use Case Tabs ───
        tabs = st.tabs(["💦 Spraying", "📡 Monitoring", "🔥 Burn Detection", "💰 Full ROI", "📋 Regulations"])
        
        with tabs[0]:
            if result['spray']:
                s = result['spray']
                st.subheader("💦 Precision Spraying vs Manual")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    | Metric | Manual | Drone |
                    |--------|--------|-------|
                    | Annual cost | **฿{s['manual_cost_annual']:,.0f}** | **฿{s['drone_cost_annual']:,.0f}** |
                    | Chemical usage | 100% | **{100 - s['chemical_reduction_pct']}%** (-{s['chemical_reduction_pct']}%) |
                    | Yield impact | Baseline | **+{s['yield_boost_pct']}%** |
                    | Spray savings | — | **฿{s['spray_savings']:,.0f}** |
                    | Yield income boost | — | **฿{s['yield_income_boost']:,.0f}** |
                    | **Total benefit** | — | **฿{s['total_spray_benefit']:,.0f}** |
                    """)
                with c2:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='Manual', x=['Cost', 'Chemical Use'], y=[s['manual_cost_annual'], 100], marker_color='#ef4444'))
                    fig.add_trace(go.Bar(name='Drone', x=['Cost', 'Chemical Use'], y=[s['drone_cost_annual'], 60], marker_color='#10b981'))
                    fig.update_layout(barmode='group', title='Manual vs Drone Spraying', height=300, template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
                
                st.success(f"💦 **{s['chemical_reduction_pct']}% less chemicals** + **{s['yield_boost_pct']}% yield boost** = ฿{s['total_spray_benefit']:,.0f} total benefit for {result['total_rai']} rai")
            else:
                st.info("Enable 'Precision Spraying' in use cases to see this analysis.")
        
        with tabs[1]:
            if result['monitoring']:
                mo = result['monitoring']
                st.subheader("📡 NDVI Crop Monitoring & Mapping")
                st.markdown(f"""
                **What drone monitoring gives you:**
                
                | Capability | Value | Annual Savings |
                |-----------|-------|---------------|
                | 🦠 Early disease detection | Spot problems 2 weeks earlier | **฿{mo['disease_detection_savings']:,.0f}** |
                | 💧 Water management optimization | Precise irrigation timing | **฿{mo['water_savings']:,.0f}** |
                | 🌾 Straw inventory mapping | Better collection for mushrooms | **฿{mo['straw_mapping_value']:,.0f}** |
                | 📊 Annual monitoring cost | {mo['monitoring_flights_per_year']} flights/year | **-฿{mo['annual_monitoring_cost']:,.0f}** |
                | **Net monitoring benefit** | | **฿{mo['total_monitoring_benefit']:,.0f}** |
                """)
                
                if mo['camera_cost'] > 0:
                    st.info(f"📸 Multispectral camera add-on: ฿{mo['camera_cost']:,.0f} (amortized over 5 years)")
                
                st.success(f"📡 NDVI monitoring saves ฿{mo['total_monitoring_benefit']:,.0f}/year across {result['total_rai']} rai")
            else:
                st.info("Enable 'Crop Monitoring (NDVI)' in use cases to see this analysis.")
        
        with tabs[2]:
            if result['burn_detection']:
                bd = result['burn_detection']
                st.subheader("🔥 Burn Detection & Carbon Credit Verification")
                st.markdown(f"""
                **Why this matters:** The Thai government (2026) requires proof of zero-burn for subsidies.
                Drone thermal imaging provides verifiable evidence for **T-VER carbon credits** and **penalty avoidance**.
                
                | Component | Value |
                |-----------|-------|
                | 🌍 Baseline carbon credit value | ฿{bd['baseline_credit_value']:,.0f} |
                | 🛸 Drone-verified premium (+30%) | ฿{bd['verified_credit_value']:,.0f} |
                | 💎 Premium from drone verification | **฿{bd['drone_premium_value']:,.0f}** |
                | 🛡️ Subsidy penalty avoidance | **฿{bd['penalty_avoidance']:,.0f}** |
                | 📊 Detection cost | -฿{bd['annual_detection_cost']:,.0f} |
                | **Total burn detection benefit** | **฿{bd['total_burn_benefit']:,.0f}** |
                """)
                
                st.warning("⚠️ **2026 Regulation**: Farmers caught burning face loss of government subsidies AND potential fines up to ฿40,000. Drone proof protects against false accusations too.")
            else:
                st.info("Enable 'Burn Detection' in use cases to see this analysis.")
        
        with tabs[3]:
            st.subheader("💰 Full Investment & ROI Breakdown")
            inv = result['investment']
            roi = result['roi']
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                ### Investment
                | Item | Amount |
                |------|--------|
                | Drone cost | ฿{inv['drone_cost']:,.0f} |
                | DEPA subsidy ({inv['subsidy_pct']}%) | -฿{inv['subsidy_amount']:,.0f} |
                | **Net investment** | **฿{inv['net_investment']:,.0f}** |
                | Per farmer ({coop_size} farmers) | **฿{result['per_farmer']['investment']:,.0f}** |
                | Annual maintenance | ฿{inv['annual_fixed_cost']:,.0f} |
                """)
            
            with c2:
                st.markdown(f"""
                ### Returns
                | Item | Amount |
                |------|--------|
                | Total annual benefit | **฿{roi['total_annual_benefit']:,.0f}** |
                | Net benefit (after costs) | **฿{roi['net_annual_benefit']:,.0f}** |
                | ROI | **{roi['roi_pct']:.0f}%** |
                | Payback period | **{roi['payback_years']:.1f} years** |
                | Per farmer benefit | **฿{result['per_farmer']['annual_benefit']:,.0f}/yr** |
                """)
            
            if result['service_income'] > 0:
                st.success(f"🤑 **Side hustle alert!** A trained operator can earn **฿{result['service_income']:,.0f}/year** servicing other farmers' fields.")
            
            # ROI comparison chart across all drone models
            st.subheader("📊 Drone Model Comparison")
            models = ['service', 'thai_local', 'dji_t10', 'dji_t25', 'dji_t50']
            model_names = ['Hire Service', 'Thai GCS-9', 'DJI T10', 'DJI T25', 'DJI T50']
            investments = []
            benefits = []
            rois = []
            for m in models:
                r = compute_drone_operations(n_rai=n_rai, drone_model=m, cooperative_size=coop_size, subsidy_pct=subsidy)
                investments.append(r['per_farmer']['investment'])
                benefits.append(r['per_farmer']['annual_benefit'])
                rois.append(min(r['roi']['roi_pct'], 500))
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Investment/Farmer', x=model_names, y=investments, marker_color='#ef4444'))
            fig.add_trace(go.Bar(name='Annual Benefit/Farmer', x=model_names, y=benefits, marker_color='#10b981'))
            fig.update_layout(barmode='group', title='Investment vs Annual Benefit by Drone Model', height=350, template='plotly_white',
                            yaxis_title='Thai Baht (฿)')
            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[4]:
            st.subheader("📋 CAAT Regulations (Thailand)")
            regs = result['regulations']
            for key, val in regs.items():
                emoji = {'registration': '📝', 'operator_cert': '🎓', 'flight_hours': '🕐', 
                        'max_altitude': '📏', 'notification': '📱', 'insurance': '🛡️',
                        'penalty': '⚠️', 'no_fly_zones': '🚫'}.get(key, '📌')
                st.markdown(f"{emoji} **{key.replace('_', ' ').title()}**: {val}")
            
            st.divider()
            st.markdown("""
            ### 🇹🇭 Government Programs
            
            | Program | Subsidy | Coverage |
            |---------|---------|---------|
            | DEPA "One Drone, One Community" | **60% of drone cost** | 1.25M rai target |
            | "Half-cost agricultural drone" (Oct 2025) | **50% service subsidy** | Central region pilot |
            | BAAC Smart Tech Loan | **MRR - 1% (5.625%)** | Agricultural tech |
            
            *Sources: DEPA, Bangkok Post, Winrock International*
            """)

    render_references("🛸 Drone Operations & ROI")


# ================================================================
# LAB 35: DRONE COLD PASTEURIZATION (ROUND 9)
# ================================================================
    render_references("🛸 Drone Operations & ROI")

elif lab == "🧪 Drone Cold Pasteurization":
    st.title("🧪 Drone Cold Pasteurization Lab")
    st.markdown("*Can we eliminate the ฿50,000 boiler? Lime & H₂O₂ cold methods delivered by drone.*")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("⚙️ Method")
        method = st.selectbox("Pasteurization Method", [
            'steam', 'lime', 'h2o2', 'fermentation'
        ], index=1, format_func=lambda x: {
            'steam': '🔥 Traditional Steam Boiler',
            'lime': '🧪 Lime (Ca(OH)₂) — Drone Spray',
            'h2o2': '🧴 Hydrogen Peroxide — Drone Spray',
            'fermentation': '💧 Cold Water Fermentation',
        }[x])
        
        coop = st.slider("Cooperative size", 1, 30, 10, key="cp_coop")
        n_rai = st.slider("Rai per farmer", 5, 50, 15, key="cp_rai")
        be = st.slider("Base BE %", 5, 25, 12, key="cp_be")
        price = st.slider("Mushroom price ฿/kg", 30, 120, 60, key="cp_price")

    result = compute_cold_pasteurization(
        n_rai=n_rai,
        method=method,
        cooperative_size=coop,
        be_pct=be,
        mushroom_price=price,
    )

    with col2:
        # ─── Key Metrics ───
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            savings = result['vs_steam']['cost_savings']
            st.metric("💰 vs Steam Savings", f"฿{savings:,.0f}/yr", 
                     delta=f"{result['vs_steam']['cost_savings_pct']:.0f}%")
        with m2:
            st.metric("🍄 Annual Harvest", f"{result['production']['total_mushroom_kg']:,.0f} kg")
        with m3:
            st.metric("💵 Annual Profit", f"฿{result['production']['profit']:,.0f}")
        with m4:
            boiler = "✅ Eliminated" if result['vs_steam']['boiler_eliminated'] else "❌ Still needed"
            st.metric("🔥 Boiler Status", boiler)

        st.divider()

        # ─── Tabs ───
        tabs = st.tabs(["📊 Head-to-Head", "💰 Cost Breakdown", "⚡ Throughput", "🔬 How It Works"])

        with tabs[0]:
            st.subheader("📊 All 4 Methods — Head-to-Head Comparison")
            
            comp = result['all_methods_comparison']
            names = [c['name'] for c in comp]
            costs = [c['annual_cost'] for c in comp]
            profits = [c['profit'] for c in comp]
            contam = [c['contamination'] for c in comp]
            
            # Profit comparison
            colors = ['#ef4444', '#10b981', '#3b82f6', '#8b5cf6']
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Annual Cost', x=names, y=costs, marker_color='#ef4444', opacity=0.7))
            fig.add_trace(go.Bar(name='Annual Profit', x=names, y=profits, marker_color='#10b981'))
            fig.update_layout(barmode='group', title='Cost vs Profit by Method', height=350, 
                            template='plotly_white', yaxis_title='Thai Baht (฿)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Comparison table
            st.markdown("| Method | Annual Cost | Profit | Cost/kg straw | Contamination | BE |")
            st.markdown("|--------|-----------|--------|--------------|--------------|-----|")
            for c in comp:
                highlight = "**" if c['key'] == method else ""
                st.markdown(f"| {highlight}{c['name']}{highlight} | ฿{c['annual_cost']:,.0f} | ฿{c['profit']:,.0f} | ฿{c['cost_per_kg_straw']:.2f} | {c['contamination']}% | {c['be']:.1f}% |")
            
            # Winner
            best = max(comp, key=lambda x: x['profit'])
            st.success(f"🏆 **{best['name']}** delivers the highest profit: ฿{best['profit']:,.0f}/year")

        with tabs[1]:
            st.subheader("💰 Cost Breakdown — Selected Method")
            costs = result['costs']
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                | Cost Component | Amount |
                |---------------|--------|
                | 🏗️ Equipment (annual) | ฿{costs['equipment_annual']:,.0f} |
                | ⛽ Fuel | ฿{costs['fuel']:,.0f} |
                | 🧪 Chemicals | ฿{costs['chemicals']:,.0f} |
                | 💧 Water | ฿{costs['water']:,.0f} |
                | 👷 Labor | ฿{costs['labor']:,.0f} |
                | 🛸 Drone delivery | ฿{costs['drone_delivery']:,.0f} |
                | **Total annual** | **฿{costs['total_annual']:,.0f}** |
                | **Per kg straw** | **฿{costs['cost_per_kg_straw']:.2f}** |
                """)
            with c2:
                # Pie chart
                labels = ['Equipment', 'Fuel', 'Chemicals', 'Water', 'Labor', 'Drone']
                values = [costs['equipment_annual'], costs['fuel'], costs['chemicals'],
                         costs['water'], costs['labor'], costs['drone_delivery']]
                # Filter out zero values
                filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
                if filtered:
                    fig = go.Figure(data=[go.Pie(
                        labels=[f[0] for f in filtered],
                        values=[f[1] for f in filtered],
                        hole=0.4,
                        marker_colors=['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#06b6d4']
                    )])
                    fig.update_layout(title=f'{result["method"]["name"]} Cost Split', height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            if result['vs_steam']['boiler_eliminated']:
                st.warning(f"🔥 **Boiler eliminated!** One-time savings of ฿{result['vs_steam']['boiler_equipment_savings']:,.0f} in equipment + annual fuel savings.")

        with tabs[2]:
            st.subheader("⚡ Throughput & Capacity")
            tp = result['throughput']
            
            st.markdown(f"""
            | Metric | Value |
            |--------|-------|
            | Batch size | **{tp['batch_size_kg']:,} kg** straw |
            | Cycle time | **{tp['total_cycle_hours']} hours** ({tp['total_cycle_hours']/24:.1f} days) |
            | Daily capacity | **{tp['daily_capacity_kg']:,} kg**/day |
            | Batches/year needed | **{tp['batches_per_year']:,}** |
            | Days to process all straw | **{tp['days_to_process']:.0f} days** |
            | Total straw for cooperative | **{result['total_straw_kg']:,} kg** |
            """)
            
            # Throughput comparison bar
            all_methods = ['Steam', 'Lime', 'H₂O₂', 'Fermentation']
            batch_sizes = [100, 500, 500, 1000]
            cycle_hours = [11, 20, 20, 264]
            daily_caps = [round(24/ch * bs) for ch, bs in zip(cycle_hours, batch_sizes)]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=all_methods, y=daily_caps, marker_color=['#ef4444', '#10b981', '#3b82f6', '#8b5cf6']))
            fig.update_layout(title='Daily Processing Capacity (kg straw/day)', height=300, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)

        with tabs[3]:
            st.subheader("🔬 How It Works")
            m = result['method']
            
            st.info(f"**{m['name']}**\n\n{m['description']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### ✅ Advantages")
                for pro in m['pros']:
                    st.markdown(f"- {pro}")
            with c2:
                st.markdown("### ⚠️ Limitations")
                for con in m['cons']:
                    st.markdown(f"- {con}")
            
            if method == 'lime':
                st.divider()
                st.markdown("""
                ### 🧪 Lime Pasteurization — The Science
                
                **Chemical reaction:** Ca(OH)₂ + H₂O → Ca²⁺ + 2OH⁻ (pH rises to 12+)
                
                | Parameter | Value |
                |-----------|-------|
                | Hydrated lime per liter | **2 grams** |
                | Target pH | **12.0+** |
                | Soak duration | **12-24 hours** |
                | Log reduction | **4 log** (99.99% kill) |
                | Thai lime price | **฿8/kg** (bulk agricultural) |
                | Cost per kg straw | **฿0.40** |
                
                > ⚠️ **Critical:** Must use **hydrated lime** Ca(OH)₂, NOT garden lime (CaCO₃).
                > Garden lime will NOT achieve pH 12.
                
                **Why mycelium survives:** Mushroom mycelium is naturally alkaline-tolerant. 
                Most competitor molds and bacteria cannot survive pH 12+.
                """)
            
            elif method == 'h2o2':
                st.divider()
                st.markdown("""
                ### 🧴 Hydrogen Peroxide — The Science
                
                **Mechanism:** H₂O₂ creates reactive oxygen species (ROS) → oxidative cell damage
                
                | Parameter | Value |
                |-----------|-------|
                | Working concentration | **3%** H₂O₂ |
                | Dilution from 35% stock | **1:10** ratio |
                | Soak duration | **12-24 hours** |
                | Decomposition products | **Water + Oxygen** (clean!) |
                | Log reduction | **4.5 log** |
                
                > 🧬 **Key insight:** Mushroom mycelium is **naturally resistant** to oxidative stress
                > because it produces its own antioxidant enzymes (catalase, SOD).
                > 
                > Bonus: H₂O₂ slightly breaks down lignocellulose → **BE boost +2%**
                """)

    render_references("🧪 Drone Cold Pasteurization")
