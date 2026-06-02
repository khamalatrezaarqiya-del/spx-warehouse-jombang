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

# ── SHOPEE THEME CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=DM+Sans:wght@400;500;600&display=swap');

:root {
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

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--shopee-text);
}
.stApp { background: var(--shopee-gray); }

h1 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 900 !important; font-size: 1.8rem !important;
    color: var(--shopee-orange) !important; letter-spacing: -0.5px;
    margin-bottom: 0 !important;
}
h2 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important; font-size: 1.15rem !important;
    color: var(--shopee-dark) !important; margin-top: 0.5rem !important;
}
h3 { font-family: 'Nunito', sans-serif !important; font-weight: 700 !important; color: var(--shopee-dark) !important; }

.stApp [data-testid="stCaptionContainer"] p { color: var(--shopee-subtext) !important; font-size: 0.82rem !important; }

section[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 2px solid var(--shopee-orange-mid);
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span { color: var(--shopee-dark) !important; }

.stNumberInput input, .stTextInput input {
    border: 1.5px solid var(--shopee-gray-2) !important;
    border-radius: var(--radius-sm) !important;
    background: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s;
}
.stNumberInput input:focus, .stTextInput input:focus {
    border-color: var(--shopee-orange) !important;
    box-shadow: 0 0 0 3px rgba(238,77,45,0.12) !important;
}

[data-testid="metric-container"] {
    background: var(--white) !important;
    border: 1.5px solid var(--shopee-orange-mid) !important;
    border-radius: var(--radius) !important;
    padding: 16px 20px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow 0.2s, transform 0.2s;
}
[data-testid="metric-container"]:hover { box-shadow: var(--shadow-md) !important; transform: translateY(-2px); }
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; font-weight: 600 !important; color: var(--shopee-subtext) !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { font-family: 'Nunito', sans-serif !important; font-weight: 900 !important; font-size: 1.4rem !important; color: var(--shopee-orange) !important; }

.stButton > button {
    background: linear-gradient(135deg, var(--shopee-orange), var(--shopee-orange-2)) !important;
    color: white !important; border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    padding: 8px 22px !important; transition: opacity 0.2s, transform 0.15s;
}
.stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }

.stSuccess { background: #F0FFF4 !important; border-left: 4px solid #22c55e !important; border-radius: var(--radius-sm) !important; }
.stError   { background: #FFF5F5 !important; border-left: 4px solid var(--shopee-orange) !important; border-radius: var(--radius-sm) !important; }
.stWarning { background: #FFFBEB !important; border-left: 4px solid #f59e0b !important; border-radius: var(--radius-sm) !important; }
.stInfo    { background: var(--shopee-orange-lt) !important; border-left: 4px solid var(--shopee-orange) !important; border-radius: var(--radius-sm) !important; }

[data-testid="stDataFrame"] { border-radius: var(--radius) !important; overflow: hidden; border: 1px solid var(--shopee-orange-mid) !important; box-shadow: var(--shadow-sm); }

.streamlit-expanderHeader {
    background: var(--shopee-orange-lt) !important;
    border-radius: var(--radius-sm) !important; font-weight: 700 !important;
    color: var(--shopee-orange) !important; border: 1px solid var(--shopee-orange-mid) !important;
}

hr { border-color: var(--shopee-orange-mid) !important; margin: 12px 0 !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--white); border-radius: var(--radius);
    padding: 4px; gap: 4px; border: 1px solid var(--shopee-orange-mid);
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    color: var(--shopee-subtext) !important; padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--shopee-orange), var(--shopee-orange-2)) !important;
    color: white !important;
}

.sidebar-section {
    font-family: 'Nunito', sans-serif; font-weight: 800;
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.2px;
    color: #EE4D2D !important; padding: 6px 0 4px 0;
    border-bottom: 2px solid #FFDDD6; margin-bottom: 6px;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--shopee-gray); }
::-webkit-scrollbar-thumb { background: var(--shopee-orange-mid); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--shopee-orange); }
</style>
""", unsafe_allow_html=True)

# ── TOP HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#EE4D2D 0%,#F85606 100%);
            border-radius:12px; padding:18px 28px; margin-bottom:20px;
            display:flex; align-items:center; justify-content:space-between;
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

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#EE4D2D,#F85606);
                border-radius:10px;padding:12px 16px;margin-bottom:16px;">
        <div style="color:white;font-family:'Nunito',sans-serif;font-weight:900;font-size:1rem;">⚙️ Parameter Simulasi</div>
        <div style="color:rgba(255,255,255,0.8);font-size:0.75rem;margin-top:2px;">Atur semua parameter di bawah ini</div>
    </div>
    """, unsafe_allow_html=True)

    # — Demand & Kandidat —
    st.markdown('<div class="sidebar-section">📍 Titik Demand & Kandidat</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        num_demand = st.number_input("Titik Demand", min_value=1, value=40, step=5,
                                     help="Jumlah agen/user sebagai titik demand")
    with col_s2:
        num_candidates = st.number_input("Kandidat Gudang", min_value=1, value=5, step=1,
                                         help="Jumlah kandidat lokasi gudang")
    gudang_harus_buka = st.number_input(
        "Gudang Harus Dibuka", min_value=1, max_value=num_candidates, value=2, step=1
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
                                             step=0.5, format="%.1f",
                                             help="Biaya operasional per kilometer")
    with col_t4:
        fixed_cost_truk = st.number_input("Fixed/Rit (Rp rb)", min_value=0.0, value=150.0,
                                           step=10.0, format="%.1f",
                                           help="Biaya tetap per rit truk")

    st.divider()

    # — Biaya Gudang —
    st.markdown('<div class="sidebar-section">🏢 Biaya Gudang</div>', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        biaya_operasional = st.number_input("Opex/Gudang (Rp jt)", min_value=0.0,
                                             value=50.0, step=5.0, format="%.1f",
                                             help="Biaya operasional bulanan per gudang")
    with col_g2:
        km_per_deg = st.number_input("1° = ? km", min_value=50.0, value=111.0,
                                      step=1.0, format="%.1f",
                                      help="Konversi derajat koordinat ke kilometer")

    st.divider()

    # — Biaya Pembukaan (1 input untuk semua gudang) —
    st.markdown('<div class="sidebar-section">🏗️ Biaya Pembukaan Gudang</div>', unsafe_allow_html=True)
    biaya_buka_per_gudang = st.number_input(
        "Biaya Pembukaan per Gudang (Rp jt)",
        min_value=0.0, value=100.0, step=10.0, format="%.1f",
        help="Biaya ini berlaku sama untuk semua kandidat gudang"
    )

# ── DATA GENERATOR ────────────────────────────────────────────────────────────
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
}
kec_list = list(kecamatan_jombang.values())
lat_base, lon_base = -7.5466, 112.2384

rng_d = np.random.default_rng(42)
rng_c = np.random.default_rng(99)

demand_lats, demand_lons = [], []
for _ in range(num_demand):
    center = kec_list[rng_d.integers(0, len(kec_list))]
    demand_lats.append(float(center[0]) + rng_d.normal(0, 0.025))
    demand_lons.append(float(center[1]) + rng_d.normal(0, 0.025))

demand_data = pd.DataFrame({
    'Lat':    demand_lats,
    'Lon':    demand_lons,
    'Demand': rng_d.integers(10, 120, num_demand)
})
demand_data['Jumlah_Truk'] = np.ceil(demand_data['Demand'] / kapasitas_truk).astype(int)

candidate_lats, candidate_lons = [], []
for i in range(num_candidates):
    center = kec_list[i % len(kec_list)]
    candidate_lats.append(float(center[0]) + rng_c.uniform(-0.02, 0.02))
    candidate_lons.append(float(center[1]) + rng_c.uniform(-0.02, 0.02))

candidate_data = pd.DataFrame({
    'Gudang': [f"Kandidat Gudang {i+1}" for i in range(num_candidates)],
    'Lat':    candidate_lats,
    'Lon':    candidate_lons,
})

# Biaya buka seragam untuk semua kandidat
biaya_buka = [biaya_buka_per_gudang] * num_candidates

# ── HELPER ────────────────────────────────────────────────────────────────────
def hitung_jarak_km(p1, p2, km_per_deg):
    return math.sqrt(((p1[0]-p2[0])*km_per_deg)**2 + ((p1[1]-p2[1])*km_per_deg)**2)

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

# Constraint 1: setiap demand dilayani tepat 1 gudang
for j in range(num_demand):
    model += lpSum(x[i][j] for i in range(num_candidates)) == 1

# Constraint 2: demand hanya bisa ke gudang yang dibuka
for i in range(num_candidates):
    for j in range(num_demand):
        model += x[i][j] <= y[i]

# Constraint 3: jumlah gudang yang dibuka = p
model += lpSum(y[i] for i in range(num_candidates)) == gudang_harus_buka

# Constraint 4: total rit per gudang <= kapasitas armada
for i in range(num_candidates):
    model += lpSum(
        demand_data.loc[j, 'Jumlah_Truk'] * x[i][j] for j in range(num_demand)
    ) <= jumlah_armada * y[i]

solver_result = model.solve(PULP_CBC_CMD(msg=False))
solver_status = LpStatus[model.status]

# ── STATUS BANNER ─────────────────────────────────────────────────────────────
STATUS_INFO = {
    "Optimal": {
        "fn":  st.success,
        "msg": "✅ **Solusi OPTIMAL ditemukan.** Alokasi gudang dengan biaya minimum berhasil dihitung dan memenuhi semua constraint armada truk.",
    },
    "Infeasible": {
        "fn":  st.error,
        "msg": "❌ **Solusi TIDAK LAYAK (Infeasible).** Tidak ada kombinasi gudang yang memenuhi semua constraint. "
               "**Kemungkinan penyebab:** armada truk terlalu sedikit. Coba tambah jumlah armada, kurangi titik demand, atau buka lebih banyak gudang.",
    },
    "Undefined": {
        "fn":  st.warning,
        "msg": "⚠️ **Status TIDAK TERDEFINISI.** Solver tidak dapat menentukan solusi. Periksa parameter input.",
    },
    "Not Solved": {
        "fn":  st.warning,
        "msg": "⚠️ **Model BELUM DISELESAIKAN.** Solver berhenti sebelum menemukan solusi.",
    },
}

info = STATUS_INFO.get(solver_status, {"fn": st.warning, "msg": f"⚠️ Status solver: **{solver_status}**."})
info["fn"](info["msg"])

if solver_status not in ("Optimal", "Feasible"):
    st.info("Tidak ada hasil yang bisa ditampilkan. Sesuaikan parameter di sidebar.")
    st.stop()

# ── HITUNG HASIL ──────────────────────────────────────────────────────────────
gudang_terpilih = [i for i in range(num_candidates) if (value(y[i]) or 0) >= 0.5]

total_truck_trips = sum(
    demand_data.loc[j, 'Jumlah_Truk']
    for i in gudang_terpilih
    for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5
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
    for i in gudang_terpilih
    for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5
)
total_transport_cost_jt = total_transport_cost_rb / 1000
total_setup_cost_jt     = sum(biaya_buka[i] for i in gudang_terpilih)
total_opex_cost_jt      = biaya_operasional * len(gudang_terpilih)
total_cost_jt           = total_transport_cost_jt + total_setup_cost_jt + total_opex_cost_jt

utilisasi_armada = {}
for i in gudang_terpilih:
    rit = sum(demand_data.loc[j, 'Jumlah_Truk'] for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5)
    utilisasi_armada[i] = rit

# ── METRICS ───────────────────────────────────────────────────────────────────
st.markdown("### 📊 Ringkasan Hasil Optimasi")
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("🏭 Gudang Terpilih",  f"{len(gudang_terpilih)} / {num_candidates}")
with c2: st.metric("🚛 Total Rit Truk",   f"{total_truck_trips} rit")
with c3: st.metric("🚗 Armada / Gudang",  f"{jumlah_armada} truk")
with c4: st.metric("🛣️ Biaya Transport",  f"Rp {total_transport_cost_jt:,.1f} jt")
with c5: st.metric("💰 Total Biaya",      f"Rp {total_cost_jt:,.1f} jt")

for i in gudang_terpilih:
    pct = utilisasi_armada[i] / jumlah_armada * 100
    if pct >= 90:
        st.warning(
            f"⚠️ **{candidate_data.loc[i, 'Gudang']}** menggunakan **{utilisasi_armada[i]} rit** "
            f"dari {jumlah_armada} armada ({pct:.0f}%) — hampir penuh!"
        )

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
    st.markdown("##### Sebaran titik demand dan rute distribusi truk dari gudang terpilih")

    m = folium.Map(location=[lat_base, lon_base], zoom_start=11, tiles="CartoDB positron")

    for _, row in demand_data.iterrows():
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=max(3, float(row['Demand']) / 15),
            color='#EE4D2D', fill=True, fill_color='#EE4D2D', fill_opacity=0.45,
            popup=folium.Popup(
                f"<b>Demand:</b> {row['Demand']} unit<br><b>Kebutuhan:</b> {row['Jumlah_Truk']} Rit",
                max_width=160
            )
        ).add_to(m)

    for i, row in candidate_data.iterrows():
        terpilih   = i in gudang_terpilih
        warna      = 'orange' if terpilih else 'lightgray'
        status_txt = "✅ TERPILIH" if terpilih else "❌ Tidak Dipilih"
        rit_info   = f"<br>Utilisasi: {utilisasi_armada.get(i,0)}/{jumlah_armada} rit" if terpilih else ""
        popup_html = (
            f"<b>{row['Gudang']}</b><br>{status_txt}"
            f"<br>Biaya Setup: Rp {biaya_buka[i]:.0f} jt"
            f"{rit_info}"
        )
        folium.Marker(
            location=[row['Lat'], row['Lon']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{row['Gudang']} – {status_txt}",
            icon=folium.Icon(color=warna, icon='home' if terpilih else 'info-sign')
        ).add_to(m)

        if terpilih:
            for j, d_row in demand_data.iterrows():
                if (value(x[i][j]) or 0) >= 0.5:
                    folium.PolyLine(
                        locations=[[row['Lat'], row['Lon']], [d_row['Lat'], d_row['Lon']]],
                        color='#EE4D2D', weight=min(5, int(d_row['Jumlah_Truk'])),
                        opacity=0.45, tooltip=f"{d_row['Jumlah_Truk']} rit truk"
                    ).add_to(m)

    st_folium(m, width="100%", height=520, returned_objects=[])

# ── TAB 2: ANALISIS GUDANG ────────────────────────────────────────────────────
with tab2:
    st.markdown("##### Detail armada dan volume distribusi per gudang terpilih")

    rows = []
    for i in gudang_terpilih:
        served              = [j for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5]
        total_demand_served = sum(demand_data.loc[j, 'Demand'] for j in served)
        total_rit           = utilisasi_armada[i]
        avg_dist = (
            np.mean([
                hitung_jarak_km(
                    (candidate_data.loc[i, 'Lat'], candidate_data.loc[i, 'Lon']),
                    (demand_data.loc[j, 'Lat'],    demand_data.loc[j, 'Lon']),
                    km_per_deg
                ) for j in served
            ]) if served else 0
        )
        utilisasi_pct = total_rit / jumlah_armada * 100
        rows.append({
            "Gudang":           candidate_data.loc[i, 'Gudang'],
            "Agen Dilayani":    len(served),
            "Volume (Unit)":    total_demand_served,
            "Total Rit":        total_rit,
            "Kapasitas":        jumlah_armada,
            "Utilisasi (%)":    f"{utilisasi_pct:.1f}%",
            "Avg. Jarak (km)":  f"{avg_dist:.2f}",
            "Setup (Rp jt)":    f"{biaya_buka[i]:.0f}",
            "Opex (Rp jt)":     f"{biaya_operasional:.0f}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── TAB 3: BREAKDOWN BIAYA ────────────────────────────────────────────────────
with tab3:
    st.markdown("##### Rincian komponen biaya total solusi optimal")

    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        cost_df = pd.DataFrame({
            "Komponen Biaya":  ["🚛 Transportasi (Truk)", "🏗️ Setup Gudang", "🏢 Operasional", "💰 TOTAL"],
            "Nilai (Rp juta)": [
                f"{total_transport_cost_jt:,.2f}",
                f"{total_setup_cost_jt:,.2f}",
                f"{total_opex_cost_jt:,.2f}",
                f"{total_cost_jt:,.2f}",
            ],
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
        <div style="background:#FFF3F0;border:1.5px solid #FFDDD6;
                    border-radius:12px;padding:20px;text-align:center;">
            <div style="color:#757575;font-size:0.75rem;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.5px;">Total Biaya Optimal</div>
            <div style="color:#EE4D2D;font-family:'Nunito',sans-serif;
                        font-weight:900;font-size:1.8rem;margin:8px 0;">
                Rp {total_cost_jt:,.1f} jt
            </div>
            <div style="color:#757575;font-size:0.78rem;">
                {len(gudang_terpilih)} gudang · {total_truck_trips} rit truk
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 4: MODEL MATEMATIS ────────────────────────────────────────────────────
with tab4:
    st.markdown("##### Formulasi model Mixed-Integer Linear Programming (MILP)")

    # — Variabel Keputusan —
    st.markdown("**Variabel Keputusan**")
    var_df = pd.DataFrame({
        "Variabel": ["y_i", "x_ij"],
        "Definisi": [
            "= 1 jika kandidat gudang i dibuka, = 0 jika tidak",
            "= 1 jika titik demand j dilayani oleh gudang i, = 0 jika tidak",
        ],
        "Tipe": ["Binary", "Binary"],
    })
    st.dataframe(var_df, use_container_width=True, hide_index=True)

    st.divider()

    # — Fungsi Objektif —
    st.markdown("**Fungsi Objektif — Minimasi Total Biaya**")
    obj_df = pd.DataFrame({
        "Komponen": [
            "Biaya Transportasi",
            "Biaya Setup Gudang",
            "Biaya Operasional",
        ],
        "Formulasi": [
            "SUM_i SUM_j [ (n_j * d_ij * c_km) + (n_j * c_fix) ] * x_ij",
            "SUM_i  F * y_i",
            "SUM_i  O * y_i",
        ],
        "Keterangan": [
            "n_j = jumlah rit truk demand j, d_ij = jarak (km), c_km = biaya/km, c_fix = biaya tetap/rit",
            "F = biaya pembukaan gudang (sama untuk semua kandidat)",
            "O = biaya operasional bulanan per gudang",
        ],
    })
    st.dataframe(obj_df, use_container_width=True, hide_index=True)

    st.divider()

    # — Constraint —
    st.markdown("**Constraint (Batasan Model)**")
    con_df = pd.DataFrame({
        "No.": ["C1", "C2", "C3", "C4"],
        "Nama": [
            "Pelayanan Penuh",
            "Konsistensi Gudang",
            "Jumlah Gudang",
            "Kapasitas Armada",
        ],
        "Formulasi": [
            "SUM_i x_ij = 1,  untuk setiap j",
            "x_ij <= y_i,  untuk setiap i dan j",
            "SUM_i y_i = p",
            "SUM_j (n_j * x_ij) <= A * y_i,  untuk setiap i",
        ],
        "Penjelasan": [
            "Setiap titik demand harus dilayani oleh tepat 1 gudang",
            "Demand hanya bisa dialokasikan ke gudang yang dibuka",
            "Jumlah gudang yang dibuka harus tepat p (sesuai input)",
            "Total rit truk per gudang tidak boleh melebihi kapasitas armada A",
        ],
    })
    st.dataframe(con_df, use_container_width=True, hide_index=True)

    st.divider()

    # — Notasi Lengkap —
    st.markdown("**Notasi Parameter**")
    notasi_df = pd.DataFrame({
        "Simbol": ["i", "j", "n_j", "d_ij", "c_km", "c_fix", "F", "O", "p", "A"],
        "Keterangan": [
            "Indeks kandidat gudang",
            "Indeks titik demand",
            "Jumlah rit truk untuk demand j = ceil(demand_j / kapasitas_truk)",
            "Jarak Euclidean (km) dari gudang i ke titik demand j",
            "Biaya operasional truk per km (Rp ribu)",
            "Biaya tetap per rit truk — uang jalan, tol, dll (Rp ribu)",
            "Biaya pembukaan gudang, berlaku sama untuk semua kandidat (Rp)",
            "Biaya operasional bulanan per gudang (Rp)",
            "Jumlah gudang yang harus dibuka (input user)",
            "Jumlah armada truk tersedia per gudang (input user)",
        ],
        "Nilai Saat Ini": [
            f"0 s/d {num_candidates-1}",
            f"0 s/d {num_demand-1}",
            "Dihitung otomatis",
            "Dihitung otomatis",
            f"Rp {biaya_truk_per_km:.1f} rb/km",
            f"Rp {fixed_cost_truk:.1f} rb/rit",
            f"Rp {biaya_buka_per_gudang:.0f} jt",
            f"Rp {biaya_operasional:.0f} jt/bulan",
            str(gudang_harus_buka),
            str(jumlah_armada),
        ],
    })
    st.dataframe(notasi_df, use_container_width=True, hide_index=True)
