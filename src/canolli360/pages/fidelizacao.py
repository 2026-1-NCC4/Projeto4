import streamlit as st

st.set_page_config(
    page_title="RFM & Retenção | Cannoli Food Tech",
    layout="wide",
    initial_sidebar_state="expanded",
)

import altair as alt

import etl
import funcs
import menu

st.session_state.menu_ativo = "RFM & retenção"

menu.render_sidebar()
dados = etl.carregar_ou_demo()
store = dados["store"]
storeorder = dados["storeorder"]

st.title("RFM e fidelização")
st.caption(
    "Segmentação por Recência, Frequência e Valor (pedidos concluídos). "
    "Coluna de parceiro = nome da loja do último pedido no período filtrado."
)

periodo, restaurante, canal, pedido, df_loja = menu.render_header(store, storeorder)

rfm = funcs.calcular_rfm(df_loja, periodo, store)
if rfm.empty:
    st.warning("Sem pedidos concluídos no período e loja selecionados.")
    st.stop()

agg = rfm.groupby("segmento", as_index=False).size().rename(columns={"size": "clientes"})

c1, c2, c3 = st.columns(3)
c1.metric("Clientes analisados (RFM)", f"{len(rfm):,}".replace(",", "."))
prop_risco = (rfm["segmento"].isin(["Em risco", "Hibernando / churn"]).mean() * 100)
c2.metric("Em risco ou hibernando (aprox.)", f"{prop_risco:.1f}%")
c3.metric("Campeões", f"{(rfm['segmento'] == 'Campeões').sum():,}".replace(",", "."))

chart = (
    alt.Chart(agg)
    .mark_bar(color="#ff7a00")
    .encode(
        x=alt.X("clientes:Q", title="Quantidade de clientes"),
        y=alt.Y("segmento:N", sort="-x", title="Segmento"),
        tooltip=["segmento", "clientes"],
    )
    .properties(height=280)
)
st.altair_chart(chart, use_container_width=True)

st.subheader("Amostra (por parceiro)")
amostra = rfm.head(25).copy()
st.dataframe(
    amostra[
        ["parceiro", "recencia_dias", "frequencia", "valor", "R", "F", "M", "segmento"]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "parceiro": st.column_config.TextColumn("Parceiro (nome da loja)", width="large"),
    },
)

cols_export = ["parceiro", "recencia_dias", "frequencia", "valor", "R", "F", "M", "segmento"]
csv_out = rfm[cols_export]
st.download_button(
    label="Exportar segmentação RFM (CSV)",
    data=csv_out.to_csv(index=False).encode("utf-8"),
    file_name="cannoli_food_tech_rfm_segmentos.csv",
    mime="text/csv",
)
