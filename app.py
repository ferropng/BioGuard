import streamlit as st
import pandas as pd
import folium
import plotly.express as px

from folium.plugins import HeatMap
from streamlit_folium import st_folium

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="BioGuard",
    page_icon="🌎",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("🌎 BioGuard")
st.subheader("Monitoramento Inteligente de Queimadas e Fauna Brasileira")

# ============================================================
# LOAD DATA
# ============================================================

arquivo = "bdqueimadas_2026-05-27_2026-05-28.csv"

df = pd.read_csv(arquivo)

df.columns = df.columns.str.lower().str.strip()

# Detectar latitude e longitude
col_lat = None
col_lon = None

for col in df.columns:

    if "lat" in col:
        col_lat = col

    if "lon" in col or "long" in col:
        col_lon = col

st.write("Coluna latitude:", col_lat)
st.write("Coluna longitude:", col_lon)

# ============================================================
# KPIS
# ============================================================

col1, col2 = st.columns(2)

col1.metric(
    "🔥 Queimadas",
    len(df)
)

col2.metric(
    "🐾 Espécies monitoradas",
    5
)

# ============================================================
# MAPA
# ============================================================

st.header("🗺️ Mapa de Queimadas")

mapa = folium.Map(
    location=[-14, -55],
    zoom_start=4
)

if col_lat and col_lon:

    mapa_df = df.dropna(subset=[col_lat, col_lon])

    heat_data = mapa_df[[col_lat, col_lon]].values.tolist()

    HeatMap(
        heat_data,
        radius=12
    ).add_to(mapa)

# Marcadores fauna
marcadores = [
    [-16, -56, "🐾 Onça-pintada"],
    [-18, -57, "🐦 Arara-azul"],
    [-3, -60, "🐒 Sauim-de-coleira"]
]

for lat, lon, nome in marcadores:

    folium.Marker(
        location=[lat, lon],
        popup=nome
    ).add_to(mapa)

st_folium(
    mapa,
    width=1200,
    height=600
)

# ============================================================
# DASHBOARD
# ============================================================

st.header("📊 Dashboard")

# Detectar bioma
coluna_bioma = None

for col in df.columns:
    if "bioma" in col:
        coluna_bioma = col

if coluna_bioma:

    fig = px.histogram(
        df,
        x=coluna_bioma,
        color=coluna_bioma,
        title="Queimadas por Bioma"
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TABELA
# ============================================================

st.header("📋 Dados") 
st.dataframe(df.head(100))