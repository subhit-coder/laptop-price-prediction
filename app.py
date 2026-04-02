
import streamlit as st
import streamlit.components.v1 as components
import joblib
import numpy as np
import pandas as pd

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Laptop Price Predictor",
    page_icon="💻",
    layout="wide"
)

# ======================
# UI DESIGN — ENHANCED
# ======================
def set_bg():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── RESET & BASE ── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html, body, .stApp {
        font-family: 'DM Sans', sans-serif;
        background: #0a0e1a;
        color: #e8eaf0;
        min-height: 100vh;
    }

    /* ── ANIMATED BACKGROUND ── */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.18) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 80%, rgba(16,185,129,0.13) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 50% 50%, rgba(245,158,11,0.07) 0%, transparent 60%),
            #0a0e1a;
        animation: bgPulse 10s ease-in-out infinite alternate;
        z-index: 0;
        pointer-events: none;
    }

    @keyframes bgPulse {
        0%   { opacity: 1; }
        50%  { opacity: 0.75; }
        100% { opacity: 1; }
    }

    /* ── FLOATING PARTICLES ── */
    .particles {
        position: fixed;
        inset: 0;
        overflow: hidden;
        pointer-events: none;
        z-index: 0;
    }
    .particle {
        position: absolute;
        border-radius: 50%;
        opacity: 0;
        animation: float linear infinite;
    }
    @keyframes float {
        0%   { transform: translateY(100vh) scale(0); opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 0.6; }
        100% { transform: translateY(-10vh) scale(1); opacity: 0; }
    }

    /* ── CONTENT LAYER ── */
    .block-container {
        position: relative;
        z-index: 1;
        max-width: 1100px !important;
        padding: 2.5rem 2rem 4rem !important;
    }

    /* ── HEADER ── */
    .hero-header {
        text-align: center;
        padding: 2.5rem 1rem 2rem;
        animation: slideDown 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-32px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(16,185,129,0.15));
        border: 1px solid rgba(99,102,241,0.4);
        border-radius: 50px;
        padding: 6px 18px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #a5b4fc;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2rem, 5vw, 3.4rem);
        font-weight: 800;
        background: linear-gradient(135deg, #e0e7ff 30%, #6366f1 70%, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.15;
        margin-bottom: 0.75rem;
    }
    .hero-sub {
        font-size: 1rem;
        color: #8b92a9;
        font-weight: 300;
    }

    /* ── DIVIDER ── */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0 1.5rem;
        animation: fadeIn 0.5s ease both;
    }
    .section-divider span {
        font-family: 'Syne', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #6366f1;
    }
    .section-divider::before, .section-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent);
    }

    /* ── GLASS CARD ── */
    .glass-card {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
        transition: box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(99,102,241,0.3);
        box-shadow: 0 8px 40px rgba(99,102,241,0.12);
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .glass-card:nth-child(2) { animation-delay: 0.08s; }
    .glass-card:nth-child(3) { animation-delay: 0.16s; }
    .glass-card:nth-child(4) { animation-delay: 0.24s; }

    /* ── STREAMLIT WIDGET OVERRIDES ── */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stNumberInput"] label {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: #9ca3b8 !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 4px !important;
    }

    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stNumberInput"] input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e8eaf0 !important;
        font-family: 'DM Sans', sans-serif !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="stSelectbox"] > div > div:hover,
    div[data-testid="stNumberInput"] input:focus {
        border-color: rgba(99,102,241,0.5) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    }

    /* Slider */
    div[data-testid="stSlider"] div[role="slider"] {
        background: #6366f1 !important;
        border: 2px solid #a5b4fc !important;
        box-shadow: 0 0 12px rgba(99,102,241,0.5) !important;
    }
    div[data-testid="stSlider"] > div > div > div {
        background: linear-gradient(90deg, #6366f1, #10b981) !important;
    }

    /* ── PREDICT BUTTON ── */
    div[data-testid="stButton"] > button {
        width: 100%;
        padding: 1rem 2rem !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 50%, #10b981 100%) !important;
        background-size: 200% 200% !important;
        border: none !important;
        border-radius: 14px !important;
        color: #fff !important;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.3s ease !important;
        animation: gradientShift 4s ease infinite;
        box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
        margin-top: 0.5rem;
    }
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50%       { background-position: 100% 50%; }
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(99,102,241,0.5) !important;
    }
    div[data-testid="stButton"] > button:active {
        transform: translateY(0) !important;
    }

    /* ── PRICE RESULT CARD ── */
    .price-result {
        background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(16,185,129,0.1));
        border: 1px solid rgba(99,102,241,0.35);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        text-align: center;
        margin: 1.5rem 0;
        animation: popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
        position: relative;
        overflow: hidden;
    }
    .price-result::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent 60%, rgba(99,102,241,0.08) 100%);
        animation: spin 8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes popIn {
        from { opacity: 0; transform: scale(0.85); }
        to   { opacity: 1; transform: scale(1); }
    }
    .price-label {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #6366f1;
        margin-bottom: 0.5rem;
        position: relative;
    }
    .price-amount {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2.2rem, 6vw, 3.5rem);
        font-weight: 800;
        background: linear-gradient(135deg, #e0e7ff, #a5b4fc, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        animation: countUp 0.6s ease both 0.1s;
    }
    @keyframes countUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── DATAFRAME ── */
    div[data-testid="stDataFrame"] {
        border-radius: 16px !important;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08) !important;
        animation: fadeUp 0.5s ease both 0.2s;
    }
    .stDataFrame thead th {
        background: rgba(99,102,241,0.2) !important;
        color: #a5b4fc !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(99,102,241,0.3) !important;
        padding: 12px 16px !important;
    }
    .stDataFrame tbody tr {
        transition: background 0.2s ease;
    }
    .stDataFrame tbody tr:hover {
        background: rgba(99,102,241,0.08) !important;
    }
    .stDataFrame tbody td {
        color: #d1d5e8 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.85rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.04) !important;
        padding: 10px 16px !important;
    }

    /* ── SUBHEADER ── */
    h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        color: #c7d2fe !important;
        margin-bottom: 1rem !important;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.7); }

    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    </style>

    <!-- Floating particles -->
    <div class="particles" id="particles"></div>
    <script>
    (function() {
        const container = document.getElementById('particles');
        if (!container) return;
        const colors = ['#6366f1','#10b981','#f59e0b','#ec4899','#06b6d4'];
        for (let i = 0; i < 28; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            const size = Math.random() * 5 + 2;
            p.style.cssText = `
                width: ${size}px; height: ${size}px;
                left: ${Math.random() * 100}%;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                box-shadow: 0 0 ${size * 2}px currentColor;
                animation-duration: ${Math.random() * 12 + 8}s;
                animation-delay: ${Math.random() * 8}s;
            `;
            container.appendChild(p);
        }
    })();
    </script>
    """, unsafe_allow_html=True)
set_bg()

# ======================
# LOAD FILES
# ======================
pipe         = joblib.load('pipe.pkl')
preprocessor = joblib.load('preprocessor.pkl')
knn          = joblib.load('knn_model.pkl')
df           = pd.read_csv('df.csv')

# ======================
# HERO HEADER
# ======================
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">⚡ subhit-Powered</div>
    <div class="hero-title">Laptop Price Predictor</div>
    <p class="hero-sub">Configure your specs below — get an instant price estimate + top similar models</p>
</div>
""", unsafe_allow_html=True)

# ======================
# INPUTS — SECTION 1: Identity
# ======================
st.markdown('<div class="section-divider"><span>Device Identity</span></div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    company = st.selectbox('Brand', df['Company'].unique())
with col2:
    type    = st.selectbox('Type', df['TypeName'].unique())
with col3:
    os      = st.selectbox('OS', df['os'].unique())
st.markdown('</div>', unsafe_allow_html=True)

# ======================
# INPUTS — SECTION 2: Performance
# ======================
st.markdown('<div class="section-divider"><span>Performance</span></div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col4, col5, col6, col7 = st.columns(4)
with col4:
    ram = st.selectbox('RAM (GB)', [2,4,6,8,12,16,24,32,64])
with col5:
    cpu = st.selectbox('CPU Brand', df['Cpu brand'].unique())
with col6:
    gpu = st.selectbox('GPU Brand', df['Gpu brand'].unique())
with col7:
    weight = st.number_input('Weight (kg)', min_value=0.5, max_value=5.0, value=1.5, step=0.1)
st.markdown('</div>', unsafe_allow_html=True)

# ======================
# INPUTS — SECTION 3: Display
# ======================
st.markdown('<div class="section-divider"><span>Display</span></div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col8, col9, col10, col11 = st.columns(4)
with col8:
    touchscreen = st.selectbox('Touchscreen', ['No','Yes'])
with col9:
    ips = st.selectbox('IPS Panel', ['No','Yes'])
with col10:
    screen_size = st.slider('Screen Size (in)', 10.0, 18.0, 13.0, 0.1)
with col11:
    resolution = st.selectbox('Resolution', [
        '1920x1080','1366x768','1600x900','3840x2160',
        '3200x1800','2880x1800','2560x1600','2560x1440','2304x1440'
    ])
st.markdown('</div>', unsafe_allow_html=True)

# ======================
# INPUTS — SECTION 4: Storage
# ======================
st.markdown('<div class="section-divider"><span>Storage</span></div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col12, col13 = st.columns(2)
with col12:
    hdd = st.selectbox('HDD (GB)', [0,128,256,512,1024,2048])
with col13:
    ssd = st.selectbox('SSD (GB)', [0,8,128,256,512,1024])
st.markdown('</div>', unsafe_allow_html=True)

# ======================
# PREDICT BUTTON
# ======================
st.markdown('<br>', unsafe_allow_html=True)
if st.button('🔍  Predict Price & Find Similar Laptops'):

    # Convert
    touchscreen_val = 1 if touchscreen == 'Yes' else 0
    ips_val         = 1 if ips == 'Yes' else 0

    # PPI
    X_res = int(resolution.split('x')[0])
    Y_res = int(resolution.split('x')[1])
    ppi   = ((X_res**2 + Y_res**2)**0.5) / screen_size

    # Build input
    input_df = pd.DataFrame([{
        'Company':     company,
        'TypeName':    type,
        'Ram':         ram,
        'Weight':      weight,
        'Touchscreen': touchscreen_val,
        'Ips':         ips_val,
        'ppi':         ppi,
        'Cpu brand':   cpu,
        'HDD':         hdd,
        'SSD':         ssd,
        'Gpu brand':   gpu,
        'os':          os
    }])

    # ── Price Prediction ──
    predicted_price = int(np.exp(pipe.predict(input_df)[0]))

    st.markdown(f"""
    <div class="price-result">
        <div class="price-label">Estimated Market Price</div>
        <div class="price-amount">₹{predicted_price:,}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KNN Similarity ──
    input_processed = preprocessor.transform(input_df)
    distances, indices = knn.kneighbors(input_processed)
    similar_laptops = df.iloc[indices[0]].copy()
    similar_laptops['Price Diff (₹)'] = abs(similar_laptops['Price'] - predicted_price)
    similar_laptops = similar_laptops.sort_values(by='Price Diff (₹)')

    st.markdown('<div class="section-divider"><span>🔥 Top 5 Similar Laptops</span></div>', unsafe_allow_html=True)

    # ── Custom Card Table ──
    display_cols = ['Company', 'TypeName', 'Ram', 'Weight', 'Cpu brand', 'Gpu brand', 'HDD', 'SSD', 'os', 'Price', 'Price Diff (₹)']
    available_cols = [c for c in display_cols if c in similar_laptops.columns]
    top5 = similar_laptops[available_cols].head(5).reset_index(drop=True)

    cards_html = '<div class="laptop-cards">'
    for i, row in top5.iterrows():
        rank_colors = ['#6366f1','#10b981','#f59e0b','#ec4899','#06b6d4']
        color = rank_colors[i]
        price_val = f"₹{int(row['Price']):,}" if 'Price' in row else '—'
        diff_val  = f"₹{int(row['Price Diff (₹)']):,}" if 'Price Diff (₹)' in row else '—'

        specs_html = ''
        spec_map = {
            'TypeName': '🖥️', 'Ram': '💾', 'Cpu brand': '⚡',
            'Gpu brand': '🎮', 'HDD': '💿', 'SSD': '⚡', 'os': '🪟', 'Weight': '⚖️'
        }
        for col, icon in spec_map.items():
            if col in row:
                val = row[col]
                if col in ['Ram','HDD','SSD'] and val == 0:
                    continue
                label = col.replace(' brand','').replace('TypeName','Type')
                unit = ' GB' if col in ['Ram','HDD','SSD'] else (' kg' if col == 'Weight' else '')
                specs_html += f'<div class="spec-chip"><span class="spec-icon">{icon}</span><span class="spec-text">{label}: <b>{val}{unit}</b></span></div>'

        cards_html += f"""
        <div class="laptop-card" style="--accent:{color}; animation-delay:{i*0.1}s">
            <div class="card-rank">#{i+1}</div>
            <div class="card-header">
                <div class="card-brand">{row.get('Company','—')}</div>
                <div class="card-price">{price_val}</div>
            </div>
            <div class="card-specs">{specs_html}</div>
            <div class="card-footer">
                <span class="diff-badge">Δ {diff_val} from estimate</span>
            </div>
        </div>
        """
    cards_html += '</div>'

    # ── Render cards using components.html (bypasses Streamlit's HTML sanitizer) ──
    cards_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: transparent; }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .laptop-cards {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 4px 2px;
        font-family: 'DM Sans', 'Segoe UI', sans-serif;
    }
    .laptop-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 3px solid var(--accent);
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        position: relative;
        animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) both;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        cursor: default;
    }
    .laptop-card:hover {
        transform: translateX(5px);
        border-color: var(--accent);
        box-shadow: 0 4px 24px rgba(0,0,0,0.4), -4px 0 16px color-mix(in srgb, var(--accent) 25%, transparent);
    }
    .card-rank {
        position: absolute;
        top: 0.9rem; right: 1.1rem;
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--accent);
        opacity: 0.2;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    .card-brand {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #e0e7ff;
    }
    .card-price {
        font-family: 'Syne', sans-serif;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--accent);
        background: color-mix(in srgb, var(--accent) 12%, transparent);
        padding: 3px 13px;
        border-radius: 50px;
        border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
    }
    .card-specs {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-bottom: 0.7rem;
    }
    .spec-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 7px;
        padding: 3px 9px;
        font-size: 0.76rem;
        color: #9ca3b8;
    }
    .laptop-card:hover .spec-chip {
        background: rgba(255,255,255,0.09);
    }
    .spec-text b { color: #c7d2fe; font-weight: 500; }
    .diff-badge {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        color: color-mix(in srgb, var(--accent) 85%, white);
        background: color-mix(in srgb, var(--accent) 10%, transparent);
        border: 1px solid color-mix(in srgb, var(--accent) 22%, transparent);
        border-radius: 50px;
        padding: 2px 11px;
    }
    </style>
    """

    # Estimate card height: ~160px per card + padding
    card_height = len(top5) * 175 + 20
    components.html(cards_css + cards_html, height=card_height, scrolling=False)
