import streamlit as st

# mapeamento entre nome e página
PAGINAS = {
    "Finance": "app.py",
    "Indicadores": "pages/indicadores.py",
    "Retention": "pages/Retention.py",
    "Settings": "pages/Settings.py",
}


# HEADER PADRONIZADO
def render_header(store, storeorder):
    # preparando daods usados para filtro de loja
    lista_lojas = store["name"].dropna().unique().tolist()
    lista_lojas.insert(0, "Todas")
    map_store = dict(zip(store['name'], store['id']))

    # estilização do header
    with st.container():
        st.markdown(
            '<style>div.block-container{padding-top:2rem;}</style>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="header">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        with col1:
            st.markdown("### Canolli Foodtech")

        # filtro de período
        with col2:
            if "periodo" not in st.session_state:
                st.session_state.periodo = "Último mês"

            periodo = st.selectbox(
                "Período",
                [
                    "Última semana",
                    "Último mês",
                    "Último bimestre",
                    "Último trimestre",
                    "Último semestre",
                    "Último ano",
                    "Todo o período"
                ],
                key="periodo"
            )

        # filtro de loja
        with col3:
            if "restaurante" not in st.session_state:
                st.session_state.restaurante = "Todas"

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

        st.markdown('</div>', unsafe_allow_html=True)

    # retorno dos dados utilizados pelas funções
    return periodo, restaurante, df_loja


# SIDEBAR PADRONIZADA
def render_sidebar():
    # estado inicial = app.py
    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "Finance"
    
    # lógica de mudar de menu
    def mudar_menu(menu):
        st.session_state.menu_ativo = menu

        if menu == "Finance":
            st.switch_page("app.py")

        st.switch_page(PAGINAS[menu])

    # estilização da sidebar
    st.sidebar.markdown("""
    <style>
        section[data-testid="stSidebar"] > div {
            background-color: #0d1440;
            padding: 20px;
        }

        div.stButton > button {
            width: 100%;
            height: 80px;
            border-radius: 10px;
            margin-bottom: 10px;
            transition: all 0.2s ease;
        }

        div.stButton > button[kind="primary"] {
            background-color: #ff7a00;
            color: white;
            border: 1px solid #ff7a00;
        }

        div.stButton > button[kind="secondary"] {
            background-color: transparent;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        div.stButton > button[kind="secondary"]:hover {
            background-color: rgba(255, 122, 0, 0.15);
        }

        [data-testid="stSidebarNav"] {
        display: none;
        }
    </style>
    """, unsafe_allow_html=True)

    # botões
    for menu in PAGINAS.keys():
        if st.sidebar.button(
            menu,
            use_container_width=True,
            type="primary" if st.session_state.menu_ativo == menu else "secondary",
        ):
            st.session_state.menu_ativo = menu
            st.switch_page(PAGINAS[menu])