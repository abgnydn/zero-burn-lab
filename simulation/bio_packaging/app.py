"""Bio-Packaging Hub — Standalone Streamlit App."""
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine import compute_bio_packaging_hub

st.set_page_config(page_title="Zero-Burn Platform — Bio-Packaging Lab", page_icon="📦", layout="wide")

_hdr1, _hdr2 = st.columns([6, 1])
with _hdr1:
    st.title("📦 Zero-Burn Bio-Packaging Platform")
with _hdr2:
    TH = st.toggle("🇹🇭 ไทย", value=False, key="lang_th")

st.markdown("*" + ("แพลตฟอร์มเชื่อมฮับเกษตรกรกับร้านอาหาร — เปลี่ยนฟางที่ถูกเผาเป็นจานย่อยสลายได้" if TH else
                   "Decentralized hub platform connecting farmers (supply) with restaurants & hotels (demand) — turning burned straw into biodegradable packaging.") + "*")
st.info("🏗️ **Platform Model:** You fund/equip hubs → farmers produce → you distribute at 25% margin → "
        "farmers earn 75% and own equipment after 10 months. Think: *CP Chicken model for eco-plates.*" if not TH else
        "🏗️ **โมเดลแพลตฟอร์ม:** คุณลงทุนฮับ → เกษตรกรผลิต → คุณจัดจำหน่ายได้ 25% → เกษตรกรได้ 75% และเป็นเจ้าของอุปกรณ์ใน 10 เดือน")

col1, col2 = st.columns([1, 3])
with col1:
    st.subheader("⚙️")
    bp_tier = st.radio("Equipment Tier", ['micro', 'starter', 'mid', 'industrial'],
                      format_func=lambda x: {'micro': '🔧 Micro (฿50K)', 'starter': '🌱 Starter (฿200K)', 'mid': '⚖️ Mid (฿500K)', 'industrial': '🏭 Industrial (฿1.5M)'}[x], key="bp_t")


    st.divider()
    st.markdown("#### ⏱️ " + ("ตารางงาน" if TH else "Work Schedule"))
    base_hrs_map = {'micro': 4, 'starter': 5, 'mid': 6, 'industrial': 8}
    _default_hrs = base_hrs_map[bp_tier]
    bp_hours = st.slider("⏱️ " + ("ชม./วัน" if TH else "Hours/Day"), 2, 12, _default_hrs, key="bp_hrs")
    _days_map = {'micro': 280, 'starter': 300, 'mid': 300, 'industrial': 320}
    bp_days = st.slider("📅 " + ("วัน/ปี" if TH else "Days/Year"), 250, 330, _days_map[bp_tier], key="bp_days")
    hour_scale = bp_hours / base_hrs_map[bp_tier]
    if hour_scale > 1:
        st.info(f"⚡ {hour_scale:.1f}× capacity — same equipment, {bp_hours} hrs instead of {base_hrs_map[bp_tier]}")

    st.divider()
    st.markdown("#### 🌾 " + ("ปริมาณฟาง" if TH else "Straw Supply"))
    bp_2crop = st.toggle("🌾🌾 " + ("ข้าว 2 รอบ" if TH else "2nd Crop (+70% straw)"), value=True, key="bp_2c")
    straw_mult = 1.7 if bp_2crop else 1.0
    base_caps = {'micro': 80, 'starter': 200, 'mid': 500, 'industrial': 1000}
    scaled_cap = base_caps[bp_tier] * hour_scale
    rai_for_full = max(5, round(scaled_cap * bp_days / (650 * straw_mult)))
    rai_defaults = {'micro': (5, 50, 30), 'starter': (10, 120, 50), 'mid': (30, 300, 120), 'industrial': (50, 600, 250)}
    rai_min, rai_max_base, rai_def = rai_defaults[bp_tier]
    rai_max = max(rai_max_base, rai_for_full + 50)
    rai_def_adj = min(rai_def, rai_max)
    bp_rai = st.slider("🌾 " + ("พื้นที่นา (ไร่)" if TH else "Total Farmland (rai)"), rai_min, rai_max, rai_def_adj, key="bp_rai")
    bp_straw_avail = round(bp_rai * 650 * straw_mult)
    hub_need = round(scaled_cap * bp_days)
    cap_pct = min(100, round(bp_straw_avail / hub_need * 100))
    if cap_pct >= 100:
        st.success(f"✅ {bp_rai} rai × {straw_mult}× = {bp_straw_avail:,} kg — **enough** ({hub_need:,} needed)")
    else:
        st.warning(f"⚠️ {bp_rai} rai = {bp_straw_avail:,} kg — **{cap_pct}%**. Need {rai_for_full} rai.")

    # Product mix
    bp_plates, bp_bowls, bp_trays, bp_containers = 40, 30, 20, 10
    bp_radius = 15

    st.divider()
    st.markdown("#### 🔧 " + ("ปรับแต่ง" if TH else "Optimizers"))
    bp_yield = st.slider("🏭 " + ("เพิ่ม yield" if TH else "Yield Boost (longer soak)"), 0, 15, 0, key="bp_yb")
    bp_bulk = st.checkbox("📋 " + ("สัญญาขายส่ง +50%" if TH else "Bulk Contract (+50% pricing)"), key="bp_bk")
    bp_auto_mix = st.checkbox("🍽️ " + ("ผสมอัตโนมัติ" if TH else "Auto-Optimize Product Mix"), key="bp_am")
    bp_transport = st.slider("🚛 " + ("ระยะส่ง km" if TH else "Delivery Distance (km)"), 0, 50, 0, key="bp_tk")

    st.divider()
    st.markdown("#### 📈 " + ("เพิ่มรายได้" if TH else "Revenue Boosters"))
    bp_brand = st.checkbox("🏷️ " + ("พิมพ์โลโก้ +40%" if TH else "Brand Printing (+40%)"), key="bp_br")
    bp_export = st.checkbox("🇯🇵 " + ("ส่งออก 3x" if TH else "Export Market (3× price)"), key="bp_ex")
    bp_cert = st.checkbox("📜 " + ("ใบรับรอง +25%" if TH else "Compostable Cert (+25%)"), key="bp_ce")
    bp_deliv = st.checkbox("🛵 " + ("พาร์ทเนอร์เดลิเวอรี่" if TH else "Delivery Partner (+30%)"), key="bp_dl")


    st.divider()
    with st.expander("💼 " + ("นักลงทุน/แพลตฟอร์ม" if TH else "Investor / Platform Scale-Up"), expanded=False):
        st.caption("ถ้ามีคนลงทุนให้ — จะแบ่งกำไรยังไง?" if TH else
                   "Choose your investor model — how profits split between you (platform) and the farmer.")
        bp_finance = st.radio("💰 " + ("โมเดล" if TH else "Model"),
                             ['revenue_share', 'installment_distro'],
                             format_func=lambda x: {
                                 'revenue_share': '🤝 Profit Split (investor takes % forever)',
                                 'installment_distro': '📦 Installment + Distribution (payback → you distribute)'}[x], key="bp_fin")
        if bp_finance == 'revenue_share':
            bp_share = st.slider("📊 " + ("ส่วนนักลงทุน %" if TH else "Investor Cut %"), 10, 50, 35, key="bp_sh")
            st.caption(f"Investor gets {bp_share}% of profit → You keep {100-bp_share}%")
        else:
            bp_share = 35
            st.caption("**Phase 1 (Months 1-10):** Farmer pays back equipment monthly.\n"
                       "**Phase 2 (Month 11+):** You earn **25% distribution margin** on all sales forever.\n"
                       "Farmer owns equipment, earns 75%. You earn 25% for managing orders & delivery.")
        bp_hubs = st.slider("🏭 " + ("ขยายกี่ฮับ" if TH else "Scale to N hubs"), 1, 50, 5, key="bp_nh")
        st.caption(f"Projection: what if the investor sets up {bp_hubs} hubs like yours?")

        st.divider()
        st.markdown("##### 💎 " + ("นักลงทุน Angel" if TH else "Angel Investor Model"))
        bp_inv_amount = st.number_input("💰 Investment (฿)", min_value=100000, max_value=20000000,
                                         value=2000000, step=500000, key="bp_inv_amt")
        bp_inv_equity = st.slider("📊 " + ("สัดส่วนหุ้น %" if TH else "Equity Given %"), 5, 50, 20, key="bp_inv_eq")
        bp_inv_opex_pct = st.slider("🏢 " + ("ค่าดำเนินการ %" if TH else "Platform Operating Cost %"), 5, 40, 20, key="bp_inv_opex")
        st.caption(f"Investor puts ฿{bp_inv_amount:,} → gets {bp_inv_equity}% equity. "
                   f"You keep {100-bp_inv_equity}% and run the platform.")


r = compute_bio_packaging_hub(
    tier=bp_tier,
    total_rai=bp_rai,
    straw_buy_price=0,
    second_crop=bp_2crop,
    pct_plates=bp_plates, pct_bowls=bp_bowls, pct_trays=bp_trays,
    pct_containers=max(0, bp_containers),
    auto_mix=bp_auto_mix,
    days_per_year=bp_days,
    work_hours_per_day=bp_hours,
    yield_boost=bp_yield,
    bulk_contract=bp_bulk,
    transport_km=bp_transport,
    opt_family_labor=True, opt_solar_drying=True,
    opt_biomass_fuel=True, opt_automation=True,
    opt_batch_schedule=True,
    opt_branding=bp_brand, opt_export=bp_export,
    opt_certification=bp_cert, opt_delivery=bp_deliv,
    opt_custom_molds=True, opt_seed_trays=True,
    opt_egg_cartons=True, opt_coconut_blend=True,
    opt_sell_training=True,
    process_method='lime', service_radius_km=bp_radius,
    financing_model=bp_finance, revenue_share_pct=bp_share, n_hubs=bp_hubs,
)

with col2:
    # Hero metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("💰 Investment", f"฿{r['investment']:,}")
    with m2:
        profit_color = "normal" if r['profit'] >= 0 else "inverse"
        st.metric("📈 Annual Profit", f"฿{r['profit']:,}")
    with m3:
        st.metric("🔄 ROI", f"{r['roi']}×/yr")
    with m4:
        st.metric("⏱️ Breakeven", f"Mo {r['breakeven_months']}" if r['breakeven_months'] < 999 else "N/A")

    st.divider()

    # Tier-specific image and description
    _img_dir = os.path.join(os.path.dirname(__file__), 'images')
    _bp_img_map = {'micro': 'bp_micro.png', 'starter': 'bp_starter.png', 'mid': 'bp_mid.png', 'industrial': 'bp_industrial.png'}
    _bp_img_path = os.path.join(_img_dir, _bp_img_map[bp_tier])
    if os.path.exists(_bp_img_path):
        st.image(_bp_img_path, use_container_width=True)

    # Tier detail descriptions
    if bp_tier == 'micro':
        st.markdown("### 🔧 " + ("ไมโครฮับ — ทำเองที่บ้าน" if TH else "Micro Hub — DIY at Home"))
        dt1, dt2 = st.columns(2)
        with dt1:
            st.markdown("""
**Equipment:**
- 🔧 Repurposed cement mixer (pulper)
- 🏭 Car jack hydraulic press + heated plate
- 🧱 Concrete molds (4 shapes)
- ☀️ Fan + clear roof drying racks
- 🪣 Lime water soak tank

**Capacity:** 80 kg straw/day → ~52 kg product
""")
        with dt2:
            st.markdown("""
**Best for:**
- 👨‍🌾 Any farmer who wants to START
- 💰 Lowest entry: **฿50,000** only
- ⏱️ 4 hrs/day part-time work
- 🌾 Uses off-season time productively

**Why this works:**
- ✅ Cement mixer = ฿15K vs ฿60K pulper
- ✅ Concrete molds = ฿500 vs ฿5,000 CNC
- ✅ Car jack press = ฿8K vs ฿80K hydraulic
- ✅ 3-month payback with family labor
""")
    elif bp_tier == 'starter':
        st.markdown("### 🌱 " + ("ระดับเริ่มต้น — โรงเรือนเปิดริมนา" if TH else "Starter — Open-Air Workshop"))
        dt1, dt2 = st.columns(2)
        with dt1:
            st.markdown("""
**Equipment:**
- 🔧 Manual hand-crank straw pulper
- 🏭 Single mold press (1 cavity)
- ☀️ Bamboo solar drying racks
- 🪣 Water tank + NaOH bath

**Capacity:** 200 kg straw/day → ~100 kg product
""")
        with dt2:
            st.markdown("""
**Best for:**
- 👨‍🌾 Family-run at rice mill
- 💰 Lowest entry cost (฿200K)
- 🎓 Learning the process first
- 📦 Local market supply (restaurants, markets)

**Limitations:**
- ⚠️ Weather-dependent (sun drying)
- ⚠️ Slow — manual pressing
- ⚠️ Less consistent quality
""")

    elif bp_tier == 'mid':
        st.markdown("### ⚖️ " + ("ระดับกลาง — โรงงานขนาดเล็ก" if TH else "Mid-Scale — Small Factory"))
        dt1, dt2 = st.columns(2)
        with dt1:
            st.markdown("""
**Equipment:**
- 🔧 Semi-auto pulping machine
- 🏭 4-station mold press (conveyor)
- 🔥 Gas-fired drying chamber (180°C)
- ♨️ Hot press finishing station
- 📊 Basic quality control

**Capacity:** 500 kg straw/day → ~280 kg product
""")
        with dt2:
            st.markdown("""
**Best for:**
- 🏢 Co-op or small business
- 📈 Serious commercial operation
- 🌧️ All-weather production (indoor drying)
- 🛒 Supply hotels, restaurants, chains

**Advantages over Starter:**
- ✅ 2.5× faster production
- ✅ Consistent quality (controlled drying)
- ✅ Hot press = waterproof finish
- ✅ Can run year-round
""")

    else:  # industrial
        st.markdown("### 🏭 " + ("ระดับอุตสาหกรรม — โรงงานเต็มรูปแบบ" if TH else "Industrial — Full Factory"))
        dt1, dt2 = st.columns(2)
        with dt1:
            st.markdown("""
**Equipment:**
- 🔧 Full auto industrial pulper
- 🏭 Multi-cavity rotary mold press
- 🔥 Tunnel dryer with conveyor belt
- ✂️ Automated trimming & stacking
- 📊 QC station + lab testing
- ☀️ Solar panels on roof
- 🚛 Loading dock

**Capacity:** 2,000 kg straw/day → ~1,200 kg product
""")
        with dt2:
            st.markdown("""
**Best for:**
- 🏢 Export-grade operation
- 🌍 Large-scale: hotels, airlines, supermarkets
- 🇯🇵 International buyers (Japan, EU)
- 📜 Certification-ready (FDA, compostable)

**Advantages:**
- ✅ 10× Starter capacity
- ✅ 85% yield (vs 70% Starter)
- ✅ Automated = lower cost per piece
- ✅ Premium quality for export
- ✅ Can absorb straw from 100+ farmers
""")


    # ─── Standard Plan ───
    with st.expander("✅ " + ("แผนมาตรฐาน — รวมอะไรบ้าง" if TH else "Standard Plan — What's Included"), expanded=False):
        st.markdown("""
| Optimizer | Savings | How It Works |
|-----------|---------|-------------|
| 🍋 **Lime Water Process** | -80% chemicals | Soak in lime ฿5/kg instead of NaOH ฿40/kg. Same quality, food-safe |
| 👨‍👩‍👧 **Family Labor** | -100% wages | Owner + family operate. No hired workers needed |
| ☀️ **Solar Drying** | -60% energy | Bamboo racks + clear roof. Sun dries for free |
| 🔥 **Biomass Fuel** | -30% energy | Burn waste straw in brick stove for heating |
| 🤖 **Automation** | -1 worker | Car jack press + timer = less manual work |
| 📅 **Batch Scheduling** | -15% energy | Batch runs instead of all-day idling |

> 💡 All optimizers are **included by default** because they require minimal or zero extra investment and dramatically reduce costs.
        """)

    # ═══════════════════════════════════════
    # TABS
    # ═══════════════════════════════════════
    tab_story, tab_econ, tab_health, tab_season, tab_cover, tab_hours, tab_whatif, tab_platform = st.tabs([
        "📖 " + ("เรื่องราว" if TH else "Story"),
        "📊 " + ("เศรษฐกิจ" if TH else "Economics"),
        "🏥 " + ("สุขภาพ" if TH else "Health"),
        "📅 " + ("ปฏิทิน" if TH else "Calendar"),
        "🗺️ " + ("พื้นที่" if TH else "Coverage"),
        "⏱️ " + ("ชั่วโมง" if TH else "Hours"),
        "🔮 " + ("จำลอง" if TH else "What-If"),
        "💼 " + ("แพลตฟอร์ม" if TH else "Platform"),
    ])

    # ═══════════ TAB 0: STORY ═══════════
    _story_dir = os.path.join(os.path.dirname(__file__), 'images', 'storyboard')
    with tab_story:
        h = r['health']
        prod = r['production']
        fi = r['farmer_income']
        wh = r['work_hours']

        # ── Act 1: The Problem ──
        st.markdown("## 🔥 Act 1: The Problem")
        st.markdown("*Every year, Thai farmers burn 25 million tons of rice straw. The smoke chokes cities, fills hospitals, and destroys soil.*")
        a1c1, a1c2 = st.columns(2)
        with a1c1:
            _p = os.path.join(_story_dir, '01_burning.png')
            if os.path.exists(_p): st.image(_p, caption="Burning straw: the free raw material going up in smoke", use_container_width=True)
            st.error(f"🔥 Your {fi['straw_from_farm']:,} kg of straw = **{h['co2_prevented']} tons CO₂** if burned")
        with a1c2:
            _p = os.path.join(_story_dir, '02_health.png')
            if os.path.exists(_p): st.image(_p, caption="PM2.5 crisis: Chiang Mai and rural hospitals overflow every burning season", use_container_width=True)
            st.error(f"😷 Prevents **{h['pm25_prevented_kg']} kg PM2.5** — saves **฿{h['healthcare_savings']:,}/yr** in healthcare")

        st.divider()

        # ── Act 2: The Raw Material ──
        st.markdown("## 🌾 Act 2: Free Raw Material")
        st.markdown("*After harvest, straw is just sitting there. Instead of burning it — collect it. It's FREE.*")
        a2c1, a2c2 = st.columns(2)
        with a2c1:
            _p = os.path.join(_story_dir, '03_harvest.png')
            if os.path.exists(_p): st.image(_p, caption="Golden rice harvest — straw bales ready for collection", use_container_width=True)
            st.success(f"🌾 Your {fi['total_rai']} rai produces **{fi['straw_from_farm']:,} kg** of free straw per year")
        with a2c2:
            _p = os.path.join(_story_dir, '04_collect.png')
            if os.path.exists(_p): st.image(_p, caption="Simple collection — load onto truck, bring to workshop", use_container_width=True)
            st.success(f"📦 Hub needs only **{fi['hub_needs']:,} kg** — you have {fi['farm_utilization']}% utilization")

        st.divider()

        # ── Act 3: The Process ──
        _tier_labels = {'micro': '🔧 Micro Hub', 'starter': '🌱 Starter', 'mid': '⚖️ Mid-Scale', 'industrial': '🏭 Industrial'}
        _tier_invest = {'micro': '฿50K', 'starter': '฿200K', 'mid': '฿500K', 'industrial': '฿1.5M'}
        st.markdown(f"## 🏭 Act 3: The Process — {_tier_labels[bp_tier]}")
        st.markdown(f"*Your **{_tier_labels[bp_tier]}** setup ({_tier_invest[bp_tier]}) — here's how it works step by step.*")

        # Step 1: Chop — tier-aware
        st.markdown("### Step 1: 🌾 Chop the Straw")
        _chop_desc = {
            'micro': '⭐️ 15 min — Use garden shears or a manual chaff cutter (฿500). Cut straw into 2-3cm strips by hand.',
            'starter': '⭐️ 15 min — Feed straw into a repurposed animal feed chopper (฿5K). Same machine farmers already have.',
            'mid': '⭐️ 10 min — Electric straw shredder (฿15K) processes batches automatically. Just dump and press start.',
            'industrial': '⭐️ 5 min — Auto-feed conveyor shredder line. Continuous flow, no manual handling.',
        }
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            _p = os.path.join(_story_dir, '05_chop.png')
            if os.path.exists(_p): st.image(_p, caption="Chop straw into small pieces", use_container_width=True)
        with sc2:
            st.info(f"**⏱️ Chopping**\n\n{_chop_desc[bp_tier]}")

        # Step 2: Lime Soak — tier-aware
        st.markdown("### Step 2: 🍋 Lime Soak Overnight")
        _soak_desc = {
            'micro': 'Use plastic bins or old water tanks. Soak overnight.',
            'starter': 'Concrete trough (฿2K). Soak 50-100 kg batches overnight.',
            'mid': 'Soaking vats with drain valves. 200+ kg per batch.',
            'industrial': 'Stainless tanks with agitation. Automated fill/drain.',
        }
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            _p = os.path.join(_story_dir, '06_soak.png')
            if os.path.exists(_p): st.image(_p, caption="Submerge in lime water overnight", use_container_width=True)
        with sc2:
            st.info(f"**⏱️ Overnight (set & forget)**\n\n{_soak_desc[bp_tier]}\n\nLime costs only **฿{r['costs']['chemicals']:,}/yr**.")

        # Step 3: Mix — tier-specific
        st.markdown("### Step 3: 🔄 Mix into Pulp")
        _mix_cap = {'micro': 'Cement mixer + tapioca starch = smooth pulp ready for pressing',
                    'starter': 'Hand-crank pulper — simple, manual, gets the job done',
                    'mid': 'Semi-auto motorized pulper — 2 workers, 2.5× faster',
                    'industrial': 'Full auto industrial pulper with digital controls — massive throughput'}
        _mix_info = {'micro': '**⏱️ 1 hour**\n\nA ฿15K cement mixer does what a ฿60K pulper does. Add tapioca starch as binder — ฿25/kg.',
                     'starter': '**⏱️ 2-4 hours**\n\nManual hand-crank pulper (฿30K). Slower but reliable. Add tapioca starch as binder.',
                     'mid': '**⏱️ 30 min**\n\nMotorized pulper (฿80K) with electric motor. Two workers feed straw in, pulp comes out. 2.5× faster than manual.',
                     'industrial': '**⏱️ Continuous**\n\nFully automated pulper with conveyor feed and touchscreen controls. Workers monitor, machine does the work.'}
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            _p = os.path.join(_story_dir, f'07_mix_{bp_tier}.png')
            if os.path.exists(_p): st.image(_p, caption=_mix_cap[bp_tier], use_container_width=True)
        with sc2:
            st.info(_mix_info[bp_tier])

        # Step 4: Press — tier-specific
        st.markdown("### Step 4: 🏭 Press into Shape")
        total_pcs = sum(p['pieces'] for p in r['products'])
        _press_cap = {'micro': 'Car jack press + concrete mold = perfect plates every time',
                      'starter': 'Single-cavity lever press — one piece at a time, simple and reliable',
                      'mid': '4-station hydraulic press with conveyor — 4 pieces at once!',
                      'industrial': 'Multi-cavity rotary press with robotic arm — 8+ pieces simultaneously'}
        _press_info = {'micro': f'**⏱️ 30 sec/piece**\n\nCar jack press (฿8K) + concrete molds (฿500 each). You make **{total_pcs:,} pieces/yr**.',
                       'starter': f'**⏱️ 30 sec/piece**\n\nSingle lever press (฿30K) with metal mold. One cavity — consistent quality. **{total_pcs:,} pieces/yr**.',
                       'mid': f'**⏱️ 8 sec/piece**\n\n4-station hydraulic press (฿150K) with conveyor. Heated plates for waterproof finish. **{total_pcs:,} pieces/yr**.',
                       'industrial': f'**⏱️ 3 sec/piece**\n\nRotary press (฿500K) pressing 8 cavities. Robotic stacking. Automated QC. **{total_pcs:,} pieces/yr**.'}
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            _p = os.path.join(_story_dir, f'08_press_{bp_tier}.png')
            if os.path.exists(_p): st.image(_p, caption=_press_cap[bp_tier], use_container_width=True)
        with sc2:
            st.info(_press_info[bp_tier])

        # Step 5: Dry — tier-specific
        _dry_titles = {'micro': 'Step 5: ☀️ Fan Dry', 'starter': 'Step 5: ☀️ Sun Dry', 'mid': 'Step 5: 🔥 Gas Dry', 'industrial': 'Step 5: 🔥 Tunnel Dry'}
        st.markdown(f"### {_dry_titles[bp_tier]}")
        _dry_cap = {'micro': 'Bamboo racks under clear roof — sun and fan dry for free',
                    'starter': 'Open-air bamboo drying racks — weather dependent but zero cost',
                    'mid': 'Gas-fired drying chamber at 180°C — all-weather, consistent results',
                    'industrial': 'Tunnel dryer with conveyor — continuous, automated, export-grade'}
        _dry_info = {'micro': f'**⏱️ 2-4 hours**\n\nFan + clear polycarbonate roof = free drying. Saves **฿{r["savings"]["energy"]:,}/yr** vs electric dryers.',
                     'starter': f'**⏱️ 4-6 hours**\n\nDirect sunlight on bamboo mats. Free but weather-dependent. Rainy season = slower. Saves **฿{r["savings"]["energy"]:,}/yr**.',
                     'mid': f'**⏱️ 20-30 min**\n\nGas drying chamber at 180°C. All-weather, year-round. Hot press finishing for waterproof surface.',
                     'industrial': f'**⏱️ Continuous**\n\nTunnel dryer with conveyor belt. Products in one end, dried and boxed the other. Solar panels on roof offset energy.'}
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            _p = os.path.join(_story_dir, f'09_dry_{bp_tier}.png')
            if os.path.exists(_p): st.image(_p, caption=_dry_cap[bp_tier], use_container_width=True)
        with sc2:
            st.info(_dry_info[bp_tier])

        # Step 6: Finished!
        st.markdown("### Step 6: ✅ Finished Products")
        _p = os.path.join(_story_dir, '10_finish.png')
        if os.path.exists(_p): st.image(_p, caption="Beautiful, premium bio-packaging — plates, bowls, trays, containers", use_container_width=True)
        st.success(f"📦 **{prod['finished_after_qc']:,} kg/yr** of finished products | 95% QC pass rate | Ready to sell!")

        st.divider()

        # ── Act 4: The Result ──
        st.markdown("## 💰 Act 4: The Result")
        st.markdown("*Your straw waste is now premium eco-packaging. Restaurants love it. You earn more than factory wages.*")
        a4c1, a4c2 = st.columns(2)
        with a4c1:
            _p = os.path.join(_story_dir, '11_selling.png')
            if os.path.exists(_p): st.image(_p, caption="Thai street food served on your bio-packaging — customers love it", use_container_width=True)
            st.success(f"💰 **Revenue: ฿{r['revenue']:,}/yr** — Restaurants, markets, hotels all want this")
        with a4c2:
            _p = os.path.join(_story_dir, '12_farmer.png')
            if os.path.exists(_p): st.image(_p, caption="A farming family's new income stream — from waste to wealth", use_container_width=True)
            st.success(f"🏆 **Profit: ฿{r['profit']:,}/yr** = **฿{wh['baht_per_hr']:,}/hr** — better than factory wages!")

        st.divider()
        st.markdown(f"""
### 📊 Your Numbers at a Glance
| Metric | Value |
|--------|-------|
| 💰 Investment | **฿{r['investment']:,}** |
| 📈 Annual Profit | **฿{r['profit']:,}** |
| 🔄 ROI | **{r['roi']}×/yr** |
| ⏱️ Breakeven | **{r['breakeven_months']} months** |
| 💵 Per Hour | **฿{wh['baht_per_hr']:,}/hr** |
| 🌍 CO₂ Saved | **{h['co2_prevented']} tons/yr** |
""")
        st.info("👆 **Adjust the settings in the sidebar** to see how the numbers change. Check the other tabs for detailed economics, health impact, and more.")

    # ═══════════ TAB 1: ECONOMICS ═══════════
    with tab_econ:
        st.subheader("🔄 " + ("กระบวนการผลิต" if TH else "Production Flow"))
        prod = r['production']
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            st.metric("🌾 Straw In", f"{prod['straw_used']:,} kg/yr")
            st.caption(f"Capacity: {prod['utilization']}%")
        with fc2:
            st.metric("🧪 Pulp", f"{prod['pulp_kg']:,} kg")
        with fc3:
            st.metric("📦 Finished", f"{prod['finished_kg']:,} kg")
        with fc4:
            total_pieces = sum(p['pieces'] for p in r['products'])
            st.metric("🍽️ Pieces", f"{total_pieces:,}/yr")

        st.divider()
        st.subheader("🍽️ " + ("ผลิตภัณฑ์" if TH else "Products"))
        p1, p2 = st.columns(2)
        with p1:
            prod_df = pd.DataFrame([{
                "Product": f"{p['emoji']} {p['name_en']}",
                "kg/yr": f"{p['kg']:,}", "Pieces": f"{p['pieces']:,}",
                "Revenue": f"฿{p['revenue']:,}",
            } for p in r['products']])
            st.dataframe(prod_df, use_container_width=True, hide_index=True)
        with p2:
            fig_prod = go.Figure(go.Pie(
                labels=[f"{p['emoji']} {p['name_en']}" for p in r['products']],
                values=[p['revenue'] for p in r['products']], hole=0.4,
                marker_colors=['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                textinfo='label+percent', textfont_size=12,
            ))
            fig_prod.update_layout(height=280, template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_prod, use_container_width=True)

        st.divider()
        st.subheader("💰 " + ("รายรับ vs ต้นทุน" if TH else "Revenue vs Costs"))
        rv1, rv2 = st.columns(2)
        c = r['costs']
        with rv1:
            st.metric("📈 Revenue", f"฿{r['revenue']:,}/yr")
            cost_df = pd.DataFrame([
                {"Cost": "🌾 Straw", "฿/yr": f"฿{c['straw']:,}"},
                {"Cost": "👷 Labor", "฿/yr": f"฿{c['labor']:,}"},
                {"Cost": "⚡ Energy", "฿/yr": f"฿{c['energy']:,}"},
                {"Cost": "🧪 Chemicals", "฿/yr": f"฿{c['chemicals']:,}"},
                {"Cost": "🔧 Maintenance", "฿/yr": f"฿{c['maintenance']:,}"},
                {"Cost": "📦 Packaging", "฿/yr": f"฿{c['packaging']:,}"},
                {"Cost": "**TOTAL**", "฿/yr": f"**฿{c['total']:,}**"},
            ])
            st.dataframe(cost_df, use_container_width=True, hide_index=True)
        with rv2:
            fig_wf = go.Figure(go.Waterfall(
                x=["Revenue", "Straw", "Labor", "Energy", "Chem", "Maint", "Pack", "Profit"],
                y=[r['revenue'], -c['straw'], -c['labor'], -c['energy'], -c['chemicals'], -c['maintenance'], -c['packaging'], r['profit']],
                measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
                connector={"line": {"color": "rgba(255,255,255,0.1)"}},
                increasing={"marker": {"color": "#10b981"}}, decreasing={"marker": {"color": "#ef4444"}},
                totals={"marker": {"color": "#3b82f6" if r['profit'] >= 0 else "#ef4444"}},
                text=[f"฿{abs(v):,}" for v in [r['revenue'], -c['straw'], -c['labor'], -c['energy'], -c['chemicals'], -c['maintenance'], -c['packaging'], r['profit']]],
                textposition="outside", textfont=dict(size=10, color='white'),
            ))
            fig_wf.update_layout(height=350, template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=20, b=10))
            st.plotly_chart(fig_wf, use_container_width=True)

        # Savings
        s = r['savings']
        if s['total'] > 0:
            st.success(f"💡 **Cost Savings: ฿{s['total']:,}/yr**")
            sv1, sv2, sv3 = st.columns(3)
            with sv1:
                st.metric("👷 Labor Saved", f"฿{s['labor']:,}/yr",
                         delta=f"-{round(s['labor']/max(s['base_labor'],1)*100)}%" if s['labor'] > 0 else None)
            with sv2:
                st.metric("⚡ Energy Saved", f"฿{s['energy']:,}/yr",
                         delta=f"-{round(s['energy']/max(s['base_energy'],1)*100)}%" if s['energy'] > 0 else None)
            with sv3:
                st.metric("📈 Profit Boost", f"+฿{s['total']:,}/yr", delta="Extra profit")

        # Revenue & Profit Boosts
        all_boosts = r['revenue_boosts'] + r['zero_cost_boosts']
        if all_boosts:
            st.divider()
            total_boost = sum(b['boost'] for b in all_boosts)
            total_extra = sum(b.get('invest', 0) for b in all_boosts)
            st.subheader("📈 " + ("รายได้เสริม" if TH else f"All Boosts: +฿{total_boost:,}/yr"))

            # Zero-cost (always active)
            if r['zero_cost_boosts']:
                st.markdown("**✅ " + ("รวมในแผน (฿0)" if TH else "Included Free (Standard Plan)") + ":**")
                for zb in r['zero_cost_boosts']:
                    st.success(f"{zb['name']}: **+฿{zb['boost']:,}/yr** — {zb['desc']}")

            # User-toggled
            if r['revenue_boosts']:
                st.markdown("**🎯 " + ("เลือกเพิ่ม" if TH else "Your Selected Extras") + ":**")
                for rb in r['revenue_boosts']:
                    inv_str = f" *(invest ฿{rb['invest']:,})*" if rb['invest'] > 0 else ""
                    st.info(f"{rb['name']}: **+฿{rb['boost']:,}/yr**{inv_str}\n\n{rb.get('desc', '')}")

        # Farmer Income
        st.divider()
        fi = r['farmer_income']
        st.subheader("🌾 " + ("ฟาร์ม & รายได้" if TH else "Farm Capacity & Income"))
        fi1, fi2 = st.columns(2)
        with fi1:
            st.metric("🌾 Farm Supply", f"{fi['straw_from_farm']:,} kg/yr")
            st.metric("🏭 Hub Needs", f"{fi['hub_needs']:,} kg/yr")
            st.caption(f"Farm utilization: {fi['farm_utilization']}% | QC reject: {fi['qc_reject_pct']}%")
        with fi2:
            st.metric("🌾 Rice Income", f"฿{fi['rice_income']:,}/yr")
            st.metric("📦 Packaging (your share)", f"฿{fi['packaging_profit']:,}/yr")
            if fi['platform_cut'] > 0:
                st.caption(f"Platform takes: ฿{fi['platform_cut']:,}/yr")
            st.metric("💰 **Total**", f"฿{fi['total']:,}/yr", delta=f"฿{fi['monthly']:,}/mo")

        with st.expander("📊 Compare All Tiers"):
            tier_df = pd.DataFrame([{
                "Tier": ti['name'], "Investment": f"฿{ti['investment']:,}",
                "Capacity": ti['capacity'], "Workers": ti['workers'],
                "Revenue": f"฿{ti['revenue']:,}", "Profit": f"฿{ti['profit']:,}", "ROI": f"{ti['roi']}×",
            } for ti in r['all_tiers']])
            st.dataframe(tier_df, use_container_width=True, hide_index=True)

        st.divider()
        # ─── Download Summary ───
        _summary = f"""╔══════════════════════════════════════════╗
║   BIO-PACKAGING HUB — FEASIBILITY REPORT   ║
╚══════════════════════════════════════════╝

📦 Equipment Tier:    {r['tier']['name']}
🏗️ Total Investment:  ฿{r['investment']:,}
🌾 Farmland:          {fi['total_rai']} rai ({'2 crops' if bp_2crop else '1 crop'})
⏱️ Schedule:           {bp_hours}h/day × {bp_days} days/yr

────────── ANNUAL FINANCIALS ──────────
📈 Revenue:     ฿{r['revenue']:,}/yr
📉 Costs:       ฿{r['costs']['total']:,}/yr
💰 Profit:      ฿{r['profit']:,}/yr
🔄 ROI:         {r['roi']}× (annual)
⏱️ Break-Even:   Month {r['breakeven_months']}

────────── PRODUCTION ──────────
🌾 Straw used:         {r['production']['straw_used']:,} kg/yr
📦 Finished product:   {r['production']['finished_after_qc']:,} kg/yr
🏭 Utilization:        {r['production']['utilization']}%
❌ QC reject:           {r['production']['qc_reject_pct']}%

────────── FARMER INCOME ──────────
🌾 Rice farming:       ฿{fi['rice_income']:,}/yr
📦 Packaging profit:   ฿{fi['packaging_profit']:,}/yr
💰 Total:              ฿{fi['total']:,}/yr (฿{fi['monthly']:,}/mo)

────────── HEALTH IMPACT ──────────
🚫 Straw diverted:     {r['health']['straw_diverted_tons']} tons
🌍 CO₂ prevented:      {r['health']['co2_prevented']} tons
😷 PM2.5 prevented:    {r['health']['pm25_prevented_kg']} kg
👥 People benefited:   {r['health']['people_benefit']}

────────── PRODUCTS ──────────
""" + "\n".join([f"  {p['emoji']} {p['name_en']}: {p['kg']:,} kg → {p['pieces']:,} pcs → ฿{p['revenue']:,}/yr" for p in r['products']]) + f"""

────────── COST BREAKDOWN ──────────
  🌾 Raw material:    ฿{c['straw']:,}
  👷 Labor:           ฿{c['labor']:,}
  ⚡ Energy:           ฿{c['energy']:,}
  🧪 Chemicals:       ฿{c['chemicals']:,}
  🔧 Maintenance:     ฿{c['maintenance']:,}
  📦 Packaging:       ฿{c['packaging']:,}
  💧 Water:           ฿{c['water']:,}
  📉 Depreciation:    ฿{c['depreciation']:,}

Generated: Bio-Packaging Hub Simulator
"""
        st.download_button(
            "📥 " + ("ดาวน์โหลดสรุป" if TH else "Download Summary Report"),
            _summary, file_name="bio_packaging_report.txt",
            mime="text/plain", use_container_width=True,
        )

    # ═══════════ TAB 2: HEALTH ═══════════
    with tab_health:
        st.subheader("🏥 " + ("ผลกระทบต่อสุขภาพ" if TH else "Health Impact"))
        h = r['health']
        h1, h2, h3, h4 = st.columns(4)
        with h1:
            st.metric("🌾 Straw Diverted", f"{h['straw_diverted_tons']} t")
        with h2:
            st.metric("🌍 CO₂ Prevented", f"{h['co2_prevented']} t")
        with h3:
            st.metric("😷 PM2.5 Prevented", f"{h['pm25_prevented_kg']} kg")
        with h4:
            st.metric("👥 People Benefit", f"{h['people_benefit']:,}")
        h5, h6 = st.columns(2)
        with h5:
            st.metric("🏥 Healthcare Saved", f"฿{h['healthcare_savings']:,}/yr", delta="Fewer hospital visits")
        with h6:
            st.metric("🌿 Carbon Credits", f"฿{h['carbon_credit']:,}/yr", delta="T-VER eligible")
        total_soc = r['profit'] + h['healthcare_savings'] + h['carbon_credit']
        st.success(f"🏆 **Total Societal Value: ฿{total_soc:,}/yr** = Profit ฿{r['profit']:,} + Health ฿{h['healthcare_savings']:,} + Carbon ฿{h['carbon_credit']:,}")

    # ═══════════ TAB 3: CALENDAR ═══════════
    with tab_season:
        st.subheader("📅 " + ("ปฏิทินการผลิต" if TH else "Monthly Production Calendar"))
        st.markdown("> " + ("ผลิตช่วงว่างจากนา — ไม่ขัดกัน!" if TH else "Production fits farming off-season!"))
        sn = r['seasonal']
        fig_cal = go.Figure()
        fig_cal.add_trace(go.Bar(
            x=[s['month'] for s in sn], y=[s['pieces'] for s in sn],
            name="📦 Pieces", marker_color=['#10b981' if s['pack_days'] > 10 else '#f59e0b' if s['pack_days'] > 5 else '#ef4444' for s in sn],
            text=[f"{s['pieces']:,}" for s in sn], textposition='outside', textfont=dict(size=10, color='white'),
        ))
        peak_val = max(ss['pieces'] for ss in sn) if sn else 1
        fig_cal.add_trace(go.Scatter(
            x=[s['month'] for s in sn], y=[s['farm_busy'] * peak_val for s in sn],
            name="🌾 Farm Busy", line=dict(color='#ef4444', width=2, dash='dot'),
        ))
        fig_cal.update_layout(height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=-0.15),
            margin=dict(t=20, b=40), yaxis_title="Pieces/month")
        st.plotly_chart(fig_cal, use_container_width=True)
        cal_df = pd.DataFrame([{
            "Month": s['month'], "🌾 Farm": f"{round(s['farm_busy']*100)}%",
            "📦 Days": s['pack_days'], "⏱️ Hrs": s['work_hrs'],
            "🍽️ Pcs": f"{s['pieces']:,}", "☀️": "☀️" * round(s['solar'] * 3),
        } for s in sn])
        st.dataframe(cal_df, use_container_width=True, hide_index=True)
        wh = r['work_hours']
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            st.metric("📅 Work Days/yr", f"{wh['total_days']}")
        with tc2:
            st.metric("⏱️ Total Hrs/yr", f"{wh['total_hrs']}")
        with tc3:
            st.metric("🍽️ Pieces/yr", f"{wh['total_pieces']:,}")
        st.info("💡 **Feb-May is peak** — no farming, great sun. Jun-Jul off (planting).")

    # ═══════════ TAB 4: COVERAGE ═══════════
    with tab_cover:
        st.subheader("🌾 " + ("ฟาร์ม & ตลาด" if TH else "Your Farm & Market"))
        cov = r['coverage']
        prod = r['production']
        fi = r['farmer_income']

        # Your Farm
        st.markdown("#### 🌾 " + ("ฟาร์มของคุณ" if TH else "Your Farm"))
        f1, f2, f3 = st.columns(3)
        with f1:
            st.metric("🌾 Your Straw", f"{fi['straw_from_farm']:,} kg/yr")
        with f2:
            st.metric("🏭 Hub Uses", f"{fi['hub_needs']:,} kg/yr")
        with f3:
            excess = fi['straw_from_farm'] - fi['hub_needs']
            if excess > 0:
                st.metric("📦 Excess", f"{excess:,} kg", delta="sell as mulch ฿2/kg")
            else:
                st.metric("⚠️ Shortage", f"{abs(excess):,} kg", delta="need more rai")

        st.divider()
        st.markdown("#### 🏭 " + ("ผลผลิต" if TH else "Your Production"))
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("📦 Daily Output", f"{prod['effective_capacity_day']} kg/day")
        with p2:
            st.metric("🍽️ Monthly Pieces", f"{cov['supply_pieces_mo']:,} pcs")
        with p3:
            st.metric("✅ QC Pass", f"{100 - prod['qc_reject_pct']}%")

        st.divider()
        st.markdown("#### 🛒 " + ("ตลาดท้องถิ่น" if TH else "Local Market (15km)"))
        dd1, dd2, dd3 = st.columns(3)
        with dd1:
            st.metric("🍜 Restaurants Nearby", f"{cov['restaurants']}")
        with dd2:
            st.metric("📦 They Need", f"{cov['demand_pieces_mo']:,} pcs/mo")
        with dd3:
            st.metric("🏭 You Make", f"{cov['supply_pieces_mo']:,} pcs/mo")

        met = cov['demand_met_pct']
        if met < 10:
            st.info(f"📈 You cover **{met}%** of local demand — huge room to grow! Scale up hours or tier.")
        elif met < 50:
            st.info(f"📈 You cover **{met}%** — growing well!")
        elif met < 100:
            st.success(f"✅ You cover **{met}%** — great market fit!")
        else:
            st.warning("⚠️ Supply > demand — explore export or delivery partners.")

        fig_rad = go.Figure(go.Indicator(
            mode="gauge+number", value=cov['supply_pieces_mo'],
            title={'text': "Your Supply vs Local Demand (pcs/mo)", 'font': {'size': 14, 'color': 'white'}},
            gauge={'axis': {'range': [0, max(cov['demand_pieces_mo'], cov['supply_pieces_mo']) * 1.2]},
                   'bar': {'color': '#10b981'},
                   'steps': [{'range': [0, cov['demand_pieces_mo']], 'color': 'rgba(239,68,68,0.3)'}],
                   'threshold': {'line': {'color': '#ef4444', 'width': 3}, 'value': cov['demand_pieces_mo']}},
            number={'font': {'color': 'white'}},
        ))
        fig_rad.update_layout(height=250, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=10))
        st.plotly_chart(fig_rad, use_container_width=True)

    # ═══════════ TAB 5: WORK HOURS ═══════════
    with tab_hours:
        st.subheader("⏱️ " + ("ชั่วโมง & รายได้" if TH else "Work Hours & Earnings"))
        wh = r['work_hours']
        wm1, wm2, wm3, wm4 = st.columns(4)
        with wm1:
            st.metric("⏱️ Hrs/Day", f"{wh['hrs_per_day']}")
        with wm2:
            st.metric("📅 Days/Yr", f"{wh['total_days']}")
        with wm3:
            st.metric("⏱️ Total", f"{wh['total_hrs']} hrs/yr")
        with wm4:
            st.metric("💰 ฿/Hour", f"฿{wh['baht_per_hr']:,}", delta="Net profit/hr")

        st.divider()
        st.subheader("🔬 " + ("ขั้นตอนต่อวัน" if TH else "Daily Steps"))
        if r['process_method'] == 'pulp':
            steps = [("🌾 Cut & soak", "30 min"), ("🧪 NaOH pulp", "2-4 hrs"), ("💧 Wash", "1 hr"),
                     ("🔄 Mix", "30 min"), ("🏭 Press", "10s/pc"), ("🔥 Dry", "20-30 min")]
        elif r['process_method'] == 'lime':
            steps = [("🌾 Chop", "15 min"), ("🍋 Lime soak", "Overnight ⏳"), ("🔄 Mixer", "1 hr"),
                     ("🥣 Starch mix", "15 min"), ("🏭 Press", "30s/pc"), ("☀️ Fan dry", "2-4 hrs")]
        else:
            steps = [("🌾 Shred fine", "30 min"), ("🥣 Starch mix", "15 min"),
                     ("🏭 Hot press", "30s/pc"), ("☀️ Cool", "15 min")]
        st.dataframe(pd.DataFrame([{"Step": s[0], "Time": s[1]} for s in steps]),
                    use_container_width=True, hide_index=True)

        method_info = {'pulp': "Best quality. Standard industry.", 'lime': "80% cheaper chemicals! Lime ฿5 vs NaOH ฿40/kg.",
                      'direct': "Skip pulping! Fastest (15 min). Rougher finish."}
        st.info(f"**Method: {r['process_method'].upper()}** — {method_info[r['process_method']]}")

        st.divider()
        st.subheader("📊 " + ("เปรียบเทียบรายได้" if TH else "Earnings vs Jobs"))
        st.dataframe(pd.DataFrame([
            {"Job": "🌾 Rice Farming", "฿/hr": "฿40-60", "Hrs/yr": "~1,500"},
            {"Job": "🏭 Factory Worker", "฿/hr": "฿46 (min wage)", "Hrs/yr": "~2,400"},
            {"Job": "🛵 Grab Driver", "฿/hr": "฿80-120", "Hrs/yr": "~2,000"},
            {"Job": f"📦 **Bio-Pack ({r['tier']['name']})**", "฿/hr": f"**฿{wh['baht_per_hr']:,}**", "Hrs/yr": f"**{wh['total_hrs']}**"},
        ]), use_container_width=True, hide_index=True)
        if wh['baht_per_hr'] > 120:
            st.success(f"🏆 **฿{wh['baht_per_hr']:,}/hr** — Better than most rural jobs!")
        elif wh['baht_per_hr'] > 46:
            st.info(f"👍 ฿{wh['baht_per_hr']:,}/hr — Above minimum wage + flexible.")
        else:
            st.warning(f"⚠️ ฿{wh['baht_per_hr']:,}/hr — Enable optimizers to improve.")

    # ═══════════ TAB 7: WHAT-IF ═══════════
    with tab_whatif:
        st.subheader("📈 " + ("กราฟจุดคุ้มทุน" if TH else "Break-Even Timeline"))
        # Month-by-month cumulative profit
        monthly_profit = r['profit'] / 12
        be_months = []
        cumul = -r['investment']
        for mo in range(1, 37):
            cumul += monthly_profit
            be_months.append({'month': mo, 'cumulative': round(cumul)})
        fig_be = go.Figure()
        fig_be.add_trace(go.Scatter(
            x=[b['month'] for b in be_months],
            y=[b['cumulative'] for b in be_months],
            fill='tozeroy',
            fillcolor='rgba(16,185,129,0.15)',
            line=dict(color='#10b981', width=3),
            name='Cumulative Profit',
        ))
        fig_be.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.4)")
        if r['breakeven_months'] < 999:
            fig_be.add_vline(x=r['breakeven_months'], line_dash="dot", line_color="#f59e0b",
                           annotation_text=f"Break-even: Month {r['breakeven_months']}")
        fig_be.update_layout(height=350, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Month", yaxis_title="Cumulative ฿",
            margin=dict(t=20, b=40), showlegend=False)
        st.plotly_chart(fig_be, use_container_width=True)

        be1, be2, be3 = st.columns(3)
        with be1:
            st.metric("💰 Investment", f"฿{r['investment']:,}")
        with be2:
            st.metric("📈 Monthly Profit", f"฿{round(monthly_profit):,}/mo")
        with be3:
            st.metric("✅ Break-Even", f"Month {r['breakeven_months']}" if r['breakeven_months'] < 999 else "N/A")

        st.divider()

        # ─── Sensitivity Analysis ───
        st.subheader("🔮 " + ("วิเคราะห์ความไว" if TH else "Sensitivity Analysis"))
        st.markdown("*" + ("ถ้าเปลี่ยนตัวแปร — กำไรเปลี่ยนยังไง?" if TH else "How does profit change when key variables shift?") + "*")

        # Run scenarios with different hours
        hrs_scenarios = []
        for h in [2, 3, 4, 5, 6, 8, 10, 12]:
            sc = compute_bio_packaging_hub(
                tier=bp_tier, total_rai=bp_rai, straw_buy_price=0, second_crop=bp_2crop,
                pct_plates=bp_plates, pct_bowls=bp_bowls, pct_trays=bp_trays, pct_containers=bp_containers,
                auto_mix=bp_auto_mix, days_per_year=bp_days, work_hours_per_day=h,
                yield_boost=bp_yield, bulk_contract=bp_bulk, transport_km=bp_transport,
                opt_family_labor=True, opt_solar_drying=True, opt_biomass_fuel=True,
                opt_automation=True, opt_batch_schedule=True,
                opt_branding=bp_brand, opt_export=bp_export, opt_certification=bp_cert, opt_delivery=bp_deliv,
                opt_custom_molds=True, opt_seed_trays=True, opt_egg_cartons=True,
                opt_coconut_blend=True, opt_sell_training=True,
                process_method='lime', service_radius_km=bp_radius,
                financing_model=bp_finance, revenue_share_pct=bp_share, n_hubs=bp_hubs,
            )
            hrs_scenarios.append({'hours': h, 'profit': sc['profit'], 'roi': sc['roi'],
                                 'baht_hr': sc['work_hours']['baht_per_hr'],
                                 'current': h == bp_hours})

        fig_sens = go.Figure()
        colors = ['#10b981' if s['current'] else '#3b82f6' for s in hrs_scenarios]
        fig_sens.add_trace(go.Bar(
            x=[f"{s['hours']}h" for s in hrs_scenarios],
            y=[s['profit'] for s in hrs_scenarios],
            marker_color=colors,
            text=[f"฿{s['profit']:,}" for s in hrs_scenarios],
            textposition='outside', textfont=dict(size=10, color='white'),
        ))
        fig_sens.update_layout(height=300, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Hours/Day", yaxis_title="Annual Profit ฿",
            margin=dict(t=20, b=40), showlegend=False)
        st.plotly_chart(fig_sens, use_container_width=True)
        st.caption("🟢 = your current setting")

        st.dataframe(pd.DataFrame([{
            "⏱️ Hours": f"{s['hours']}h/day {'✅' if s['current'] else ''}",
            "💰 Profit": f"฿{s['profit']:,}/yr",
            "🔄 ROI": f"{s['roi']}×",
            "💵 ฿/hr": f"฿{s['baht_hr']:,}/hr",
        } for s in hrs_scenarios]), use_container_width=True, hide_index=True)

        st.divider()

        # ─── Risk Scenarios ───
        st.subheader("⚡ " + ("สถานการณ์ 3 แบบ" if TH else "Risk Scenarios"))
        scenarios = {
            '😰 Pessimistic': {'hours': max(2, bp_hours - 2), 'days': max(250, bp_days - 50), 'desc': 'Fewer hours, shorter season'},
            '📊 Base Case': {'hours': bp_hours, 'days': bp_days, 'desc': 'Your current settings'},
            '🚀 Optimistic': {'hours': min(12, bp_hours + 2), 'days': min(330, bp_days + 30), 'desc': 'More hours, longer season'},
        }
        scen_cols = st.columns(3)
        for i, (name, sc_params) in enumerate(scenarios.items()):
            sc = compute_bio_packaging_hub(
                tier=bp_tier, total_rai=bp_rai, straw_buy_price=0, second_crop=bp_2crop,
                pct_plates=bp_plates, pct_bowls=bp_bowls, pct_trays=bp_trays, pct_containers=bp_containers,
                auto_mix=bp_auto_mix, days_per_year=sc_params['days'], work_hours_per_day=sc_params['hours'],
                yield_boost=bp_yield, bulk_contract=bp_bulk, transport_km=bp_transport,
                opt_family_labor=True, opt_solar_drying=True, opt_biomass_fuel=True,
                opt_automation=True, opt_batch_schedule=True,
                opt_branding=bp_brand, opt_export=bp_export, opt_certification=bp_cert, opt_delivery=bp_deliv,
                opt_custom_molds=True, opt_seed_trays=True, opt_egg_cartons=True,
                opt_coconut_blend=True, opt_sell_training=True,
                process_method='lime', service_radius_km=bp_radius,
                financing_model=bp_finance, revenue_share_pct=bp_share, n_hubs=bp_hubs,
            )
            with scen_cols[i]:
                st.markdown(f"**{name}**")
                st.caption(f"{sc_params['desc']} ({sc_params['hours']}h, {sc_params['days']}d)")
                st.metric("💰 Profit", f"฿{sc['profit']:,}/yr")
                st.metric("🔄 ROI", f"{sc['roi']}×")
                st.metric("⏱️ Breakeven", f"Mo {sc['breakeven_months']}" if sc['breakeven_months'] < 999 else "N/A")

    # ═══════════ TAB 6: PLATFORM OWNER ═══════════
    with tab_platform:
        pl = r['platform']
        ph = pl['per_hub']
        pt = pl['total']

        st.subheader("💼 " + ("รายได้เจ้าของแพลตฟอร์ม" if TH else "Your Income as Platform Owner"))
        st.info(f"**{pl['description']}** — {pl['n_hubs']} hub{'s' if pl['n_hubs'] > 1 else ''}")

        _is_distro = pl['model'] == 'installment_distro'

        # Hero metrics
        pm1, pm2, pm3, pm4 = st.columns(4)
        with pm1:
            st.metric("💰 Total Investment", f"฿{pt['invest']:,}")
        with pm2:
            if _is_distro:
                st.metric("📈 Year 2+ Income", f"฿{pt.get('distro_income_yr', 0):,}/yr",
                          delta=f"฿{round(pt.get('distro_income_yr', 0)/12):,}/mo")
            else:
                st.metric("📈 Your Income/yr", f"฿{pt['income']:,}", delta=f"฿{round(pt['income']/12):,}/mo")
        with pm3:
            st.metric("📊 ROI", f"{pt['roi']}×")
        with pm4:
            st.metric("⏰ Payback", f"{pt['payback_months']} months")

        st.divider()

        # Per hub and split
        splt1, splt2 = st.columns(2)
        with splt1:
            st.subheader("📦 " + ("ต่อ 1 ฮับ" if TH else "Per Hub"))
            if _is_distro:
                st.markdown("**📅 Year 1** (payback + 2 months distro)")
                st.dataframe(pd.DataFrame([
                    {"Item": "💼 Your Income (Year 1)", "฿": f"฿{ph['owner_income']:,}",
                     "Note": f"฿{ph['owner_invest']:,} payback + ฿{ph['owner_income'] - ph['owner_invest']:,} distro"},
                    {"Item": "👨‍🌾 Farmer Income (Year 1)", "฿": f"฿{ph['farmer_income']:,}",
                     "Note": "After paying installments"},
                ]), use_container_width=True, hide_index=True)
                st.markdown("**🔄 Year 2+** (ongoing distribution)")
                st.dataframe(pd.DataFrame([
                    {"Item": "💼 Your Distro Income", "฿/yr": f"฿{ph.get('distro_income_yr', 0):,}",
                     "Note": "15% margin on sales"},
                    {"Item": "👨‍🌾 Farmer Income", "฿/yr": f"฿{ph.get('farmer_income_yr2', 0):,}",
                     "Note": "Owns equipment, keeps 85%"},
                ]), use_container_width=True, hide_index=True)
            else:
                st.dataframe(pd.DataFrame([
                    {"Item": "💼 Your Income/hub", "฿/yr": f"฿{ph['owner_income']:,}"},
                    {"Item": "👨‍🌾 Farmer Income/hub", "฿/yr": f"฿{ph['farmer_income']:,}"},
                    {"Item": "🏭 Your Investment/hub", "฿": f"฿{ph['owner_invest']:,}"},
                ]), use_container_width=True, hide_index=True)

            if pl['n_hubs'] > 1:
                st.subheader("🏭 " + ("รวมทุกฮับ" if TH else f"Total ({pl['n_hubs']} Hubs)"))
                if _is_distro:
                    st.dataframe(pd.DataFrame([
                        {"Item": "💼 Your Distro (Year 2+)", "฿/yr": f"฿{pt.get('distro_income_yr', 0):,}"},
                        {"Item": "👨‍🌾 All Farmers (Year 2+)", "฿/yr": f"฿{pt.get('farmer_total_yr2', 0):,}"},
                        {"Item": "🏭 Total Investment", "฿": f"฿{pt['invest']:,}"},
                    ]), use_container_width=True, hide_index=True)
                else:
                    st.dataframe(pd.DataFrame([
                        {"Item": "💼 Your Total Income", "฿/yr": f"฿{pt['income']:,}"},
                        {"Item": "👨‍🌾 All Farmers Total", "฿/yr": f"฿{pt['farmer_total']:,}"},
                        {"Item": "🏭 Total Investment", "฿": f"฿{pt['invest']:,}"},
                    ]), use_container_width=True, hide_index=True)

        with splt2:
            # Income split pie — use Year 2+ steady state for distro
            st.subheader("🍰 " + ("แบ่งรายได้" if TH else "Income Split (Year 2+)" if _is_distro else "Income Split"))
            _pie_you = pt.get('distro_income_yr', pt['income']) if _is_distro else pt['income']
            _pie_farmer = pt.get('farmer_total_yr2', pt['farmer_total']) if _is_distro else pt['farmer_total']
            fig_split = go.Figure(go.Pie(
                labels=["💼 You (Distribution)" if _is_distro else "💼 You (Platform)", "👨‍🌾 Farmers"],
                values=[_pie_you, _pie_farmer],
                hole=0.4, marker_colors=['#3b82f6', '#10b981'],
                textinfo='label+percent', textfont_size=14,
            ))
            fig_split.update_layout(height=280, template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10),
                showlegend=False)
            st.plotly_chart(fig_split, use_container_width=True)
            if _is_distro:
                st.caption("📊 Shows Year 2+ steady-state split. Year 1 includes equipment payback.")

        st.divider()

        # 5-year projection
        st.subheader("📈 " + ("คาดการณ์ 5 ปี" if TH else "5-Year Projection"))
        proj = pl['projection']
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Bar(
            x=[f"Year {p['year']}" for p in proj],
            y=[p['income'] for p in proj],
            name="💰 Annual Income",
            marker_color='#3b82f6',
            text=[f"฿{p['income']:,}" for p in proj],
            textposition='outside', textfont=dict(size=11, color='white'),
        ))
        fig_proj.add_trace(go.Scatter(
            x=[f"Year {p['year']}" for p in proj],
            y=[p['cumulative'] for p in proj],
            name="📈 Cumulative",
            line=dict(color='#10b981', width=3),
            text=[f"฿{p['cumulative']:,}" for p in proj],
            textposition='top center', textfont=dict(size=10, color='#10b981'),
            mode='lines+markers+text',
        ))
        fig_proj.update_layout(height=350, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", y=-0.15), margin=dict(t=20, b=40),
            yaxis_title="฿",
        )
        # Add break-even line at 0
        fig_proj.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        st.plotly_chart(fig_proj, use_container_width=True)

        # Growth roadmap
        st.subheader("🗺️ " + ("แผนขยาย" if TH else "Growth Roadmap"))
        invest_per = ph['owner_invest']
        income_per = ph['owner_income']
        if income_per > 0:
            months_to_next = round(invest_per / (income_per / 12))
            st.markdown(f"""
| Phase | Action | Hubs | Platform Owner Income/mo |
|-------|--------|------|-------------------|
| 🚀 **Start** | Invest ฿{invest_per:,} in Hub 1 | 1 | ฿{round(income_per/12):,}/mo |
| 📈 **Month {months_to_next}** | Profits fund Hub 2 | 2 | ฿{round(income_per*2/12):,}/mo |
| 📈 **Month {months_to_next*2}** | Add Hub 3 | 3 | ฿{round(income_per*3/12):,}/mo |
| 🎯 **Month {months_to_next*4}** | Reinvest → Hub 5 | 5 | ฿{round(income_per*5/12):,}/mo |
| 🏆 **Year 2-3** | Scale to 10 hubs | 10 | **฿{round(income_per*10/12):,}/mo** 🚀 |
""")
        st.success(f"🏆 **At {pl['n_hubs']} hubs: Platform owner earns ฿{round(pt['income']/12):,}/mo (distribution margin), farmers earn ฿{round(pt['farmer_total']/12):,}/mo. Everyone wins!**")

        st.divider()

        # ═══════════ INVESTOR RETURNS CALCULATOR ═══════════
        st.subheader("💎 " + ("ผลตอบแทนนักลงทุน" if TH else "Angel Investor Returns Calculator"))

        # How many hubs can the investment fund?
        hub_cost = ph['owner_invest']
        hubs_fundable = max(1, int(bp_inv_amount / hub_cost)) if hub_cost > 0 else 1
        platform_margin_per_hub = ph['owner_income']  # yearly platform income per hub
        opex_pct = bp_inv_opex_pct / 100

        st.info(f"💰 ฿{bp_inv_amount:,} investment → funds **{hubs_fundable} hubs** (at ฿{hub_cost:,}/hub). "
                f"Investor gets **{bp_inv_equity}%** equity in platform company.")

        # 5-year investor projection
        inv_years = []
        for yr in range(1, 6):
            # Scale: year 1 = hubs_fundable, year 2 = reinvest to grow, etc.
            active_hubs = min(50, round(hubs_fundable * (1.5 ** (yr - 1))))  # 50% hub growth/yr
            gross_platform = active_hubs * platform_margin_per_hub
            opex = gross_platform * opex_pct
            net_company = gross_platform - opex
            investor_share = round(net_company * bp_inv_equity / 100)
            founder_share = net_company - investor_share
            company_val = round(net_company * 10)  # 10x profit multiple
            inv_equity_val = round(company_val * bp_inv_equity / 100)
            inv_years.append({
                'year': yr, 'hubs': active_hubs,
                'gross': round(gross_platform), 'opex': round(opex),
                'net': round(net_company),
                'investor_yr': investor_share, 'founder_yr': round(founder_share),
                'company_val': company_val, 'equity_val': inv_equity_val,
            })

        # Revenue waterfall
        st.markdown("##### 💧 " + ("ทางน้ำเงิน" if TH else "Revenue Waterfall (per ฿3 plate)"))
        plate_price = 3.0
        farmer_cut = plate_price * 0.75
        platform_cut = plate_price * 0.25
        plat_opex = platform_cut * opex_pct
        plat_net = platform_cut - plat_opex
        inv_cut = plat_net * bp_inv_equity / 100
        founder_cut = plat_net - inv_cut
        st.dataframe(pd.DataFrame([
            {"Who": "👨‍🌾 Farmer", "Gets": f"฿{farmer_cut:.2f}", "%": "75%", "Role": "Produces plates"},
            {"Who": "🏢 Platform OpEx", "Gets": f"฿{plat_opex:.2f}", "%": f"{round(plat_opex/plate_price*100)}%", "Role": "Delivery, QC, tech"},
            {"Who": f"👤 Founder ({100-bp_inv_equity}%)", "Gets": f"฿{founder_cut:.2f}", "%": f"{round(founder_cut/plate_price*100)}%", "Role": "Runs everything"},
            {"Who": f"💎 Investor ({bp_inv_equity}%)", "Gets": f"฿{inv_cut:.2f}", "%": f"{round(inv_cut/plate_price*100)}%", "Role": "Passive capital"},
        ]), use_container_width=True, hide_index=True)

        # 5-year table
        st.markdown("##### 📊 " + ("คาดการณ์ 5 ปี" if TH else "5-Year Investor Projection"))
        st.dataframe(pd.DataFrame([
            {
                "Year": f"Year {y['year']}",
                "Hubs": y['hubs'],
                "Platform Net/yr": f"฿{y['net']:,}",
                f"Investor ({bp_inv_equity}%)/yr": f"฿{y['investor_yr']:,}",
                "Company Value (10×)": f"฿{y['company_val']:,}",
                f"Investor Equity Value": f"฿{y['equity_val']:,}",
            } for y in inv_years
        ]), use_container_width=True, hide_index=True)

        # Investor returns chart
        fig_inv = go.Figure()
        fig_inv.add_trace(go.Bar(
            x=[f"Year {y['year']}" for y in inv_years],
            y=[y['investor_yr'] for y in inv_years],
            name=f"💎 Investor Annual Dividend ({bp_inv_equity}%)",
            marker_color='#f59e0b',
            text=[f"฿{y['investor_yr']:,}" for y in inv_years],
            textposition='outside', textfont=dict(size=11, color='white'),
        ))
        fig_inv.add_trace(go.Scatter(
            x=[f"Year {y['year']}" for y in inv_years],
            y=[y['equity_val'] for y in inv_years],
            name="📈 Investor Equity Value",
            line=dict(color='#ef4444', width=3),
            text=[f"฿{y['equity_val']:,}" for y in inv_years],
            textposition='top center', textfont=dict(size=10, color='#ef4444'),
            mode='lines+markers+text',
        ))
        fig_inv.add_hline(y=bp_inv_amount, line_dash="dash", line_color="rgba(255,255,255,0.4)",
                          annotation_text=f"Investment: ฿{bp_inv_amount:,}")
        fig_inv.update_layout(height=400, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", y=-0.15), margin=dict(t=20, b=40),
            yaxis_title="฿",
        )
        st.plotly_chart(fig_inv, use_container_width=True)

        # Summary metrics
        total_dividends = sum(y['investor_yr'] for y in inv_years)
        final_equity = inv_years[-1]['equity_val']
        total_return = total_dividends + final_equity
        roi_mult = round(total_return / bp_inv_amount, 1) if bp_inv_amount > 0 else 0
        annual_yield = round(inv_years[1]['investor_yr'] / bp_inv_amount * 100, 1) if bp_inv_amount > 0 else 0

        im1, im2, im3, im4 = st.columns(4)
        with im1:
            st.metric("💎 Total 5yr Dividends", f"฿{total_dividends:,}")
        with im2:
            st.metric("📈 Year 5 Equity Value", f"฿{final_equity:,}")
        with im3:
            st.metric("🚀 Total Return (5yr)", f"{roi_mult}×", delta=f"฿{total_return:,}")
        with im4:
            st.metric("📊 Annual Yield (Yr2)", f"{annual_yield}%")

        # Investor pitch summary
        st.success(
            f"**Investor Pitch:** \"Put in ฿{bp_inv_amount:,} → get {bp_inv_equity}% equity. "
            f"Year 2 dividend: ฿{inv_years[1]['investor_yr']:,}/yr ({annual_yield}% yield). "
            f"By Year 5, your stake is worth ฿{final_equity:,} — a **{roi_mult}× return**.\""
        )
