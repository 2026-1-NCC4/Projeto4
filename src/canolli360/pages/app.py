import html

import streamlit as st

st.set_page_config(
    page_title="Cannoli Food Tech — BI",
    layout="wide",
    initial_sidebar_state="expanded",
)

import etl
import funcs
import graficos
import menu
import pandas as pd
from ui.dashboard_theme import inject_executive_dashboard_css

inject_executive_dashboard_css()

st.session_state.menu_ativo = "Visão geral"

menu.render_sidebar()
dados = etl.carregar_ou_demo()

store = dados["store"]
customer = dados["customer"]
storeorder = dados["storeorder"]

periodo, restaurante, canal, pedido, df_loja = menu.render_header(store, storeorder)

df_filtrado = funcs.filtrar_periodo(df_loja, periodo, "createdat")

receita = funcs.receita_total(df_filtrado)
total_vendas = funcs.total_pedidos(df_filtrado)
ticket_medio_valor = funcs.ticket_medio(df_filtrado, receita)
clientes_tot = funcs.clientes_ativos(df_loja, customer, periodo)

receita_formatada = funcs.formatar_moeda(receita)
ticket_formatado = funcs.formatar_moeda(ticket_medio_valor)

safe_loja = html.escape(str(restaurante))
safe_periodo = html.escape(str(periodo))

st.markdown(
    f"""
<div class="exec-hero">
  <h1>Visão geral</h1>
  <div class="sub">Indicadores rápidos da operação no recorte do cabeçalho (parceiro e período).</div>
  <div class="exec-pills">
    <span class="exec-pill brand">Parceiro: {safe_loja}</span>
    <span class="exec-pill">Período: {safe_periodo}</span>
    <span class="exec-pill ok">Pedidos concluídos (status 16)</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Receita total", receita_formatada)
with k2:
    st.metric("Pedidos concluídos", f"{total_vendas:,}".replace(",", "."))
with k3:
    st.metric("Ticket médio", ticket_formatado)
with k4:
    st.metric("Clientes ativos", f"{clientes_tot:,}".replace(",", "."))

st.markdown("<br/>", unsafe_allow_html=True)

st.markdown("### Receita por mês")
st.caption("Evolução da receita ao longo do tempo (pedidos concluídos, status 16).")

df_mes = funcs.valor_per_mes(df_filtrado, periodo)
grafico = graficos.grafico_receita_mensal(df_mes)
st.altair_chart(grafico, use_container_width=True)
