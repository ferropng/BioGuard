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
from folium.plugins import HeatMap, MarkerCluster
from sklearn.cluster import KMeans
import warnings

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
def get_species_data():
    """Retorna base de espécies ameaçadas por bioma"""
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
# 🗺️ CRIAR MAPA INTERATIVO (OTIMIZADO)
# ============================================================
@st.cache_data
def create_fire_map(df, col_lat="lat", col_lon="lon", max_markers=500):
    """Cria mapa interativo de queimadas com heatmap - OTIMIZADO"""
    
    if col_lat not in df.columns or col_lon not in df.columns:
        return None
    
    # Centro do mapa (Brasil)
    centro_lat = df[col_lat].mean()
    centro_lon = df[col_lon].mean()
    
    m = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=4,
        tiles="OpenStreetMap"
    )
    
    # Adicionar HeatMap com todos os dados
    heat_data = [[row[col_lat], row[col_lon]] for idx, row in df.iterrows()]
    HeatMap(
        heat_data, 
        radius=20, 
        blur=25, 
        max_zoom=13,
        gradient={0.2: 'blue', 0.4: 'green', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
    ).add_to(m)
    
    # Adicionar cluster de marcadores (limitado para performance)
    marker_cluster = MarkerCluster(name="Focos de Incêndio").add_to(m)
    
    # Usar sampling para grandes datasets
    df_sample = df.sample(min(max_markers, len(df)), random_state=42)
    
    for idx, row in df_sample.iterrows():
        risco = row.get('riscofogo', 0)
        
        # Cor baseada no risco
        if risco > 0.7:
            color = "red"
            fillColor = "darkred"
        elif risco > 0.4:
            color = "orange"
            fillColor = "orange"
        else:
            color = "yellow"
            fillColor = "yellow"
        
        folium.CircleMarker(
            location=[row[col_lat], row[col_lon]],
            radius=4,
            popup=f"""
                <b>Bioma:</b> {row.get('bioma', 'N/A')}<br>
                <b>Estado:</b> {row.get('estado', 'N/A')}<br>
                <b>Risco:</b> {risco:.2f}<br>
                <b>Satélite:</b> {row.get('satelite', 'N/A')}
            """,
            color=color,
            fill=True,
            fillColor=fillColor,
            fillOpacity=0.7,
            weight=1
        ).add_to(marker_cluster)
    
    # Adicionar controle de camadas
    folium.LayerControl().add_to(m)
    
    return m

# ============================================================
# 🎯 INTERFACE PRINCIPAL
# ============================================================

# Header
st.markdown("# 🌎 BioGuard - Monitoramento de Queimadas")
st.markdown("### FIAP Global Solution 2026 - Impacto na Fauna Brasileira")

# Sidebar para configurações
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
    # 🗺️ MAPA INTERATIVO (SEM RECARREGAMENTO)
    # ============================================================
    st.markdown("## 🗺️ Mapa Interativo de Queimadas")
    
    if col_lat and col_lon:
        with st.spinner("🔄 Gerando mapa..."):
            mapa = create_fire_map(df, col_lat, col_lon, max_markers=500)
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
    
    relatorio = f"""
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
    """
    
    if col_bioma:
        bioma_counts = df[col_bioma].value_counts()
        for bioma, count in bioma_counts.items():
            relatorio += f"\n- **{bioma}**: {count:,} queimadas"
    
    relatorio += """
    
    #### 🌱 Conclusão
    O BioGuard utiliza dados espaciais do INPE e informações da IUCN Red List para 
    monitorar o impacto de queimadas na fauna brasileira. Este sistema fornece 
    informações críticas para tomadores de decisão e pesquisadores ambientais.
    
    ---
    *Relatório gerado automaticamente pelo BioGuard*
    """
    
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
