import streamlit as st
import pandas as pd

# mapeamento entre nome e página
PAGINAS = {
    "Finance": "app.py",
    "Indicadores": "pages/indicadores.py",
    "Retention": "pages/Retention.py",
    "Settings": "pages/Settings.py",
}


# HEADER PADRONIZADO
def render_header(store, storeorder):
    
    # organizando infos de período
    datas = pd.to_datetime(storeorder['createdat'], format='mixed', utc=True).dt.to_period('M')
    lista_periodo = ["Todos os períodos"] + sorted(
        datas.astype(str).unique().tolist(), 
        reverse=True
    )
    
    # organizando infos de loja
    lista_lojas = store["name"].dropna().unique().tolist()
    lista_lojas.insert(0, "Todas")
    map_store = dict(zip(store['name'], store['id']))

    # organizando infos de canal
    lista_canal = storeorder["saleschannel"].dropna().unique().tolist()
    lista_canal.insert(0, "Todos")
    map_canal = dict(zip(storeorder['saleschannel'], storeorder['saleschannel']))

    # organizando infos de pedido
    lista_pedido = storeorder["ordertype"].dropna().unique().tolist()
    lista_pedido.insert(0, "Todos")
    map_pedido = dict(zip(storeorder['ordertype'], storeorder['ordertype']))

    # estilização do header
    with st.container():
        st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)
        st.markdown('<div class="header">', unsafe_allow_html=True)
        col1,col2,col3,col4,col5 = st.columns([2,2,2,2,2])
        
        # titulo
        with col1:
            st.markdown("### Canolli Foodtech")

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

            if canal != "Todos":
                df_loja = df_loja[df_loja['saleschannel'] == map_canal[canal]]
        
        #filtro de pedido
        with col5:
            if "pedido" not in st.session_state:
                st.session_state.pedido = "Todos os pedidos"

            pedido = st.selectbox(
                "Tipo de pedido",
                lista_pedido,
                key="pedido"
            )

            if pedido != "Todos":
                df_loja = df_loja[df_loja['ordertype'] == map_pedido[pedido]]

        if periodo != "Todos os períodos":
            periodo_selecionado = pd.Period(periodo, freq='M')
            df_loja = df_loja[
                pd.to_datetime(df_loja['createdat'], format='mixed', utc=True).dt.to_period('M') == periodo_selecionado
            ]
        
        st.markdown('</div>', unsafe_allow_html=True)

    # devolve as infos entregues pelas funções
    return periodo, restaurante, canal, pedido, df_loja


# SIDEBAR PADRONIZADA
def render_sidebar():
    # inicia em finance
    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "Finance"
    
    # logica pra muda o menu
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

    # botooes que piscam diferente :D
    for menu in PAGINAS.keys():
        if st.sidebar.button(menu,use_container_width=True,
            type="primary" if st.session_state.menu_ativo == menu else "secondary",
        ):
            st.session_state.menu_ativo = menu
            st.switch_page(PAGINAS[menu])