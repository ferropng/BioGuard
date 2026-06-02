"""
🌎 BioGuard — FIAP Global Solution 2026
Monitoramento Inteligente de Queimadas e Impacto na Fauna Brasileira

Este aplicativo utiliza:
- 🔥 Dados do INPE BDQueimadas
- 🐾 Base local da IUCN Red List
- 🗺️ Mapas interativos
- 📊 Dashboards analíticos
- 🧠 Índice de vulnerabilidade ambiental
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster, Fullscreen, MiniMap
from sklearn.cluster import KMeans
import warnings
import textwrap

warnings.filterwarnings("ignore")

# ============================================================
# 🎨 CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="BioGuard - Monitoramento de Queimadas",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 🎨 ESTILO PERSONALIZADO
# ============================================================
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 📦 CARREGAMENTO DE DADOS
# ============================================================
@st.cache_data
def load_data(arquivo):
    """Carrega e padroniza os dados do INPE"""
    try:
        df = pd.read_csv(arquivo)
        df.columns = df.columns.str.lower().str.strip()
        
        # Renomear colunas de coordenadas
        rename_map = {}
        if "latitude" in df.columns:
            rename_map["latitude"] = "lat"
        if "longitude" in df.columns:
            rename_map["longitude"] = "lon"
        
        df = df.rename(columns=rename_map)
        df = df.dropna(subset=["lat", "lon"])
        
        return df
    except FileNotFoundError:
        return None

@st.cache_data
def get_species_data_with_coordinates():
    """Retorna lista de espécies com coordenadas"""
    return [
        # --- AMAZÔNIA ---
        {"nome": "🐬 Boto-cor-de-rosa", "lat": -3.0, "lon": -60.0, "bioma": "Amazônia", "risco": "Alto"},
        {"nome": "🦅 Gavião-real", "lat": -2.5, "lon": -59.5, "bioma": "Amazônia", "risco": "Crítico"},
        {"nome": "🐠 Pirarucu", "lat": -4.0, "lon": -61.0, "bioma": "Amazônia", "risco": "Moderado"},
        {"nome": "🦜 Arara-azul-grande", "lat": -5.0, "lon": -62.0, "bioma": "Amazônia", "risco": "Alto"},
        {"nome": "🐆 Onça-negra", "lat": -3.5, "lon": -58.5, "bioma": "Amazônia", "risco": "Crítico"},
        {"nome": "🦥 Preguiça-de-três-dedos", "lat": -2.0, "lon": -59.0, "bioma": "Amazônia", "risco": "Moderado"},
        {"nome": "🐒 Macaco-aranha", "lat": -1.5, "lon": -57.5, "bioma": "Amazônia", "risco": "Alto"},
        {"nome": "🦙 Lhama-guanaco", "lat": -6.0, "lon": -63.0, "bioma": "Amazônia", "risco": "Baixo"},
        {"nome": "🐍 Sucuri", "lat": -4.5, "lon": -60.5, "bioma": "Amazônia", "risco": "Moderado"},
        {"nome": "🦆 Pato-do-mato", "lat": -3.2, "lon": -61.5, "bioma": "Amazônia", "risco": "Baixo"},
        
        # --- CERRADO ---
        {"nome": "🦁 Lobo-guará", "lat": -15.5, "lon": -48.0, "bioma": "Cerrado", "risco": "Alto"},
        {"nome": "🦌 Veado-campeiro", "lat": -14.0, "lon": -47.5, "bioma": "Cerrado", "risco": "Crítico"},
        {"nome": "🦜 Arara-azul-pequena", "lat": -13.5, "lon": -46.5, "bioma": "Cerrado", "risco": "Moderado"},
        {"nome": "🐆 Gato-do-mato", "lat": -16.0, "lon": -49.0, "bioma": "Cerrado", "risco": "Alto"},
        {"nome": "🦅 Gavião-real", "lat": -14.5, "lon": -48.5, "bioma": "Cerrado", "risco": "Crítico"},
        
        # --- PANTANAL ---
        {"nome": "🐾 Onça-pintada", "lat": -16.5, "lon": -56.5, "bioma": "Pantanal", "risco": "Alto"},
        {"nome": "🦜 Arara-azul", "lat": -17.0, "lon": -57.0, "bioma": "Pantanal", "risco": "Crítico"},
        {"nome": "🦘 Anta", "lat": -16.0, "lon": -56.0, "bioma": "Pantanal", "risco": "Moderado"},
        {"nome": "🐆 Jaguatirica", "lat": -17.5, "lon": -57.5, "bioma": "Pantanal", "risco": "Alto"},
        {"nome": "🐢 Jacaré-do-pantanal", "lat": -16.2, "lon": -56.2, "bioma": "Pantanal", "risco": "Crítico"},
        
        # --- MATA ATLÂNTICA ---
        {"nome": "🐒 Mico-leão-dourado", "lat": -22.5, "lon": -42.5, "bioma": "Mata Atlântica", "risco": "Crítico"},
        {"nome": "🐒 Muriqui-do-sul", "lat": -23.0, "lon": -43.0, "bioma": "Mata Atlântica", "risco": "Crítico"},
        {"nome": "🦜 Papagaio-de-peito-roxo", "lat": -24.0, "lon": -44.0, "bioma": "Mata Atlântica", "risco": "Alto"},
        {"nome": "🦥 Preguiça-de-coleira", "lat": -22.0, "lon": -42.0, "bioma": "Mata Atlântica", "risco": "Moderado"},
        {"nome": "🐆 Gato-do-mato", "lat": -23.5, "lon": -43.5, "bioma": "Mata Atlântica", "risco": "Alto"},
        {"nome": "🐸 Sapo-cururu", "lat": -22.0, "lon": -43.0, "bioma": "Mata Atlântica", "risco": "Baixo"},
        {"nome": "🐒 Bugio-ruivo", "lat": -21.0, "lon": -41.5, "bioma": "Mata Atlântica", "risco": "Crítico"},
        {"nome": "🦜 Papagaio-de-peito-roxo", "lat": -26.0, "lon": -48.5, "bioma": "Mata Atlântica", "risco": "Crítico"},
        {"nome": "🦥 Preguiça-de-coleira", "lat": -24.5, "lon": -47.0, "bioma": "Mata Atlântica", "risco": "Moderado"},
        {"nome": "🐸 Perereca-de-folhagem", "lat": -23.0, "lon": -44.0, "bioma": "Mata Atlântica", "risco": "Baixo"},
        
        # --- CAATINGA ---
        {"nome": "🐕 Raposa-do-campo", "lat": -9.5, "lon": -40.5, "bioma": "Caatinga", "risco": "Moderado"},
        {"nome": "🐍 Cascavel", "lat": -8.0, "lon": -39.0, "bioma": "Caatinga", "risco": "Baixo"},
        {"nome": "🦜 Ararinha-azul", "lat": -9.0, "lon": -42.5, "bioma": "Caatinga", "risco": "Crítico"},
        {"nome": "🐍 Jararaca", "lat": -7.5, "lon": -37.5, "bioma": "Caatinga", "risco": "Alto"},
        {"nome": "🦎 Calango", "lat": -8.8, "lon": -41.0, "bioma": "Caatinga", "risco": "Baixo"},
        {"nome": "🐗 Porco-do-mato", "lat": -10.5, "lon": -38.5, "bioma": "Caatinga", "risco": "Moderado"},
        {"nome": "🐦 Asa-branca", "lat": -6.2, "lon": -36.0, "bioma": "Caatinga", "risco": "Alto"},
        
        # --- PAMPA ---
        {"nome": "🦌 Veado-campeiro", "lat": -31.5, "lon": -53.5, "bioma": "Pampa", "risco": "Alto"},
        {"nome": "🐈 Gato-palheiro", "lat": -30.0, "lon": -54.0, "bioma": "Pampa", "risco": "Moderado"},
        {"nome": "🦆 Pato-mergulhão", "lat": -30.5, "lon": -52.5, "bioma": "Pampa", "risco": "Crítico"},
        {"nome": "🐾 Gato-dos-pampas", "lat": -32.0, "lon": -55.5, "bioma": "Pampa", "risco": "Alto"},
        {"nome": "🦌 Veado-virá", "lat": -29.5, "lon": -56.0, "bioma": "Pampa", "risco": "Moderado"},
        {"nome": "🐍 Boipeva", "lat": -31.8, "lon": -53.2, "bioma": "Pampa", "risco": "Baixo"},
    ]

@st.cache_data
def get_species_data():
    """Retorna base de espécies ameaçadas por bioma (para gráficos)"""
    dados_especies = [
        # 🌿 PANTANAL
        {"especie": "Panthera onca", "nome_comum": "Onça-pintada", "bioma": "Pantanal", "categoria_iucn": "NT"},
        {"especie": "Anodorhynchus hyacinthinus", "nome_comum": "Arara-azul", "bioma": "Pantanal", "categoria_iucn": "VU"},
        {"especie": "Myrmecophaga tridactyla", "nome_comum": "Tamanduá-bandeira", "bioma": "Pantanal", "categoria_iucn": "VU"},
        {"especie": "Chrysocyon brachyurus", "nome_comum": "Lobo-guará", "bioma": "Pantanal", "categoria_iucn": "NT"},
        {"especie": "Caiman yacare", "nome_comum": "Jacaré-do-pantanal", "bioma": "Pantanal", "categoria_iucn": "LC"},
        {"especie": "Jabiru mycteria", "nome_comum": "Tuiuiú", "bioma": "Pantanal", "categoria_iucn": "LC"},
        {"especie": "Hydrochoerus hydrochaeris", "nome_comum": "Capivara", "bioma": "Pantanal", "categoria_iucn": "LC"},
        {"especie": "Tapirus terrestris", "nome_comum": "Anta", "bioma": "Pantanal", "categoria_iucn": "VU"},
        {"especie": "Pteronura brasiliensis", "nome_comum": "Ariranha", "bioma": "Pantanal", "categoria_iucn": "EN"},
        {"especie": "Leopardus pardalis", "nome_comum": "Jaguatirica", "bioma": "Pantanal", "categoria_iucn": "LC"},
        
        # 🌳 AMAZÔNIA
        {"especie": "Saguinus bicolor", "nome_comum": "Sauim-de-coleira", "bioma": "Amazônia", "categoria_iucn": "CR"},
        {"especie": "Ateles paniscus", "nome_comum": "Macaco-aranha", "bioma": "Amazônia", "categoria_iucn": "VU"},
        {"especie": "Cacajao calvus", "nome_comum": "Uacari-branco", "bioma": "Amazônia", "categoria_iucn": "VU"},
        {"especie": "Inia geoffrensis", "nome_comum": "Boto-cor-de-rosa", "bioma": "Amazônia", "categoria_iucn": "EN"},
        {"especie": "Pteronura brasiliensis", "nome_comum": "Ariranha", "bioma": "Amazônia", "categoria_iucn": "EN"},
        {"especie": "Harpia harpyja", "nome_comum": "Gavião-real", "bioma": "Amazônia", "categoria_iucn": "NT"},
        {"especie": "Podocnemis expansa", "nome_comum": "Tartaruga-da-amazônia", "bioma": "Amazônia", "categoria_iucn": "VU"},
        {"especie": "Alouatta seniculus", "nome_comum": "Guariba-vermelho", "bioma": "Amazônia", "categoria_iucn": "LC"},
        {"especie": "Cebus albifrons", "nome_comum": "Macaco-prego", "bioma": "Amazônia", "categoria_iucn": "LC"},
        {"especie": "Arapaima gigas", "nome_comum": "Pirarucu", "bioma": "Amazônia", "categoria_iucn": "EN"},
        
        # 🌾 CERRADO
        {"especie": "Chrysocyon brachyurus", "nome_comum": "Lobo-guará", "bioma": "Cerrado", "categoria_iucn": "NT"},
        {"especie": "Pseudalopex vetulus", "nome_comum": "Raposa-do-campo", "bioma": "Cerrado", "categoria_iucn": "NT"},
        {"especie": "Ozotoceros bezoarticus", "nome_comum": "Veado-campeiro", "bioma": "Cerrado", "categoria_iucn": "VU"},
        {"especie": "Leopardus tigrinus", "nome_comum": "Gato-do-mato-pequeno", "bioma": "Cerrado", "categoria_iucn": "VU"},
        {"especie": "Rhea americana", "nome_comum": "Ema", "bioma": "Cerrado", "categoria_iucn": "LC"},
        
        # 🌴 MATA ATLÂNTICA
        {"especie": "Leontopithecus rosalia", "nome_comum": "Mico-leão-dourado", "bioma": "Mata Atlântica", "categoria_iucn": "EN"},
        {"especie": "Brachyteles arachnoides", "nome_comum": "Muriqui-do-sul", "bioma": "Mata Atlântica", "categoria_iucn": "CR"},
        {"especie": "Procnias nudicollis", "nome_comum": "Araponga", "bioma": "Mata Atlântica", "categoria_iucn": "VU"},
        {"especie": "Leopardus tigrinus", "nome_comum": "Gato-do-mato", "bioma": "Mata Atlântica", "categoria_iucn": "VU"},
        {"especie": "Trichechus manatus", "nome_comum": "Peixe-boi-marinho", "bioma": "Mata Atlântica", "categoria_iucn": "VU"},
        
        # 🌵 CAATINGA
        {"especie": "Callithrix jacchus", "nome_comum": "Sagui-do-nordeste", "bioma": "Caatinga", "categoria_iucn": "LC"},
        {"especie": "Pseudalopex vetulus", "nome_comum": "Raposa-do-campo", "bioma": "Caatinga", "categoria_iucn": "NT"},
        {"especie": "Leopardus tigrinus", "nome_comum": "Gato-do-mato", "bioma": "Caatinga", "categoria_iucn": "VU"},
        
        # 🌾 PAMPA
        {"especie": "Ozotoceros bezoarticus", "nome_comum": "Veado-campeiro", "bioma": "Pampa", "categoria_iucn": "VU"},
        {"especie": "Rhea pennata", "nome_comum": "Ema-do-pampa", "bioma": "Pampa", "categoria_iucn": "NT"},
    ]
    
    df_especies = pd.DataFrame(dados_especies)
    return df_especies

# ============================================================
# 🧠 CÁLCULO DE RISCO
# ============================================================
def calculate_risk_index(df, df_especies):
    """Calcula índice de vulnerabilidade ambiental"""
    PESO_IUCN = {
        "CR": 5,  # Criticamente em Perigo
        "EN": 4,  # Em Perigo
        "VU": 3,  # Vulnerável
        "NT": 2,  # Quase Ameaçado
        "LC": 1   # Pouco Preocupante
    }
    
    df_especies["peso_risco"] = df_especies["categoria_iucn"].map(PESO_IUCN)
    
    qtd_queimadas = len(df)
    media_risco = df_especies["peso_risco"].mean()
    indice_vulnerabilidade = qtd_queimadas * media_risco
    
    # Classificar nível de risco
    if indice_vulnerabilidade > 500000:
        nivel = "🔴 CRÍTICO"
    elif indice_vulnerabilidade > 250000:
        nivel = "🟠 ALTO"
    elif indice_vulnerabilidade > 100000:
        nivel = "🟡 MÉDIO"
    else:
        nivel = "🟢 BAIXO"
    
    return {
        "queimadas": qtd_queimadas,
        "media_risco": media_risco,
        "indice": indice_vulnerabilidade,
        "nivel": nivel
    }

# ============================================================
# 🗺️ CRIAR MAPA INTERATIVO (DO NOTEBOOK)
# ============================================================
@st.cache_data
def create_map_from_notebook(df):
    
    # Detectar colunas
    col_lat = None
    col_lon = None
    for col in df.columns:
        if "lat" in col.lower():
            col_lat = col
        if "lon" in col.lower() or "long" in col.lower():
            col_lon = col
    
    if col_lat is None or col_lon is None:
        return None
    
    # Limpar dados
    mapa_df = df.dropna(subset=[col_lat, col_lon])
    
    # Mapa base
    mapa = folium.Map(
        location=[-14, -55],
        zoom_start=4,
        tiles="CartoDB positron"
    )
    
    # Controles
    Fullscreen().add_to(mapa)
    MiniMap(toggle_display=True).add_to(mapa)
    
    # Heatmap de queimadas
    heat_data = mapa_df[[col_lat, col_lon]].values.tolist()
    HeatMap(
        heat_data,
        radius=18,
        blur=12,
        min_opacity=0.4,
        max_zoom=8
    ).add_to(mapa)
    
    # Cluster de marcadores
    marker_cluster = MarkerCluster().add_to(mapa)
    
    # Cores de risco
    cores_risco = {
        "Baixo": "green",
        "Moderado": "orange",
        "Alto": "red",
        "Crítico": "darkred"
    }
    
    # Adicionar espécies
    especies = get_species_data_with_coordinates()
    for especie in especies:
        popup_html = f"""
        <div style="width:200px">
        <h4>{especie['nome']}</h4>
        <b>🌱 Bioma:</b> {especie['bioma']}<br>
        <b>⚠️ Risco:</b> {especie['risco']}<br>
        </div>
        """
        folium.CircleMarker(
            location=[especie["lat"], especie["lon"]],
            radius=12,
            popup=popup_html,
            color=cores_risco[especie["risco"]],
            fill=True,
            fill_color=cores_risco[especie["risco"]],
            fill_opacity=0.9
        ).add_to(marker_cluster)
    
    # Legenda
    legenda = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 230px;
        height: 240px;
        background-color: #A9A9A9;
        border:2px solid grey;
        z-index:9999;
        font-size:14px;
        padding: 10px;
        border-radius:10px;
        font-weight: bold;
    ">
    <h4>🌎 BioGuard</h4>
    <b>🔥 Heatmap</b><br>
    Intensidade de queimadas<br><br>
    <b>🐾 Espécies</b><br>
    🟢 Baixo<br>
    🟠 Moderado<br>
    🔴 Alto<br>
    ⚫ Crítico
    </div>
    """
    mapa.get_root().html.add_child(
        folium.Element(legenda)
    )
    
    return mapa

# ============================================================
# 🎯 INTERFACE PRINCIPAL
# ============================================================

# Header
col_header1, col_header2 = st.columns([1, 4])
with col_header1:
    try:
        st.image("logo.png", width=150)
    except Exception:
        pass
with col_header2:
    st.markdown("# BioGuard - Monitoramento de Queimadas")
    st.markdown("### FIAP Global Solution 2026 - Impacto na Fauna Brasileira")

# Sidebar para configurações
try:
    st.sidebar.image("logo.png", use_container_width=True)
except Exception:
    pass
st.sidebar.markdown("## ⚙️ Configurações")
arquivo_dados = st.sidebar.text_input(
    "📁 Caminho do arquivo CSV:",
    value="bdqueimadas.csv",
    help="Insira o caminho do arquivo de dados do INPE"
)

# Carregar dados
df = load_data(arquivo_dados)
df_especies = get_species_data()

if df is None:
    st.error(f"❌ Arquivo '{arquivo_dados}' não encontrado. Verifique o caminho.")
    st.info("💡 Certifique-se de que o arquivo CSV está no diretório correto.")
else:
    # Detectar colunas
    col_lat = None
    col_lon = None
    col_bioma = None
    
    for col in df.columns:
        if "lat" in col.lower():
            col_lat = col
        if "lon" in col.lower() or "long" in col.lower():
            col_lon = col
        if "bioma" in col.lower():
            col_bioma = col
    
    # ============================================================
    # 📊 MÉTRICAS PRINCIPAIS
    # ============================================================
    st.markdown("## 📊 Métricas Principais")
    
    risk_data = calculate_risk_index(df, df_especies)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🔥 Queimadas Detectadas",
            f"{risk_data['queimadas']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            "🐾 Espécies Monitoradas",
            len(df_especies),
            delta=None
        )
    
    with col3:
        st.metric(
            "⚠️ Risco Médio",
            f"{risk_data['media_risco']:.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            "🚨 Nível de Risco",
            risk_data['nivel'],
            delta=None
        )
    
    # ============================================================
    # 🗺️ MAPA INTERATIVO
    # ============================================================
    st.markdown("## 🗺️ Mapa Interativo de Queimadas e Espécies")
    
    if col_lat and col_lon:
        with st.spinner("🔄 Gerando mapa..."):
            mapa = create_map_from_notebook(df)
            if mapa:
                # Usar key para evitar recarregamento
                st_folium(mapa, width=1400, height=600, key="fire_map")
            else:
                st.warning("⚠️ Não foi possível gerar o mapa.")
    else:
        st.warning("⚠️ Colunas de latitude/longitude não encontradas.")
    
    # ============================================================
    # 📈 GRÁFICOS ANALÍTICOS
    # ============================================================
    st.markdown("## 📈 Análises Detalhadas")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔥 Queimadas por Bioma",
        "🐾 Espécies Ameaçadas",
        "📊 Categorias IUCN",
        "🎯 Dados Brutos"
    ])
    
    # Tab 1: Queimadas por Bioma
    with tab1:
        if col_bioma:
            fig_bioma = px.histogram(
                df,
                x=col_bioma,
                color=col_bioma,
                title="🔥 Distribuição de Queimadas por Bioma",
                labels={col_bioma: "Bioma", "count": "Quantidade"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_bioma.update_layout(
                height=500, 
                showlegend=False,
                xaxis_title="Bioma",
                yaxis_title="Quantidade de Queimadas"
            )
            st.plotly_chart(fig_bioma, use_container_width=True)
            
            # Estatísticas por bioma
            st.subheader("📋 Estatísticas por Bioma")
            bioma_stats = df[col_bioma].value_counts().reset_index()
            bioma_stats.columns = ["Bioma", "Queimadas"]
            bioma_stats["Percentual"] = (bioma_stats["Queimadas"] / bioma_stats["Queimadas"].sum() * 100).round(2)
            st.dataframe(bioma_stats, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Coluna de bioma não encontrada nos dados.")
    
    # Tab 2: Espécies Ameaçadas
    with tab2:
        fig_especies = px.bar(
            df_especies.groupby("bioma").size().reset_index(name="quantidade"),
            x="bioma",
            y="quantidade",
            color="bioma",
            title="🐾 Espécies Monitoradas por Bioma",
            labels={"bioma": "Bioma", "quantidade": "Quantidade de Espécies"},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_especies.update_layout(
            height=500, 
            showlegend=False,
            xaxis_title="Bioma",
            yaxis_title="Quantidade de Espécies"
        )
        st.plotly_chart(fig_especies, use_container_width=True)
        
        # Lista de espécies
        st.subheader("📝 Espécies Monitoradas")
        bioma_selecionado = st.selectbox(
            "Selecione um bioma:",
            df_especies["bioma"].unique(),
            key="bioma_select"
        )
        
        especies_filtradas = df_especies[df_especies["bioma"] == bioma_selecionado]
        st.dataframe(
            especies_filtradas[["nome_comum", "especie", "categoria_iucn"]],
            use_container_width=True,
            hide_index=True
        )
    
    # Tab 3: Categorias IUCN
    with tab3:
        iucn_counts = df_especies["categoria_iucn"].value_counts()
        
        fig_iucn = px.pie(
            values=iucn_counts.values,
            names=iucn_counts.index,
            title="🐾 Distribuição das Categorias IUCN",
            color_discrete_map={
                "CR": "#8B0000",  # Vermelho escuro
                "EN": "#FF0000",  # Vermelho
                "VU": "#FFA500",  # Laranja
                "NT": "#FFD700",  # Ouro
                "LC": "#90EE90"   # Verde claro
            }
        )
        fig_iucn.update_layout(height=500)
        st.plotly_chart(fig_iucn, use_container_width=True)
        
        # Legenda IUCN
        st.subheader("📖 Categorias IUCN")
        iucn_info = {
            "CR": "Criticamente em Perigo",
            "EN": "Em Perigo",
            "VU": "Vulnerável",
            "NT": "Quase Ameaçado",
            "LC": "Pouco Preocupante"
        }
        
        col_leg1, col_leg2 = st.columns(2)
        for i, (sigla, descricao) in enumerate(iucn_info.items()):
            if i < 3:
                with col_leg1:
                    st.write(f"**{sigla}** - {descricao}")
            else:
                with col_leg2:
                    st.write(f"**{sigla}** - {descricao}")
    
    # Tab 4: Dados Brutos
    with tab4:
        st.subheader("📊 Dados de Queimadas")
        
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            if col_bioma:
                biomas_selecionados = st.multiselect(
                    "Filtrar por Bioma:",
                    df[col_bioma].unique(),
                    default=list(df[col_bioma].unique())[:3],
                    key="bioma_filter"
                )
                df_filtrado = df[df[col_bioma].isin(biomas_selecionados)]
            else:
                df_filtrado = df
        
        with col_filtro2:
            linhas = st.slider("Quantidade de linhas:", 10, 500, 100, key="linhas_slider")
        
        st.dataframe(
            df_filtrado.head(linhas),
            use_container_width=True,
            height=400
        )
        
        # Download dos dados
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="📥 Baixar dados filtrados (CSV)",
            data=csv,
            file_name="bioguard_dados_filtrados.csv",
            mime="text/csv",
            key="download_filtrado"
        )
    
    # ============================================================
    # 📄 RELATÓRIO AMBIENTAL
    # ============================================================
    st.markdown("## 📄 Relatório Ambiental Automático")

    relatorio = textwrap.dedent(f"""
    ### 🌎 Relatório Ambiental — BioGuard
    
    #### 🔥 Queimadas Monitoradas
    **{risk_data['queimadas']:,}** focos de incêndio foram detectados na região monitorada.
    
    #### ⚠️ Nível de Risco Ambiental
    **{risk_data['nivel']}**
    
    Índice de Vulnerabilidade: **{risk_data['indice']:,.0f}**
    
    #### 🐾 Espécies Ameaçadas Monitoradas
    - Total de espécies: **{len(df_especies)}**
    - Criticamente em Perigo (CR): **{len(df_especies[df_especies['categoria_iucn'] == 'CR'])}**
    - Em Perigo (EN): **{len(df_especies[df_especies['categoria_iucn'] == 'EN'])}**
    - Vulnerável (VU): **{len(df_especies[df_especies['categoria_iucn'] == 'VU'])}**
    
    #### 📊 Distribuição por Bioma
    """).strip()

    if col_bioma:
        bioma_counts = df[col_bioma].value_counts()
    for bioma, count in bioma_counts.items():
        relatorio += f"\n- **{bioma}**: {count:,} queimadas"

    relatorio += textwrap.dedent(f"""
    
    #### 🌱 Conclusão
    O BioGuard utiliza dados espaciais do INPE e informações da IUCN Red List para 
    monitorar o impacto de queimadas na fauna brasileira. Este sistema fornece 
    informações críticas para tomadores de decisão e pesquisadores ambientais.
    
    ---
    *Relatório gerado automaticamente pelo BioGuard*
""")

    st.markdown(relatorio)
    
    # ============================================================
    # 💾 EXPORTAÇÃO
    # ============================================================
    st.markdown("## 💾 Exportar Resultados")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        csv_queimadas = df.to_csv(index=False)
        st.download_button(
            label="📥 Dados de Queimadas (CSV)",
            data=csv_queimadas,
            file_name="bioguard_queimadas.csv",
            mime="text/csv",
            key="download_queimadas"
        )
    
    with col_exp2:
        csv_especies = df_especies.to_csv(index=False)
        st.download_button(
            label="📥 Espécies Monitoradas (CSV)",
            data=csv_especies,
            file_name="bioguard_especies.csv",
            mime="text/csv",
            key="download_especies"
        )

# ============================================================
# 📝 RODAPÉ
# ============================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
    <p>🌎 <b>BioGuard</b> — FIAP Global Solution 2026</p>
    <p>Monitoramento Inteligente de Queimadas e Impacto na Fauna Brasileira</p>
    <p style='font-size: 0.8em; color: gray;'>
    Dados: INPE BDQueimadas | Espécies: IUCN Red List
    </p>
    </div>
""", unsafe_allow_html=True)
