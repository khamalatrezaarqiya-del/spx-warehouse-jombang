import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from pulp import *
import math

st.set_page_config(
    layout="wide",
    page_title="SPX Warehouse Optimizer – Jombang",
    page_icon="🚚"
)

# ── FORCE LIGHT MODE + SHOPEE THEME CSS ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=DM+Sans:wght@400;500;600&display=swap');

/* Force light mode — override Streamlit dark/auto theme */
:root, [data-theme="dark"], [data-theme="light"] {
    color-scheme: light !important;
    --shopee-orange:     #EE4D2D;
    --shopee-orange-2:   #F85606;
    --shopee-orange-lt:  #FFF3F0;
    --shopee-orange-mid: #FFDDD6;
    --shopee-dark:       #2C2C2C;
    --shopee-gray:       #F5F5F5;
    --shopee-gray-2:     #EDEDED;
    --shopee-text:       #333333;
    --shopee-subtext:    #757575;
    --white:             #FFFFFF;
    --shadow-sm:         0 2px 8px rgba(238,77,45,0.10);
    --shadow-md:         0 4px 20px rgba(238,77,45,0.15);
    --radius:            12px;
    --radius-sm:         8px;
}

/* Hard override semua elemen ke light */
.stApp, .stApp * {
    color-scheme: light !important;
}
.stApp {
    background: #F5F5F5 !important;
    color: #333333 !important;
}

/* Main content area */
.main .block-container {
    background: #F5F5F5 !important;
    color: #333333 !important;
}

/* Semua teks */
html, body, [class*="css"], p, span, div, label {
    font-family: 'DM Sans', sans-serif !important;
    color: #333333 !important;
}

/* Heading */
h1 { font-family:'Nunito',sans-serif !important; font-weight:900 !important; font-size:1.8rem !important; color:#EE4D2D !important; letter-spacing:-0.5px; margin-bottom:0 !important; }
h2 { font-family:'Nunito',sans-serif !important; font-weight:800 !important; font-size:1.15rem !important; color:#2C2C2C !important; margin-top:0.5rem !important; }
h3 { font-family:'Nunito',sans-serif !important; font-weight:700 !important; color:#2C2C2C !important; }
h4, h5, h6 { font-family:'Nunito',sans-serif !important; color:#2C2C2C !important; }

/* Caption */
.stApp [data-testid="stCaptionContainer"] p { color:#757575 !important; font-size:0.82rem !important; }

/* Sidebar — paksa putih */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 2px solid #FFDDD6 !important;
}
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span { color:#2C2C2C !important; background: transparent !important; }

/* Input fields */
.stNumberInput input, .stTextInput input, .stSelectbox select,
input[type="number"], input[type="text"] {
    border: 1.5px solid #EDEDED !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    color: #333333 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s;
}
.stNumberInput input:focus, .stTextInput input:focus {
    border-color: #EE4D2D !important;
    box-shadow: 0 0 0 3px rgba(238,77,45,0.12) !important;
}

/* Checkbox */
.stCheckbox label { color: #333333 !important; }
.stCheckbox [data-testid="stCheckbox"] { accent-color: #EE4D2D; }

/* Multiselect */
[data-testid="stMultiSelect"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #EDEDED !important;
    border-radius: 8px !important;
}
[data-testid="stMultiSelect"] span { color: #333333 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1.5px solid #FFDDD6 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 2px 8px rgba(238,77,45,0.10) !important;
    transition: box-shadow 0.2s, transform 0.2s;
}
[data-testid="metric-container"]:hover { box-shadow: 0 4px 20px rgba(238,77,45,0.15) !important; transform: translateY(-2px); }
[data-testid="stMetricLabel"] { font-size:0.75rem !important; font-weight:600 !important; color:#757575 !important; text-transform:uppercase; letter-spacing:0.5px; }
[data-testid="stMetricValue"] { font-family:'Nunito',sans-serif !important; font-weight:900 !important; font-size:1.4rem !important; color:#EE4D2D !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg,#EE4D2D,#F85606) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important;
    font-family: 'Nunito',sans-serif !important; font-weight:700 !important;
    padding: 8px 22px !important; transition: opacity 0.2s, transform 0.15s;
}
.stButton > button:hover { opacity:0.9 !important; transform:translateY(-1px) !important; }

/* Alerts */
.stSuccess { background:#F0FFF4 !important; border-left:4px solid #22c55e !important; border-radius:8px !important; }
.stError   { background:#FFF5F5 !important; border-left:4px solid #EE4D2D !important; border-radius:8px !important; }
.stWarning { background:#FFFBEB !important; border-left:4px solid #f59e0b !important; border-radius:8px !important; }
.stInfo    { background:#FFF3F0 !important; border-left:4px solid #EE4D2D !important; border-radius:8px !important; }

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius:12px !important; overflow:hidden;
    border:1px solid #FFDDD6 !important;
    box-shadow: 0 2px 8px rgba(238,77,45,0.10);
}
[data-testid="stDataFrame"] * { color: #333333 !important; background: #FFFFFF !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background:#FFFFFF; border-radius:12px; padding:4px; gap:4px; border:1px solid #FFDDD6; }
.stTabs [data-baseweb="tab"] { border-radius:8px !important; font-family:'Nunito',sans-serif !important; font-weight:700 !important; color:#757575 !important; padding:8px 18px !important; background: transparent !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#EE4D2D,#F85606) !important; color:white !important; }
.stTabs [aria-selected="true"] * { color:white !important; }

/* Expander */
.streamlit-expanderHeader { background:#FFF3F0 !important; border-radius:8px !important; font-weight:700 !important; color:#EE4D2D !important; border:1px solid #FFDDD6 !important; }

/* Divider */
hr { border-color:#FFDDD6 !important; margin:12px 0 !important; }

/* Sidebar section label */
.sidebar-section { font-family:'Nunito',sans-serif; font-weight:800; font-size:0.72rem; text-transform:uppercase; letter-spacing:1.2px; color:#EE4D2D !important; padding:6px 0 4px 0; border-bottom:2px solid #FFDDD6; margin-bottom:6px; }

/* Scrollbar */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#F5F5F5; }
::-webkit-scrollbar-thumb { background:#FFDDD6; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#EE4D2D; }

/* LaTeX */
.katex { color: #333333 !important; }

/* Markdown teks biasa di dalam app */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# ── TOP HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#EE4D2D 0%,#F85606 100%);
            border-radius:12px;padding:18px 28px;margin-bottom:20px;
            display:flex;align-items:center;justify-content:space-between;
            box-shadow:0 4px 20px rgba(238,77,45,0.15);">
    <div>
        <div style="color:white;font-family:'Nunito',sans-serif;font-weight:900;font-size:1.5rem;letter-spacing:-0.5px;">
            🚚 SPX Warehouse Optimizer
        </div>
        <div style="color:rgba(255,255,255,0.85);font-size:0.82rem;margin-top:3px;">
            Simulasi Alokasi Gudang Strategis · Mixed-Integer Linear Programming · Kabupaten Jombang, Jawa Timur
        </div>
    </div>
    <div style="color:white;font-family:'Nunito',sans-serif;font-weight:800;font-size:0.75rem;
                background:rgba(255,255,255,0.18);padding:6px 14px;border-radius:20px;letter-spacing:0.5px;">
        SPX Express · Beta
    </div>
</div>
""", unsafe_allow_html=True)

# ── DATA KECAMATAN JOMBANG ────────────────────────────────────────────────────
kecamatan_jombang = {
    "Jombang Kota":      [-7.5568, 112.2332],
    "Peterongan":        [-7.5461, 112.2714],
    "Mojoagung":         [-7.5684, 112.3364],
    "Ploso":             [-7.4566, 112.2152],
    "Ngoro":             [-7.6841, 112.2592],
    "Diwek":             [-7.5936, 112.2185],
    "Sumobito":          [-7.5200, 112.3100],
    "Kesamben":          [-7.6200, 112.3600],
    "Bandarkedungmulyo": [-7.5100, 112.1700],
    "Wonosalam":         [-7.6500, 112.3900],
    "Perak":             [-7.4800, 112.2600],
    "Gudo":              [-7.5750, 112.2900],
    "Megaluh":           [-7.5050, 112.2400],
    "Tembelang":         [-7.5300, 112.2000],
    "Kabuh":             [-7.4200, 112.2800],
    "Plandaan":          [-7.4100, 112.3200],
    "Kudu":              [-7.4400, 112.3700],
    "Bareng":            [-7.6300, 112.3200],
    "Mojowarno":         [-7.6100, 112.3000],
    "Jogoroto":          [-7.5700, 112.2500],
    "Ngusikan":          [-7.4700, 112.3400],
}
lat_base, lon_base = -7.5466, 112.2384

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#EE4D2D,#F85606);
                border-radius:10px;padding:12px 16px;margin-bottom:16px;">
        <div style="color:white;font-family:'Nunito',sans-serif;font-weight:900;font-size:1rem;">⚙️ Parameter Simulasi</div>
        <div style="color:rgba(255,255,255,0.8);font-size:0.75rem;margin-top:2px;">Atur semua parameter di bawah ini</div>
    </div>
    """, unsafe_allow_html=True)

    # — Pilih Kecamatan Demand —
    st.markdown('<div class="sidebar-section">📍 Pilih Kecamatan Titik Demand</div>', unsafe_allow_html=True)
    semua_kecamatan = list(kecamatan_jombang.keys())

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ Pilih Semua", use_container_width=True):
            st.session_state["kec_terpilih"] = semua_kecamatan
    with col_btn2:
        if st.button("❌ Reset", use_container_width=True):
            st.session_state["kec_terpilih"] = semua_kecamatan[:5]

    if "kec_terpilih" not in st.session_state:
        st.session_state["kec_terpilih"] = semua_kecamatan[:5]

    kec_terpilih = st.multiselect(
        "Kecamatan aktif sebagai titik demand:",
        options=semua_kecamatan,
        default=st.session_state["kec_terpilih"],
        help="Demand akan di-generate secara acak di sekitar kecamatan yang dipilih"
    )
    st.session_state["kec_terpilih"] = kec_terpilih

    if not kec_terpilih:
        st.error("⚠️ Pilih minimal 1 kecamatan!")
        st.stop()

    demand_per_kec = st.number_input(
        "Jumlah Titik Demand per Kecamatan",
        min_value=1, value=4, step=1,
        help="Setiap kecamatan terpilih akan punya sejumlah titik demand ini"
    )
    num_demand = len(kec_terpilih) * demand_per_kec

    st.markdown(
        f'<div style="background:#FFF3F0;border:1px solid #FFDDD6;border-radius:6px;'
        f'padding:6px 12px;font-size:0.8rem;color:#993C1D;margin-top:4px;">'
        f'📊 Total titik demand: <b>{num_demand}</b> '
        f'({len(kec_terpilih)} kecamatan × {demand_per_kec})</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # — Kandidat Gudang —
    st.markdown('<div class="sidebar-section">🏭 Kandidat Gudang</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        num_candidates = st.number_input("Kandidat Gudang", min_value=1, value=5, step=1,
                                         help="Jumlah kandidat lokasi gudang")
    with col_s2:
        gudang_harus_buka = st.number_input(
            "Harus Dibuka", min_value=1, max_value=num_candidates, value=2, step=1
        )

    st.divider()

    # — Armada Truk —
    st.markdown('<div class="sidebar-section">🚛 Armada Truk</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        kapasitas_truk = st.number_input("Kapasitas / Truk", min_value=10, value=50, step=5,
                                          help="Maksimal unit barang per truk")
    with col_t2:
        jumlah_armada = st.number_input("Armada / Gudang", min_value=1, value=5, step=1,
                                         help="Maksimal truk per gudang")
    col_t3, col_t4 = st.columns(2)
    with col_t3:
        biaya_truk_per_km = st.number_input("Biaya/km (Rp rb)", min_value=0.0, value=5.0,
                                             step=0.5, format="%.1f")
    with col_t4:
        fixed_cost_truk = st.number_input("Fixed/Rit (Rp rb)", min_value=0.0, value=150.0,
                                           step=10.0, format="%.1f")

    st.divider()

    # — Biaya & Kapasitas Gudang —
    st.markdown('<div class="sidebar-section">🏢 Biaya & Kapasitas Gudang</div>', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        biaya_operasional = st.number_input("Opex/Gudang (Rp jt)", min_value=0.0,
                                             value=50.0, step=5.0, format="%.1f")
    with col_g2:
        km_per_deg = st.number_input("1° = ? km", min_value=50.0, value=111.0,
                                      step=1.0, format="%.1f")

    kapasitas_gudang = st.number_input(
        "Kapasitas Gudang (Unit Barang)",
        min_value=100, value=2000, step=100,
        help="Maksimal total unit barang yang bisa ditampung satu gudang."
    )

    st.divider()

    st.markdown('<div class="sidebar-section">🏗️ Biaya Pembukaan Gudang</div>', unsafe_allow_html=True)
    biaya_buka_per_gudang = st.number_input(
        "Biaya Pembukaan per Gudang (Rp jt)",
        min_value=0.0, value=100.0, step=10.0, format="%.1f",
        help="Biaya ini berlaku sama untuk semua kandidat gudang"
    )

# ── DATA GENERATOR ────────────────────────────────────────────────────────────
rng_d = np.random.default_rng(42)
rng_c = np.random.default_rng(99)

# Generate demand berdasarkan kecamatan terpilih
demand_lats, demand_lons, demand_kec = [], [], []
for kec in kec_terpilih:
    center = kecamatan_jombang[kec]
    for _ in range(demand_per_kec):
        demand_lats.append(float(center[0]) + rng_d.normal(0, 0.020))
        demand_lons.append(float(center[1]) + rng_d.normal(0, 0.020))
        demand_kec.append(kec)

demand_data = pd.DataFrame({
    'Kecamatan': demand_kec,
    'Lat':       demand_lats,
    'Lon':       demand_lons,
    'Demand':    rng_d.integers(10, 120, num_demand)
})
demand_data['Jumlah_Truk'] = np.ceil(demand_data['Demand'] / kapasitas_truk).astype(int)

# Kandidat gudang dari kecamatan pertama sejumlah num_candidates
kec_list_all = list(kecamatan_jombang.values())
candidate_lats, candidate_lons = [], []
for i in range(num_candidates):
    center = kec_list_all[i % len(kec_list_all)]
    candidate_lats.append(float(center[0]) + rng_c.uniform(-0.02, 0.02))
    candidate_lons.append(float(center[1]) + rng_c.uniform(-0.02, 0.02))

candidate_data = pd.DataFrame({
    'Gudang': [f"Kandidat Gudang {i+1}" for i in range(num_candidates)],
    'Lat':    candidate_lats,
    'Lon':    candidate_lons,
})

biaya_buka = [biaya_buka_per_gudang] * num_candidates

# ── HELPER ────────────────────────────────────────────────────────────────────
def hitung_jarak_km(p1, p2, km_per_deg):
    return math.sqrt(((p1[0]-p2[0])*km_per_deg)**2 + ((p1[1]-p2[1])*km_per_deg)**2)

# ── PRE-CHECK ─────────────────────────────────────────────────────────────────
total_demand_all    = int(demand_data['Demand'].sum())
total_rit_all       = int(demand_data['Jumlah_Truk'].sum())
max_kapasitas_total = kapasitas_gudang * gudang_harus_buka
max_rit_total       = jumlah_armada * gudang_harus_buka

infeasible_reasons = []
if total_demand_all > max_kapasitas_total:
    infeasible_reasons.append({
        "icon": "📦", "judul": "Kapasitas Gudang Tidak Cukup",
        "detail": (
            f"Total demand seluruh agen adalah <b>{total_demand_all:,} unit</b>, "
            f"sedangkan kapasitas maksimal {gudang_harus_buka} gudang hanya "
            f"<b>{max_kapasitas_total:,} unit</b> ({gudang_harus_buka} × {kapasitas_gudang:,}). "
            f"Selisih kekurangan: <b>{total_demand_all - max_kapasitas_total:,} unit</b>."
        ),
        "saran": "Tambah kapasitas gudang, tambah jumlah gudang yang dibuka, atau kurangi kecamatan demand."
    })
if total_rit_all > max_rit_total:
    infeasible_reasons.append({
        "icon": "🚛", "judul": "Armada Truk Tidak Cukup",
        "detail": (
            f"Total kebutuhan rit truk adalah <b>{total_rit_all} rit</b>, "
            f"sedangkan kapasitas armada maksimal {gudang_harus_buka} gudang hanya "
            f"<b>{max_rit_total} rit</b> ({gudang_harus_buka} × {jumlah_armada}). "
            f"Kekurangan: <b>{total_rit_all - max_rit_total} rit</b>."
        ),
        "saran": "Tambah jumlah armada per gudang, tambah gudang yang dibuka, atau kurangi kecamatan demand."
    })

# ── MODEL OPTIMASI ────────────────────────────────────────────────────────────
model = LpProblem("Facility_Location_Truck_Fleet", LpMinimize)
y = LpVariable.dicts("Buka_Gudang", range(num_candidates), cat='Binary')
x = LpVariable.dicts("Alokasi", (range(num_candidates), range(num_demand)), cat='Binary')

transport_cost = lpSum(
    (
        demand_data.loc[j, 'Jumlah_Truk'] *
        hitung_jarak_km(
            (candidate_data.loc[i, 'Lat'], candidate_data.loc[i, 'Lon']),
            (demand_data.loc[j, 'Lat'],    demand_data.loc[j, 'Lon']),
            km_per_deg
        ) * biaya_truk_per_km
        + demand_data.loc[j, 'Jumlah_Truk'] * fixed_cost_truk
    ) * x[i][j]
    for i in range(num_candidates) for j in range(num_demand)
)
setup_cost = lpSum(biaya_buka[i] * 1000 * y[i] for i in range(num_candidates))
opex_cost  = lpSum(biaya_operasional * 1000 * y[i] for i in range(num_candidates))
model += transport_cost + setup_cost + opex_cost

for j in range(num_demand):
    model += lpSum(x[i][j] for i in range(num_candidates)) == 1
for i in range(num_candidates):
    for j in range(num_demand):
        model += x[i][j] <= y[i]
model += lpSum(y[i] for i in range(num_candidates)) == gudang_harus_buka
for i in range(num_candidates):
    model += lpSum(demand_data.loc[j, 'Jumlah_Truk'] * x[i][j] for j in range(num_demand)) <= jumlah_armada * y[i]
for i in range(num_candidates):
    model += lpSum(demand_data.loc[j, 'Demand'] * x[i][j] for j in range(num_demand)) <= kapasitas_gudang * y[i]

solver_result = model.solve(PULP_CBC_CMD(msg=False))
solver_status = LpStatus[model.status]

# ── STATUS BANNER ─────────────────────────────────────────────────────────────
if solver_status == "Optimal":
    st.success("✅ **Solusi OPTIMAL ditemukan.** Alokasi gudang dengan biaya minimum berhasil dihitung dan memenuhi semua constraint.")

elif solver_status in ("Infeasible", "Undefined", "Not Solved"):
    st.markdown("""
    <div style="background:linear-gradient(135deg,#7f1d1d,#991b1b);border-radius:16px;
                padding:28px 32px;margin-bottom:24px;
                box-shadow:0 8px 32px rgba(153,27,27,0.35);border:1px solid #ef4444;">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">
            <div style="font-size:2.2rem;">❌</div>
            <div>
                <div style="color:white;font-family:'Nunito',sans-serif;font-weight:900;font-size:1.3rem;">
                    Solusi TIDAK LAYAK (Infeasible)
                </div>
                <div style="color:#fca5a5;font-size:0.82rem;margin-top:2px;">
                    Solver tidak dapat menemukan kombinasi alokasi yang memenuhi semua batasan.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if infeasible_reasons:
        st.markdown("#### 🔍 Diagnosa Penyebab")
        for r in infeasible_reasons:
            st.markdown(f"""
            <div style="background:white;border-left:5px solid #EE4D2D;border-radius:10px;
                        padding:16px 20px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
                <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:1rem;color:#991b1b;margin-bottom:6px;">
                    {r['icon']} {r['judul']}
                </div>
                <div style="font-size:0.88rem;color:#374151;margin-bottom:8px;line-height:1.6;">
                    {r['detail']}
                </div>
                <div style="background:#FFF3F0;border-radius:6px;padding:8px 12px;font-size:0.82rem;color:#92400e;">
                    💡 <b>Saran:</b> {r['saran']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:white;border-left:5px solid #EE4D2D;border-radius:10px;
                    padding:16px 20px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:1rem;color:#991b1b;margin-bottom:6px;">
                ⚖️ Distribusi Demand Tidak Seimbang
            </div>
            <div style="font-size:0.88rem;color:#374151;margin-bottom:8px;line-height:1.6;">
                Solver tidak bisa mendistribusikan demand ke <b>{gudang_harus_buka} gudang</b>
                tanpa melanggar constraint armada atau kapasitas pada salah satu kandidat lokasi.
            </div>
            <div style="background:#FFF3F0;border-radius:6px;padding:8px 12px;font-size:0.82rem;color:#92400e;">
                💡 <b>Saran:</b> Tambah kandidat gudang, naikkan armada atau kapasitas, atau kurangi kecamatan demand.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📊 Ringkasan Parameter vs Kebutuhan")
    diag_df = pd.DataFrame({
        "Parameter":    ["Total Demand (unit)", "Total Kebutuhan Rit", "Kapasitas Gudang × p", "Kapasitas Armada × p"],
        "Nilai Aktual": [f"{total_demand_all:,}", f"{total_rit_all}", f"{max_kapasitas_total:,}", f"{max_rit_total}"],
        "Status":       [
            "✅ Cukup" if total_demand_all <= max_kapasitas_total else "❌ Kurang",
            "✅ Cukup" if total_rit_all <= max_rit_total else "❌ Kurang",
            f"{kapasitas_gudang:,} × {gudang_harus_buka}",
            f"{jumlah_armada} × {gudang_harus_buka}",
        ]
    })
    st.dataframe(diag_df, use_container_width=True, hide_index=True)
    st.stop()

else:
    st.warning(f"⚠️ Status solver: **{solver_status}**.")
    st.stop()

# ── HITUNG HASIL ──────────────────────────────────────────────────────────────
gudang_terpilih = [i for i in range(num_candidates) if (value(y[i]) or 0) >= 0.5]

total_truck_trips = sum(
    demand_data.loc[j, 'Jumlah_Truk']
    for i in gudang_terpilih for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5
)
total_transport_cost_rb = sum(
    (
        demand_data.loc[j, 'Jumlah_Truk'] *
        hitung_jarak_km(
            (candidate_data.loc[i, 'Lat'], candidate_data.loc[i, 'Lon']),
            (demand_data.loc[j, 'Lat'],    demand_data.loc[j, 'Lon']),
            km_per_deg
        ) * biaya_truk_per_km
        + demand_data.loc[j, 'Jumlah_Truk'] * fixed_cost_truk
    )
    for i in gudang_terpilih for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5
)
total_transport_cost_jt = total_transport_cost_rb / 1000
total_setup_cost_jt     = sum(biaya_buka[i] for i in gudang_terpilih)
total_opex_cost_jt      = biaya_operasional * len(gudang_terpilih)
total_cost_jt           = total_transport_cost_jt + total_setup_cost_jt + total_opex_cost_jt

utilisasi_armada    = {}
utilisasi_kapasitas = {}
for i in gudang_terpilih:
    utilisasi_armada[i]    = sum(demand_data.loc[j, 'Jumlah_Truk'] for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5)
    utilisasi_kapasitas[i] = sum(demand_data.loc[j, 'Demand']      for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5)

# ── METRICS ───────────────────────────────────────────────────────────────────
st.markdown("### 📊 Ringkasan Hasil Optimasi")
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("🏭 Gudang Terpilih",  f"{len(gudang_terpilih)} / {num_candidates}")
with c2: st.metric("🚛 Total Rit Truk",   f"{total_truck_trips} rit")
with c3: st.metric("📦 Kap. Gudang",      f"{kapasitas_gudang:,} unit")
with c4: st.metric("🛣️ Biaya Transport",  f"Rp {total_transport_cost_jt:,.1f} jt")
with c5: st.metric("💰 Total Biaya",      f"Rp {total_cost_jt:,.1f} jt")

for i in gudang_terpilih:
    pct_arm = utilisasi_armada[i] / jumlah_armada * 100
    pct_kap = utilisasi_kapasitas[i] / kapasitas_gudang * 100
    if pct_arm >= 90:
        st.warning(f"⚠️ **{candidate_data.loc[i, 'Gudang']}** — armada hampir penuh: **{utilisasi_armada[i]}/{jumlah_armada} rit** ({pct_arm:.0f}%)")
    if pct_kap >= 90:
        st.warning(f"⚠️ **{candidate_data.loc[i, 'Gudang']}** — kapasitas gudang hampir penuh: **{utilisasi_kapasitas[i]:,}/{kapasitas_gudang:,} unit** ({pct_kap:.0f}%)")

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️  Peta Distribusi",
    "📋  Analisis Gudang",
    "📊  Breakdown Biaya",
    "📐  Model Matematis"
])

# ── TAB 1: PETA ───────────────────────────────────────────────────────────────
with tab1:
    st.markdown("##### Sebaran titik demand per kecamatan dan rute distribusi truk dari gudang terpilih")

    # Warna per kecamatan
    warna_kec = [
        "#EE4D2D","#3b82f6","#22c55e","#f59e0b","#8b5cf6",
        "#ec4899","#06b6d4","#84cc16","#f97316","#6366f1",
        "#14b8a6","#ef4444","#a855f7","#0ea5e9","#d97706",
        "#10b981","#e11d48","#7c3aed","#0284c7","#65a30d","#dc2626"
    ]
    kec_warna_map = {kec: warna_kec[i % len(warna_kec)] for i, kec in enumerate(kec_terpilih)}

    m = folium.Map(location=[lat_base, lon_base], zoom_start=11, tiles="CartoDB positron")

    # Titik demand berwarna per kecamatan
    for _, row in demand_data.iterrows():
        warna = kec_warna_map.get(row['Kecamatan'], '#EE4D2D')
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=max(3, float(row['Demand']) / 15),
            color=warna, fill=True, fill_color=warna, fill_opacity=0.6,
            popup=folium.Popup(
                f"<b>Kecamatan:</b> {row['Kecamatan']}<br>"
                f"<b>Demand:</b> {row['Demand']} unit<br>"
                f"<b>Kebutuhan:</b> {row['Jumlah_Truk']} Rit",
                max_width=180
            )
        ).add_to(m)

    # Kandidat gudang
    for i, row in candidate_data.iterrows():
        terpilih   = i in gudang_terpilih
        status_txt = "✅ TERPILIH" if terpilih else "❌ Tidak Dipilih"
        rit_info   = (
            f"<br>Utilisasi Armada: {utilisasi_armada.get(i,0)}/{jumlah_armada} rit"
            f"<br>Utilisasi Kapasitas: {utilisasi_kapasitas.get(i,0):,}/{kapasitas_gudang:,} unit"
        ) if terpilih else ""
        popup_html = f"<b>{row['Gudang']}</b><br>{status_txt}<br>Biaya Setup: Rp {biaya_buka[i]:.0f} jt{rit_info}"
        folium.Marker(
            location=[row['Lat'], row['Lon']],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{row['Gudang']} – {status_txt}",
            icon=folium.Icon(color='orange' if terpilih else 'lightgray', icon='home' if terpilih else 'info-sign')
        ).add_to(m)
        if terpilih:
            for j, d_row in demand_data.iterrows():
                if (value(x[i][j]) or 0) >= 0.5:
                    folium.PolyLine(
                        locations=[[row['Lat'], row['Lon']], [d_row['Lat'], d_row['Lon']]],
                        color='#EE4D2D', weight=min(5, int(d_row['Jumlah_Truk'])),
                        opacity=0.4, tooltip=f"{d_row['Jumlah_Truk']} rit truk"
                    ).add_to(m)

    st_folium(m, width="100%", height=520, returned_objects=[])

    # Legend warna kecamatan
    legend_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;">'
    for kec in kec_terpilih:
        w = kec_warna_map[kec]
        legend_html += (
            f'<div style="display:flex;align-items:center;gap:5px;'
            f'background:white;border:1px solid #EDEDED;border-radius:6px;padding:4px 10px;">'
            f'<div style="width:12px;height:12px;border-radius:50%;background:{w};flex-shrink:0;"></div>'
            f'<span style="font-size:0.78rem;color:#333;">{kec}</span></div>'
        )
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)

# ── TAB 2: ANALISIS GUDANG ────────────────────────────────────────────────────
with tab2:
    st.markdown("##### Detail armada dan volume distribusi per gudang terpilih")
    rows = []
    for i in gudang_terpilih:
        served              = [j for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5]
        total_demand_served = utilisasi_kapasitas[i]
        total_rit           = utilisasi_armada[i]
        avg_dist = (
            np.mean([hitung_jarak_km(
                (candidate_data.loc[i, 'Lat'], candidate_data.loc[i, 'Lon']),
                (demand_data.loc[j, 'Lat'], demand_data.loc[j, 'Lon']), km_per_deg
            ) for j in served]) if served else 0
        )
        armada_beroperasi = min(total_rit, jumlah_armada)
        armada_idle       = jumlah_armada - armada_beroperasi
        rows.append({
            "Gudang":              candidate_data.loc[i, 'Gudang'],
            "Agen Dilayani":       len(served),
            "Volume (Unit)":       f"{total_demand_served:,}",
            "Kap. Gudang (Unit)":  f"{kapasitas_gudang:,}",
            "Utilisasi Kap. (%)":  f"{100*total_demand_served/kapasitas_gudang:.1f}%",
            "Total Rit":           total_rit,
            "Kap. Armada":         jumlah_armada,
            "🟢 Armada Beroperasi": armada_beroperasi,
            "⚪ Armada Idle":       armada_idle,
            "Utilisasi Arm. (%)":  f"{100*total_rit/jumlah_armada:.1f}%",
            "Avg. Jarak (km)":     f"{avg_dist:.2f}",
            "Setup (Rp jt)":       f"{biaya_buka[i]:.0f}",
            "Opex (Rp jt)":        f"{biaya_operasional:.0f}",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    total_beroperasi = sum(min(utilisasi_armada[i], jumlah_armada) for i in gudang_terpilih)
    total_idle       = jumlah_armada * len(gudang_terpilih) - total_beroperasi
    total_armada_all = jumlah_armada * len(gudang_terpilih)

    st.markdown(f"""
    <div style="display:flex;gap:12px;margin-top:16px;">
        <div style="flex:1;background:#F0FFF4;border:1.5px solid #86efac;border-radius:10px;padding:14px 18px;text-align:center;">
            <div style="font-size:0.72rem;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.5px;">🟢 Total Armada Beroperasi</div>
            <div style="font-family:'Nunito',sans-serif;font-weight:900;font-size:1.6rem;color:#16a34a;margin:4px 0;">{total_beroperasi}</div>
            <div style="font-size:0.78rem;color:#166534;">dari {total_armada_all} armada total</div>
        </div>
        <div style="flex:1;background:#F5F5F5;border:1.5px solid #d1d5db;border-radius:10px;padding:14px 18px;text-align:center;">
            <div style="font-size:0.72rem;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.5px;">⚪ Total Armada Idle</div>
            <div style="font-family:'Nunito',sans-serif;font-weight:900;font-size:1.6rem;color:#6b7280;margin:4px 0;">{total_idle}</div>
            <div style="font-size:0.78rem;color:#6b7280;">tidak digunakan</div>
        </div>
        <div style="flex:1;background:#FFF3F0;border:1.5px solid #FFDDD6;border-radius:10px;padding:14px 18px;text-align:center;">
            <div style="font-size:0.72rem;font-weight:700;color:#993C1D;text-transform:uppercase;letter-spacing:0.5px;">📊 Utilisasi Armada Total</div>
            <div style="font-family:'Nunito',sans-serif;font-weight:900;font-size:1.6rem;color:#EE4D2D;margin:4px 0;">
                {100*total_beroperasi/total_armada_all:.1f}%
            </div>
            <div style="font-size:0.78rem;color:#993C1D;">{total_beroperasi}/{total_armada_all} rit terpakai</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 3: BREAKDOWN BIAYA ────────────────────────────────────────────────────
with tab3:
    st.markdown("##### Rincian komponen biaya total solusi optimal")
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        cost_df = pd.DataFrame({
            "Komponen Biaya":  ["🚛 Transportasi (Truk)", "🏗️ Setup Gudang", "🏢 Operasional", "💰 TOTAL"],
            "Nilai (Rp juta)": [f"{total_transport_cost_jt:,.2f}", f"{total_setup_cost_jt:,.2f}", f"{total_opex_cost_jt:,.2f}", f"{total_cost_jt:,.2f}"],
            "Proporsi (%)": [
                f"{100*total_transport_cost_jt/total_cost_jt:.1f}%" if total_cost_jt else "-",
                f"{100*total_setup_cost_jt/total_cost_jt:.1f}%"    if total_cost_jt else "-",
                f"{100*total_opex_cost_jt/total_cost_jt:.1f}%"     if total_cost_jt else "-",
                "100%",
            ]
        })
        st.dataframe(cost_df, use_container_width=True, hide_index=True)
    with col_b2:
        st.markdown(f"""
        <div style="background:#FFF3F0;border:1.5px solid #FFDDD6;border-radius:12px;padding:20px;text-align:center;">
            <div style="color:#757575;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Total Biaya Optimal</div>
            <div style="color:#EE4D2D;font-family:'Nunito',sans-serif;font-weight:900;font-size:1.8rem;margin:8px 0;">
                Rp {total_cost_jt:,.1f} jt
            </div>
            <div style="color:#757575;font-size:0.78rem;">{len(gudang_terpilih)} gudang · {total_truck_trips} rit truk</div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 4: MODEL MATEMATIS ────────────────────────────────────────────────────
with tab4:
    st.markdown("##### Formulasi model Mixed-Integer Linear Programming (MILP)")

    st.markdown("**Variabel Keputusan**")
    st.dataframe(pd.DataFrame({
        "Variabel": ["yᵢ", "xᵢⱼ"],
        "Definisi": ["= 1 jika kandidat gudang i dibuka, = 0 jika tidak",
                     "= 1 jika titik demand j dilayani oleh gudang i, = 0 jika tidak"],
        "Tipe": ["Binary", "Binary"],
    }), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("**Fungsi Objektif — Minimasi Total Biaya**")
    st.latex(r"""
        \min \quad Z = \underbrace{\sum_{i}\sum_{j}
        \Bigl(n_j \cdot d_{ij} \cdot c_{km} + n_j \cdot c_{fix}\Bigr) x_{ij}}_{\text{Biaya Transportasi}}
        + \underbrace{\sum_{i} F \cdot y_i}_{\text{Biaya Setup}}
        + \underbrace{\sum_{i} O \cdot y_i}_{\text{Biaya Operasional}}
    """)

    st.divider()
    st.markdown("**Constraint (Batasan Model)**")
    st.markdown("**C1 — Pelayanan Penuh:** setiap titik demand dilayani tepat 1 gudang")
    st.latex(r"\sum_{i} x_{ij} = 1 \qquad \forall \, j")
    st.markdown("**C2 — Konsistensi Gudang:** demand hanya bisa dialokasikan ke gudang yang dibuka")
    st.latex(r"x_{ij} \leq y_i \qquad \forall \, i, \, j")
    st.markdown("**C3 — Jumlah Gudang:** jumlah gudang yang dibuka harus tepat p")
    st.latex(r"\sum_{i} y_i = p")
    st.markdown("**C4 — Kapasitas Armada:** total rit truk per gudang tidak boleh melebihi kapasitas armada")
    st.latex(r"\sum_{j} n_j \cdot x_{ij} \leq A \cdot y_i \qquad \forall \, i")
    st.markdown("**C5 — Kapasitas Gudang:** total volume barang per gudang tidak boleh melebihi kapasitas gudang")
    st.latex(r"\sum_{j} \text{demand}_j \cdot x_{ij} \leq W \cdot y_i \qquad \forall \, i")
    st.markdown("**Domain Variabel**")
    st.latex(r"y_i \in \{0,1\} \quad \forall\,i \qquad x_{ij} \in \{0,1\} \quad \forall\,i,j")

    st.divider()
    st.markdown("**Notasi Parameter**")
    st.dataframe(pd.DataFrame({
        "Simbol": ["i", "j", "nⱼ", "dᵢⱼ", "c_km", "c_fix", "F", "O", "p", "A", "W"],
        "Keterangan": [
            "Indeks kandidat gudang",
            "Indeks titik demand",
            "Jumlah rit truk untuk demand j = ⌈demand_j / kapasitas_truk⌉",
            "Jarak Euclidean (km) dari gudang i ke titik demand j",
            "Biaya operasional truk per km (Rp ribu)",
            "Biaya tetap per rit truk (Rp ribu)",
            "Biaya pembukaan gudang (Rp)",
            "Biaya operasional bulanan per gudang (Rp)",
            "Jumlah gudang yang harus dibuka",
            "Jumlah armada truk tersedia per gudang",
            "Kapasitas maksimal volume barang per gudang (unit)",
        ],
        "Nilai Saat Ini": [
            f"0 s/d {num_candidates-1}", f"0 s/d {num_demand-1}",
            "Dihitung otomatis", "Dihitung otomatis",
            f"Rp {biaya_truk_per_km:.1f} rb/km", f"Rp {fixed_cost_truk:.1f} rb/rit",
            f"Rp {biaya_buka_per_gudang:.0f} jt", f"Rp {biaya_operasional:.0f} jt/bulan",
            str(gudang_harus_buka), str(jumlah_armada), f"{kapasitas_gudang:,} unit",
        ],
    }), use_container_width=True, hide_index=True)
