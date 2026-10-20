import streamlit as st
import pandas as pd
import hashlib
from recommend import recommend

st.set_page_config(
    page_title="NutriGuide AI — Smart Meal Planner",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: Premium Airbnb-style ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

/* Base */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #F8F8F8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #EBEBEB !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* Kill default top padding */
[data-testid="stAppViewContainer"] > section > div:first-child {
    padding-top: 0 !important;
}

/* Hide hamburger & footer */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar styling ── */
.sidebar-brand {
    background: linear-gradient(135deg, #FF5A5F, #FC642D);
    padding: 28px 24px 24px;
    margin-bottom: 0;
}
.sidebar-brand-title {
    color: white;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.sidebar-brand-sub {
    color: rgba(255,255,255,0.8);
    font-size: 12px;
    font-weight: 500;
    margin-top: 4px;
}
.sidebar-section {
    padding: 20px 20px 0;
}
.sidebar-section-title {
    font-size: 11px;
    font-weight: 700;
    color: #AAAAAA;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

/* Meal pill buttons in sidebar */
.meal-pill-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 8px;
}
.meal-pill-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 14px 8px;
    border-radius: 14px;
    border: 2px solid #EBEBEB;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}
.meal-pill-btn.active {
    border-color: #FF5A5F;
    background: #FFF0F0;
    box-shadow: 0 2px 12px rgba(255,90,95,0.2);
}
.meal-pill-icon { font-size: 22px; }
.meal-pill-label { font-size: 12px; font-weight: 700; color: #222; }

/* ── Main content ── */
.main-header {
    background: linear-gradient(135deg, #FF5A5F 0%, #E8444A 40%, #FC642D 100%);
    border-radius: 24px;
    padding: 40px 44px;
    color: white;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.main-header::after {
    content: '';
    position: absolute;
    bottom: -80px; right: 80px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.header-tag {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    color: white;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 50px;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.3);
}
.header-title {
    font-size: 40px;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 10px;
    letter-spacing: -1px;
}
.header-sub {
    font-size: 15px;
    opacity: 0.85;
    line-height: 1.6;
    max-width: 480px;
}
.header-stats {
    display: flex;
    gap: 28px;
    margin-top: 24px;
}
.header-stat {
    display: flex;
    flex-direction: column;
}
.header-stat-val {
    font-size: 24px;
    font-weight: 800;
}
.header-stat-lbl {
    font-size: 12px;
    opacity: 0.72;
    font-weight: 500;
    margin-top: 2px;
}

/* ── Section title ── */
.results-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 20px;
    margin-top: 8px;
}
.results-title {
    font-size: 22px;
    font-weight: 800;
    color: #1A1A1A;
    letter-spacing: -0.5px;
}
.results-badge {
    background: #FF5A5F;
    color: white;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 50px;
}
.results-sub {
    font-size: 13px;
    color: #888;
    font-weight: 500;
    margin-left: auto;
}

/* ── Meal Card ── */
.ng-card {
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.05);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    border: 1px solid rgba(0,0,0,0.05);
    height: 100%;
}
.ng-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.13);
}
.ng-card-img {
    background: linear-gradient(145deg, #FFF2F2, #FFF8F5);
    padding: 28px 16px 22px;
    text-align: center;
    position: relative;
    border-bottom: 1px solid #FFF0F0;
    min-height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.ng-card-emoji {
    font-size: 52px;
    line-height: 1;
    display: block;
    font-style: normal;
    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif;
}
.ng-cal-pill {
    position: absolute;
    top: 12px; right: 12px;
    background: #FF5A5F;
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 50px;
    letter-spacing: 0.3px;
}
.ng-meal-pill {
    position: absolute;
    top: 12px; left: 12px;
    background: rgba(255,255,255,0.95);
    color: #555;
    font-size: 10px;
    font-weight: 600;
    padding: 4px 9px;
    border-radius: 50px;
    border: 1px solid rgba(0,0,0,0.07);
}
.ng-card-body {
    padding: 16px 18px 18px;
}
.ng-food-id {
    font-size: 10px;
    font-weight: 700;
    color: #FF5A5F;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 5px;
}
.ng-food-name {
    font-size: 15px;
    font-weight: 700;
    color: #1A1A1A;
    line-height: 1.35;
    margin-bottom: 12px;
    min-height: 40px;
}
.ng-macros {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}
.ng-mac {
    font-size: 11px;
    font-weight: 600;
    padding: 4px 9px;
    border-radius: 7px;
}
.ng-mac-p { background: #ECFDF5; color: #065F46; }
.ng-mac-c { background: #EFF6FF; color: #1E40AF; }
.ng-mac-f { background: #FFF7ED; color: #9A3412; }
.ng-serving {
    font-size: 11px;
    color: #999;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
    padding-top: 10px;
    border-top: 1px solid #F5F5F5;
}
.ng-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.ng-dot-low  { background: #F59E0B; }
.ng-dot-med  { background: #10B981; }
.ng-dot-high { background: #3B82F6; }

/* ── Summary card ── */
.summary-card {
    background: white;
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.05);
    margin-top: 28px;
    margin-bottom: 12px;
}
.summary-label {
    font-size: 11px;
    font-weight: 700;
    color: #AAAAAA;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 16px;
}
.summary-val {
    font-size: 26px;
    font-weight: 800;
    color: #FF5A5F;
    line-height: 1;
}
.summary-sub {
    font-size: 12px;
    color: #999;
    font-weight: 500;
    margin-top: 4px;
}

/* ── Landing state ── */
.landing-wrap {
    text-align: center;
    padding: 48px 20px 32px;
}
.landing-emoji { font-size: 80px; margin-bottom: 16px; }
.landing-title { font-size: 28px; font-weight: 800; color: #1A1A1A; margin-bottom: 8px; letter-spacing: -0.5px; }
.landing-sub { font-size: 15px; color: #888; line-height: 1.7; max-width: 400px; margin: 0 auto 32px; }

.qcard {
    background: white;
    border-radius: 18px;
    padding: 24px 16px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.04);
    border: 1px solid #EBEBEB;
    transition: all 0.25s ease;
    cursor: pointer;
}
.qcard:hover {
    border-color: #FF5A5F;
    box-shadow: 0 8px 24px rgba(255,90,95,0.15);
    transform: translateY(-3px);
}
.qcard-icon { font-size: 36px; margin-bottom: 8px; }
.qcard-title { font-size: 14px; font-weight: 700; color: #1A1A1A; margin-bottom: 3px; }
.qcard-cal { font-size: 12px; color: #FF5A5F; font-weight: 600; }

/* ── Sidebar widgets ── */
[data-testid="stSidebar"] label { 
    font-family: 'Plus Jakarta Sans', sans-serif !important; 
    font-weight: 600 !important; 
    font-size: 12px !important;
    color: #555 !important;
}
[data-testid="stSidebar"] .stSlider > div { margin-top: 4px; }

/* Button */
[data-testid="stSidebar"] [data-testid="stButton"] > button,
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #FF5A5F, #FC642D) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    height: auto !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 16px rgba(255,90,95,0.4) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover,
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(255,90,95,0.5) !important;
}

/* Selectbox */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    border-radius: 12px !important;
    border: 1.5px solid #E8E8E8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Number input */
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    border-radius: 12px !important;
    border: 1.5px solid #E8E8E8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Warning */
.ng-warning {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 14px;
    padding: 14px 18px;
    font-size: 12px;
    color: #78350F;
    line-height: 1.6;
    margin-top: 16px;
}

/* Regen button secondary */
.btn-regen [data-testid="stButton"] > button {
    background: white !important;
    color: #FF5A5F !important;
    border: 2px solid #FF5A5F !important;
    box-shadow: none !important;
}
.btn-regen [data-testid="stButton"] > button:hover {
    background: #FFF0F0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
MEAL_EMOJIS = {
    "breakfast": ["🥞", "🍳", "🥐", "☕", "🧇", "🍓", "🥣"],
    "lunch":     ["🥗", "🍜", "🌮", "🥙", "🍱", "🥘", "🫕"],
    "dinner":    ["🍽️", "🥩", "🍲", "🫔", "🍛", "🦐", "🥦"],
    "snacks":    ["🍎", "🥜", "🧀", "🍇", "🥨", "🍿", "🫐"],
}
MEAL_META = {
    "breakfast": {"icon": "🌅", "label": "Breakfast", "cal": 350},
    "lunch":     {"icon": "☀️",  "label": "Lunch",     "cal": 500},
    "dinner":    {"icon": "🌙", "label": "Dinner",    "cal": 650},
    "snacks":    {"icon": "✨", "label": "Snacks",    "cal": 200},
}

def pick_emoji(name: str, meal: str) -> str:
    pool = MEAL_EMOJIS.get(meal, ["🍽️"])
    return pool[int(hashlib.md5(name.encode()).hexdigest(), 16) % len(pool)]

def conf_dot(conf: str):
    c = str(conf).lower()
    if "high" in c: return "ng-dot-high", "Verified"
    if "med"  in c: return "ng-dot-med",  "Moderate"
    return "ng-dot-low", "Estimated"

def meal_card(row, meal: str):
    e    = pick_emoji(row["food_name"], meal)
    cal  = int(row["calories_kcal_per_serving_estimated"])
    pro  = round(row["protein_g_per_serving_estimated"], 1)
    carb = round(row["carbs_g_per_serving_estimated"], 1)
    fat  = round(row["fat_g_per_serving_estimated"], 1)
    serv = int(round(row["serving_size_g_estimated"]))
    dot, dlabel = conf_dot(row.get("estimate_confidence",""))
    fid  = row.get("food_id","")
    name = row["food_name"].title()
    icon = MEAL_META[meal]["icon"]
    lbl  = MEAL_META[meal]["label"]

    st.markdown(f"""
    <div class="ng-card">
      <div class="ng-card-img" style="position:relative;">
        <span class="ng-card-emoji" role="img">{e}</span>
        <span class="ng-cal-pill" style="position:absolute;top:10px;right:10px;">&#x1F525; {cal} kcal</span>
        <span class="ng-meal-pill" style="position:absolute;top:10px;left:10px;">{lbl}</span>
      </div>
      <div class="ng-card-body">
        <div class="ng-food-id">{fid}</div>
        <div class="ng-food-name">{name}</div>
        <div class="ng-macros">
          <span class="ng-mac ng-mac-p">Protein: {pro}g</span>
          <span class="ng-mac ng-mac-c">Carbs: {carb}g</span>
          <span class="ng-mac ng-mac-f">Fat: {fat}g</span>
        </div>
        <div class="ng-serving">
          <span class="ng-dot {dot}"></span>
          <span>{serv}g serving &nbsp;&middot;&nbsp; {dlabel}</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
for key, default in [
    ("results", None), ("last_meal", "lunch"),
    ("last_cal", 400), ("excluded_ids", [])
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="sidebar-brand-title">🍽️ NutriGuide AI</div>
      <div class="sidebar-brand-sub">Smart Meal Recommendations</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Meal Type</div>', unsafe_allow_html=True)

    meal_type = st.selectbox(
        "Select meal",
        options=["breakfast", "lunch", "dinner", "snacks"],
        format_func=lambda x: f"{MEAL_META[x]['icon']}  {MEAL_META[x]['label']}",
        index=["breakfast","lunch","dinner","snacks"].index(st.session_state.last_meal),
        label_visibility="collapsed",
        key="meal_sel",
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-section-title">Calorie Target</div>', unsafe_allow_html=True)
    target_cal = st.slider(
        "kcal per serving",
        100, 1200,
        value=st.session_state.last_cal,
        step=25,
        label_visibility="collapsed",
        key="cal_sl",
    )
    st.caption(f"🎯 Target: **{target_cal} kcal**")

    st.markdown("---")
    st.markdown('<div class="sidebar-section-title">Results Count</div>', unsafe_allow_html=True)
    count = st.number_input("Count", min_value=1, max_value=20, value=6, step=1,
                            label_visibility="collapsed", key="count_ni")

    st.markdown("---")
    find_btn = st.button("🍽️  Find My Meals", key="find_btn", use_container_width=True)

    if st.session_state.excluded_ids:
        st.markdown(f"""
        <div style="margin-top:12px;font-size:12px;color:#999;text-align:center;">
        🚫 {len(st.session_state.excluded_ids)} items excluded
        </div>""", unsafe_allow_html=True)
        if st.button("↺ Reset exclusions", key="reset_sb"):
            st.session_state.excluded_ids = []
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Stats
    st.markdown("---")
    st.markdown("""
    <div style="padding:0 4px;">
      <div style="font-size:11px;font-weight:700;color:#AAA;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">Dataset</div>
      <div style="display:flex;gap:12px;">
        <div style="flex:1;background:#FFF5F5;border-radius:12px;padding:12px 10px;text-align:center;">
          <div style="font-size:18px;font-weight:800;color:#FF5A5F;">2,483</div>
          <div style="font-size:10px;color:#999;margin-top:2px;">Foods</div>
        </div>
        <div style="flex:1;background:#FFF5F5;border-radius:12px;padding:12px 10px;text-align:center;">
          <div style="font-size:18px;font-weight:800;color:#FF5A5F;">KNN</div>
          <div style="font-size:10px;color:#999;margin-top:2px;">Model</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN AREA ────────────────────────────────────────────────────────────────

# Hero banner
icon = MEAL_META[meal_type]["icon"]
lbl  = MEAL_META[meal_type]["label"]
st.markdown(f"""
<div class="main-header">
  <div class="header-tag">✦ AI-Powered</div>
  <div class="header-title">Find your perfect<br>{lbl} meal.</div>
  <div class="header-sub">
    Set your calorie target in the sidebar and let our KNN model surface
    the most nutritionally diverse picks from 2,483 foods.
  </div>
  <div class="header-stats">
    <div class="header-stat">
      <div class="header-stat-val">2,483</div>
      <div class="header-stat-lbl">Food items</div>
    </div>
    <div class="header-stat">
      <div class="header-stat-val">{target_cal}</div>
      <div class="header-stat-lbl">Target kcal</div>
    </div>
    <div class="header-stat">
      <div class="header-stat-val">{lbl}</div>
      <div class="header-stat-lbl">Meal type</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Trigger search
if find_btn:
    st.session_state.last_meal = meal_type
    st.session_state.last_cal  = target_cal
    with st.spinner(f"Finding the best {lbl.lower()} options..."):
        try:
            res = recommend(
                meal=meal_type, target_calories=target_cal,
                count=int(count), exclude_ids=st.session_state.excluded_ids,
            )
            st.session_state.results = res
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
            st.session_state.results = None

results   = st.session_state.results
last_meal = st.session_state.last_meal

# ─── Results ─────────────────────────────────────────────────────────────────
if results is not None and not results.empty:
    n = len(results)
    avg_cal = int(results["calories_kcal_per_serving_estimated"].mean())
    m_icon = MEAL_META[last_meal]["icon"]
    m_lbl  = MEAL_META[last_meal]["label"]

    st.markdown(f"""
    <div class="results-header">
      <div class="results-title">{m_icon} {m_lbl} Picks</div>
      <span class="results-badge">{n} results</span>
      <span class="results-sub">avg {avg_cal} kcal / serving</span>
    </div>
    """, unsafe_allow_html=True)

    # 3-column grid
    for i in range(0, len(results), 3):
        chunk = results.iloc[i:i+3]
        cols  = st.columns(3, gap="large")
        for j, (_, row) in enumerate(chunk.iterrows()):
            with cols[j]:
                meal_card(row, last_meal)
        if i + 3 < len(results):
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Regenerate ──
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    shown_ids = results["food_id"].astype(str).tolist()
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("🔄 Regenerate", key="regen_btn", use_container_width=True):
            st.session_state.excluded_ids = list(set(st.session_state.excluded_ids + shown_ids))
            with st.spinner("Finding fresh picks..."):
                try:
                    new_r = recommend(
                        meal=last_meal, target_calories=st.session_state.last_cal,
                        count=int(count), exclude_ids=st.session_state.excluded_ids,
                    )
                    if new_r.empty:
                        st.warning("No more unique meals — resetting exclusions.")
                        st.session_state.excluded_ids = []
                        new_r = recommend(meal=last_meal, target_calories=st.session_state.last_cal, count=int(count))
                    st.session_state.results = new_r
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ── Nutrition Summary ──
    st.markdown("""
    <div class="summary-card">
      <div class="summary-label">📊 Average Nutrition Per Serving</div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    for col_w, val, sub in [
        (sc1, f"{int(results['calories_kcal_per_serving_estimated'].mean())} kcal", "🔥 Calories"),
        (sc2, f"{results['protein_g_per_serving_estimated'].mean():.1f}g",           "💪 Protein"),
        (sc3, f"{results['carbs_g_per_serving_estimated'].mean():.1f}g",             "🌾 Carbs"),
        (sc4, f"{results['fat_g_per_serving_estimated'].mean():.1f}g",               "🥑 Fat"),
    ]:
        with col_w:
            st.markdown(f"""
            <div style="text-align:center;padding:4px 0;">
              <div class="summary-val">{val}</div>
              <div class="summary-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif results is not None and results.empty:
    st.warning("😕 No meals found for that combination. Try adjusting the calorie target or meal type.")

else:
    # ── Landing ──
    st.markdown("""
    <div class="landing-wrap">
      <div class="landing-emoji">🥗</div>
      <div class="landing-title">Ready for your meal plan?</div>
      <div class="landing-sub">
        Pick a meal type and calorie target in the sidebar,
        then hit <strong style="color:#FF5A5F;">Find My Meals</strong>.
      </div>
    </div>
    """, unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4, gap="large")
    for col_w, meal_k in zip([q1, q2, q3, q4], ["breakfast","lunch","dinner","snacks"]):
        m = MEAL_META[meal_k]
        with col_w:
            st.markdown(f"""
            <div class="qcard">
              <div class="qcard-icon">{m['icon']}</div>
              <div class="qcard-title">{m['label']}</div>
              <div class="qcard-cal">~{m['cal']} kcal</div>
            </div>""", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ng-warning">
  ⚠️ <strong>Note:</strong> All nutrition values are estimated and unverified.
  Allergen status is unknown. Do not use for medical, dietary, or allergy decisions.
  Values marked <em>low_unverified_or_imputed</em> are heuristic estimates only.
</div>
""", unsafe_allow_html=True)
