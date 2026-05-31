import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from pulp import *
import math

st.set_page_config(layout="wide", page_title="SPX Warehouse Optimizer – Jombang")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stAlert { border-radius: 10px; }
section[data-testid="stSidebar"] { background: #0d1117; }
</style>
""", unsafe_allow_html=True)

st.title("🚚 Simulasi Alokasi Gudang Strategis SPX")
st.caption("Optimasi fasilitas berbasis Mixed-Integer Linear Programming · Lokasi: Kabupaten Jombang, Jawa Timur")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Parameter Simulasi")

    st.subheader("📍 Titik Demand & Kandidat")
    num_demand        = st.number_input("Jumlah Titik Demand (Agen/User)", min_value=1, value=40, step=5)
    num_candidates    = st.number_input("Jumlah Kandidat Lokasi Gudang", min_value=1, value=5, step=1)
    gudang_harus_buka = st.number_input("Jumlah Gudang yang Harus Dibuka", min_value=1, value=2, step=1)

    st.divider()
    st.subheader("🚛 Parameter Armada Truk")

    kapasitas_truk = st.number_input(
        "Kapasitas Maksimal 1 Truk (Unit Barang)",
        min_value=10, value=50, step=5,
        help="Jika demand melebihi angka ini, otomatis dihitung multi-rit."
    )
    jumlah_armada = st.number_input(
        "Jumlah Armada Truk Tersedia (per Gudang)",
        min_value=1, value=5, step=1,
        help="Batas maksimal truk yang bisa dioperasikan per gudang. "
             "Jika total rit melebihi ini, solusi dinyatakan TIDAK LAYAK."
    )
    biaya_truk_per_km = st.number_input(
        "Biaya Operasional Truk per km (Rp ribu)",
        min_value=0.0, value=5.0, step=0.5, format="%.1f",
        help="Biaya bensin + keausan truk per kilometer."
    )
    fixed_cost_truk = st.number_input(
        "Biaya Tetap / Uang Jalan per Rit Truk (Rp ribu)",
        min_value=0.0, value=150.0, step=10.0, format="%.1f",
        help="Uang jalan sopir, tol, atau biaya sewa dasar per perjalanan."
    )

    st.divider()
    st.subheader("🏢 Parameter Biaya Gudang")
    biaya_operasional = st.number_input(
        "Biaya Operasional / Gudang (Rp juta/bulan)",
        min_value=0.0, value=50.0, step=5.0, format="%.1f"
    )
    km_per_deg = st.number_input(
        "Konversi: 1 derajat = ? km",
        min_value=50.0, value=111.0, step=1.0, format="%.1f"
    )

    st.divider()
    st.subheader("🏗️ Biaya Pembukaan Per Kandidat Gudang")

# ── DATA GENERATOR ────────────────────────────────────────────────────────────
kecamatan_jombang = {
    "Jombang Kota": [-7.5568, 112.2332],
    "Peterongan":   [-7.5461, 112.2714],
    "Mojoagung":    [-7.5684, 112.3364],
    "Ploso":        [-7.4566, 112.2152],
    "Ngoro":        [-7.6841, 112.2592],
    "Diwek":        [-7.5936, 112.2185],
    "Sumobito":     [-7.5200, 112.3100],
    "Kesamben":     [-7.6200, 112.3600],
    "Bandarkedungmulyo": [-7.5100, 112.1700],
    "Wonosalam":    [-7.6500, 112.3900],
}
kec_list   = list(kecamatan_jombang.values())
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

biaya_buka = []
with st.sidebar:
    for i in range(num_candidates):
        b = st.number_input(
            f"Gudang {i+1} (Rp juta)",
            min_value=0.0, value=float(100 + i * 20), step=10.0,
            key=f"biaya_buka_{i}", format="%.1f"
        )
        biaya_buka.append(b)

# ── HELPER ────────────────────────────────────────────────────────────────────
def hitung_jarak_km(p1, p2, km_per_deg):
    return math.sqrt(((p1[0]-p2[0])*km_per_deg)**2 + ((p1[1]-p2[1])*km_per_deg)**2)

# ── MODEL OPTIMASI ────────────────────────────────────────────────────────────
model = LpProblem("Facility_Location_Truck_Fleet", LpMinimize)

y = LpVariable.dicts("Buka_Gudang", range(num_candidates), cat='Binary')
x = LpVariable.dicts("Alokasi", (range(num_candidates), range(num_demand)), cat='Binary')

# Objective
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

# Constraints
for j in range(num_demand):
    model += lpSum(x[i][j] for i in range(num_candidates)) == 1

for i in range(num_candidates):
    for j in range(num_demand):
        model += x[i][j] <= y[i]

model += lpSum(y[i] for i in range(num_candidates)) == gudang_harus_buka

# ── CONSTRAINT ARMADA: total rit per gudang <= jumlah_armada ──────────────────
for i in range(num_candidates):
    model += lpSum(
        demand_data.loc[j, 'Jumlah_Truk'] * x[i][j] for j in range(num_demand)
    ) <= jumlah_armada * y[i]

# Solve
solver_result = model.solve(PULP_CBC_CMD(msg=False))
solver_status = LpStatus[model.status]   # "Optimal", "Infeasible", "Undefined", dll.

# ── STATUS BANNER ─────────────────────────────────────────────────────────────
st.divider()

STATUS_INFO = {
    "Optimal": {
        "fn":  st.success,
        "msg": "✅ **Solusi OPTIMAL ditemukan.** Model berhasil menemukan alokasi gudang dengan biaya minimum yang memenuhi semua constraint termasuk batas armada truk.",
    },
    "Infeasible": {
        "fn":  st.error,
        "msg": "❌ **Solusi TIDAK LAYAK (Infeasible).** Tidak ada kombinasi gudang yang bisa memenuhi semua constraint sekaligus. "
               "Kemungkinan penyebab: **jumlah armada truk terlalu sedikit** untuk melayani semua titik demand dari gudang yang tersedia. "
               "Coba tambah jumlah armada, kurangi titik demand, atau buka lebih banyak gudang.",
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

info = STATUS_INFO.get(solver_status, {
    "fn": st.warning,
    "msg": f"⚠️ Status solver: **{solver_status}**. Solusi mungkin tidak valid."
})
info["fn"](info["msg"])

# Hanya tampilkan hasil jika solver menemukan solusi valid
if solver_status not in ("Optimal", "Feasible"):
    st.info("Tidak ada hasil yang bisa ditampilkan karena model tidak menghasilkan solusi yang valid. Sesuaikan parameter di sidebar.")
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

# Cek utilisasi armada per gudang terpilih
utilisasi_armada = {}
for i in gudang_terpilih:
    rit = sum(demand_data.loc[j, 'Jumlah_Truk'] for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5)
    utilisasi_armada[i] = rit

# ── METRICS ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("🏭 Gudang Terpilih",   f"{len(gudang_terpilih)} dari {num_candidates}")
with c2: st.metric("🚛 Total Rit Truk",    f"{total_truck_trips} rit")
with c3: st.metric("🚗 Armada / Gudang",   f"{jumlah_armada} truk")
with c4: st.metric("🛣️ Biaya Transport",   f"Rp {total_transport_cost_jt:,.1f} jt")
with c5: st.metric("💰 Total Biaya",       f"Rp {total_cost_jt:,.1f} jt")

# Warning jika ada gudang yang utilisasi armadanya mepet
for i in gudang_terpilih:
    pct = utilisasi_armada[i] / jumlah_armada * 100
    if pct >= 90:
        st.warning(
            f"⚠️ **{candidate_data.loc[i, 'Gudang']}** menggunakan **{utilisasi_armada[i]} rit** "
            f"dari kapasitas {jumlah_armada} armada ({pct:.0f}%). Armada hampir penuh!"
        )

# ── PETA ──────────────────────────────────────────────────────────────────────
st.subheader("🗺️ Peta Sebaran Demand & Rute Distribusi Truk – Kabupaten Jombang")

m = folium.Map(location=[lat_base, lon_base], zoom_start=11, tiles="CartoDB positron")

for _, row in demand_data.iterrows():
    folium.CircleMarker(
        location=[row['Lat'], row['Lon']],
        radius=max(3, float(row['Demand']) / 15),
        color='#3b82f6', fill=True, fill_color='#3b82f6', fill_opacity=0.5,
        popup=folium.Popup(
            f"<b>Demand:</b> {row['Demand']} unit<br><b>Kebutuhan:</b> {row['Jumlah_Truk']} Rit Truk",
            max_width=160
        )
    ).add_to(m)

for i, row in candidate_data.iterrows():
    terpilih   = i in gudang_terpilih
    warna      = 'green' if terpilih else 'lightgray'
    status_txt = "✅ TERPILIH" if terpilih else "❌ Tidak Terpilih"
    rit_info   = f"<br>Utilisasi Armada: {utilisasi_armada.get(i,0)}/{jumlah_armada} rit" if terpilih else ""
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
                    color='#22c55e',
                    weight=min(5, int(d_row['Jumlah_Truk'])),
                    opacity=0.55,
                    tooltip=f"{d_row['Jumlah_Truk']} rit truk"
                ).add_to(m)

st_folium(m, width="100%", height=520, returned_objects=[])

# ── TABEL DETAIL GUDANG ───────────────────────────────────────────────────────
st.subheader("📋 Analisis Armada Distribusi Gudang Terpilih")

rows = []
for i in gudang_terpilih:
    served              = [j for j in range(num_demand) if (value(x[i][j]) or 0) >= 0.5]
    total_demand_served = sum(demand_data.loc[j, 'Demand'] for j in served)
    total_rit           = utilisasi_armada[i]
    avg_dist            = (
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
        "Gudang":                 candidate_data.loc[i, 'Gudang'],
        "Titik Agen Dilayani":    len(served),
        "Total Volume (Unit)":    total_demand_served,
        "Total Ritase Truk":      total_rit,
        "Kapasitas Armada":       jumlah_armada,
        "Utilisasi Armada (%)":   f"{utilisasi_pct:.1f}%",
        "Rata-rata Jarak (km)":   f"{avg_dist:.2f}",
        "Biaya Setup (Rp jt)":    f"{biaya_buka[i]:.0f}",
        "Biaya Opex (Rp jt)":     f"{biaya_operasional:.0f}",
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── BREAKDOWN BIAYA ───────────────────────────────────────────────────────────
with st.expander("📊 Breakdown Biaya Lengkap"):
    cost_df = pd.DataFrame({
        "Komponen Biaya":  ["Transportasi (Truk)", "Setup Gudang", "Operasional", "TOTAL"],
        "Nilai (Rp juta)": [
            f"{total_transport_cost_jt:,.2f}",
            f"{total_setup_cost_jt:,.2f}",
            f"{total_opex_cost_jt:,.2f}",
            f"{total_cost_jt:,.2f}",
        ],
        "Proporsi (%)": [
            f"{100*total_transport_cost_jt/total_cost_jt:.1f}%" if total_cost_jt else "-",
            f"{100*total_setup_cost_jt/total_cost_jt:.1f}%"     if total_cost_jt else "-",
            f"{100*total_opex_cost_jt/total_cost_jt:.1f}%"      if total_cost_jt else "-",
            "100%",
        ]
    })
    st.dataframe(cost_df, use_container_width=True, hide_index=True)
