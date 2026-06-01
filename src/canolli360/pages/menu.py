import etl
import pandas as pd
import streamlit as st

# Navegação customizada (mantém identidade visual da sidebar).
PAGINAS = {
    "Visão geral": "app.py",
    "Indicadores": "pages/indicadores.py",
    "RFM & retenção": "pages/fidelizacao.py",
    "Campanhas": "pages/campanhas.py",
}


def _opcoes_filtro(df: pd.DataFrame, coluna: str) -> tuple[list[str], dict]:
    """Lista de opções + mapa para filtro; retorna só 'Todos' se a coluna não existir."""
    if coluna not in df.columns:
        return ["Todos"], {}
    valores = df[coluna].dropna().astype(str).unique().tolist()
    lista = ["Todos"] + sorted(valores)
    mapa = dict(zip(valores, valores))
    return lista, mapa


def render_header(store, storeorder):
    
    # organizando infos de período
    datas = pd.to_datetime(storeorder['createdat'], format='mixed', utc=True).dt.tz_localize(None).dt.to_period('M')
    lista_periodo = ["Todos"] + sorted(
        datas.astype(str).unique().tolist(), 
        reverse=True
    )
    
    # organizando infos de loja
    lista_lojas = store["name"].dropna().unique().tolist()
    lista_lojas.insert(0, "Todas")
    map_store = dict(zip(store['name'], store['id']))

    # organizando infos de canal e tipo de pedido (colunas opcionais no ETL)
    lista_canal, map_canal = _opcoes_filtro(storeorder, "saleschannel")
    lista_pedido, map_pedido = _opcoes_filtro(storeorder, "ordertype")
    tem_filtro_pedido = "ordertype" in storeorder.columns and len(lista_pedido) > 1

    # estilização do header
    with st.container():
        st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)
        st.markdown('<div class="header">', unsafe_allow_html=True)
        col1,col2,col3,col4,col5 = st.columns([2,2,2,2,2])
        
        # titulo
        with col1:
            st.markdown("### Cannoli Food Tech")

        # filtro de período
        with col2:
            if "periodo" not in st.session_state or st.session_state.periodo not in lista_periodo:
                st.session_state.periodo = "Todos os períodos"

            periodo = st.selectbox(
                "Período",
                lista_periodo,
                key="periodo"
            )

        # filtro de loja
        with col3:
            if "restaurante" not in st.session_state:
                st.session_state.restaurante = "Todas as lojas"

            restaurante = st.selectbox(
                "Loja",
                lista_lojas,
                key="restaurante"
            )

            if restaurante != "Todas":
                store_id = map_store[restaurante]
                df_loja = storeorder[storeorder['storeid'] == store_id]
            else:
                df_loja = storeorder.copy()

        # filtro de canal
        with col4:
            if "canal" not in st.session_state:
                st.session_state.canal = "Todos os canais"

            canal = st.selectbox(
                "Canal de Venda",
                lista_canal,
                key="canal"
            )

            if canal != "Todos" and "saleschannel" in df_loja.columns:
                df_loja = df_loja[df_loja["saleschannel"].astype(str) == map_canal[canal]]
        
        # filtro de pedido (somente se a coluna existir na base)
        with col5:
            if tem_filtro_pedido:
                if "pedido" not in st.session_state or st.session_state.pedido not in lista_pedido:
                    st.session_state.pedido = "Todos"

                pedido = st.selectbox(
                    "Tipo de pedido",
                    lista_pedido,
                    key="pedido",
                )

                if pedido != "Todos":
                    df_loja = df_loja[df_loja["ordertype"].astype(str) == map_pedido[pedido]]
            else:
                pedido = "Todos"
                st.selectbox("Tipo de pedido", ["Todos"], key="pedido", disabled=True)

        if periodo != "Todos":
            periodo_selecionado = pd.Period(periodo, freq='M')
            df_loja = df_loja[
                pd.to_datetime(df_loja['createdat'], format='mixed', utc=True).dt.tz_localize(None).dt.to_period('M') == periodo_selecionado
            ]
        
        st.markdown('</div>', unsafe_allow_html=True)

    # devolve as infos entregues pelas funções
    return periodo, restaurante, canal, pedido, df_loja


def render_header_campanhas(store, campaignxorder):
    """Header simplificado para a página de Campanhas.

    Expõe apenas os filtros relevantes para CAMPAIGNXORDER:
    período (baseado em sent_at) e loja. Canal e tipo de pedido
    não se aplicam a campanhas e ficam fora desta tela.
    Retorna (periodo, restaurante) no mesmo formato que render_header.
    """

    # organizando infos de período a partir de sent_at
    datas = pd.to_datetime(campaignxorder["sent_at"], errors="coerce").dt.to_period("M")
    lista_periodo = ["Todos"] + sorted(
        datas.dropna().astype(str).unique().tolist(),
        reverse=True,
    )

    # organizando infos de loja
    lista_lojas = store["name"].dropna().unique().tolist()
    lista_lojas.insert(0, "Todas")

    with st.container():
        st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)
        st.markdown('<div class="header">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            st.markdown("### Cannoli Food Tech")

        with col2:
            if "periodo_camp" not in st.session_state or st.session_state.periodo_camp not in lista_periodo:
                st.session_state.periodo_camp = lista_periodo[0]

            periodo = st.selectbox(
                "Período",
                lista_periodo,
                key="periodo_camp",
            )

        with col3:
            if "restaurante_camp" not in st.session_state:
                st.session_state.restaurante_camp = "Todas"

            restaurante = st.selectbox(
                "Loja",
                lista_lojas,
                key="restaurante_camp",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    return periodo, restaurante


def render_sidebar():
    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "Visão geral"

    st.sidebar.markdown(
        """
    <style>
        section[data-testid="stSidebar"] > div {
            background-color: #0d1440;
            padding: 20px;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        section[data-testid="stSidebar"] .sidebar-rodape-fixo {
            margin-top: auto;
            padding-top: 1.25rem;
            border-top: 1px solid rgba(255, 255, 255, 0.12);
        }

        section[data-testid="stSidebar"] .sidebar-rodape-fixo p {
            color: rgba(255, 255, 255, 0.7) !important;
            font-size: 0.78rem !important;
            margin: 0.15rem 0 !important;
        }

        /* Botões da sidebar — altura fixa (evita “CARREGAR” gigante) */
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            height: 3.25rem !important;
            min-height: 3.25rem !important;
            max-height: 3.5rem !important;
            border-radius: 10px;
            margin-bottom: 10px;
            font-size: 0.9rem !important;
            line-height: 1.2 !important;
            padding: 0.5rem 0.75rem !important;
            transition: all 0.2s ease;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background-color: #ff7a00;
            color: white;
            border: 1px solid #ff7a00;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background-color: transparent;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
            background-color: #1a2557;
        }

        section[data-testid="stSidebar"] .bloco-upload-dados {
            margin-top: 0.5rem;
            margin-bottom: 0.35rem;
        }

        section[data-testid="stSidebar"] .bloco-upload-dados h3 {
            color: #ffffff;
            font-size: 1rem;
            margin: 0 0 0.35rem 0;
            font-weight: 600;
        }

        section[data-testid="stSidebar"] .bloco-upload-dados p {
            color: #ffffff;
            font-size: 0.88rem;
            margin: 0 0 0.25rem 0;
            line-height: 1.35;
        }

        section[data-testid="stSidebar"] .bloco-upload-dados .fmt-tipos {
            color: rgba(255, 255, 255, 0.75) !important;
            font-size: 0.8rem !important;
            margin: 0 0 0.5rem 0 !important;
        }

        /* Área de upload mais leve — sem botão “Carregar” duplicado */
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
            margin-bottom: 0.35rem;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            min-height: 5.5rem !important;
            padding: 0.65rem 0.75rem !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            display: none !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div {
            font-size: 0.8rem !important;
            line-height: 1.35 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
            display: none !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
            margin-bottom: 0.2rem !important;
        }

        /* Upload · Limpar · Demonstração — mesma altura e alinhamento */
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ~ div [data-testid="stHorizontalBlock"] {
            align-items: stretch !important;
            gap: 0.5rem !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ~ div [data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            min-width: 0 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ~ div [data-testid="column"] .stButton {
            width: 100% !important;
            margin: 0 !important;
            padding-top: 0 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ~ div .stButton > button {
            width: 100% !important;
            height: 2.5rem !important;
            min-height: 2.5rem !important;
            max-height: 2.5rem !important;
            margin: 0 0 0.4rem 0 !important;
            padding: 0 0.5rem !important;
            font-size: 0.82rem !important;
            line-height: 1.2 !important;
            border-radius: 8px !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ~ div .stButton > button[kind="primary"] {
            background-color: #ff7a00 !important;
            color: #ffffff !important;
            border: 1px solid #ff7a00 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ~ div .stButton > button:disabled {
            background-color: transparent !important;
            color: rgba(255, 255, 255, 0.45) !important;
            border: 1px solid rgba(255, 255, 255, 0.28) !important;
            opacity: 1 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stFileUploader"] ~ div > div:last-child .stButton > button {
            margin-bottom: 0 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: rgba(255, 255, 255, 0.75) !important;
            font-size: 0.78rem !important;
        }

        .msg-inicio-app {
            margin-top: 12vh;
            padding: 2rem 2.5rem;
            max-width: 520px;
            background: #f8f9fc;
            border: 1px solid #e2e6ef;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(13, 20, 64, 0.06);
        }

        .msg-inicio-app p {
            color: #0d1440;
            font-size: 1.35rem;
            font-weight: 600;
            margin: 0 0 0.5rem 0;
        }

        .msg-inicio-app span {
            color: #4a5568;
            font-size: 1rem;
            line-height: 1.5;
        }

        [data-testid="stSidebarNav"],
        [data-testid="stSidebarHeader"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    for nome in PAGINAS:
        if st.sidebar.button(
            nome,
            use_container_width=True,
            type="primary" if st.session_state.menu_ativo == nome else "secondary",
        ):
            st.session_state.menu_ativo = nome
            st.switch_page(PAGINAS[nome])

    st.sidebar.markdown("---")
    etl.render_secao_upload()
    etl.render_rodape_sidebar()