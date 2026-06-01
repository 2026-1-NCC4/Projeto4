import streamlit as st

st.set_page_config(
    page_title="Indicadores | Cannoli Food Tech",
    layout="wide",
    initial_sidebar_state="expanded",
)

import numpy as np
import pandas as pd

import etl
import funcs
import menu
from ui import dashboard_charts as dch
from ui.dashboard_theme import fmt_milhares, inject_executive_dashboard_css

def safe_div(numerador, denominador, fallback=0.0):
    """Divisão segura — retorna fallback se denominador for zero ou NaN."""
    if not denominador or pd.isna(denominador):
        return fallback
    return numerador / denominador

inject_executive_dashboard_css()

st.session_state.menu_ativo = "Indicadores"

menu.render_sidebar()
dados = etl.carregar_ou_demo()
store = dados["store"]
customer = dados["customer"]
storeorder = dados["storeorder"]
customeraddress = dados["customeraddress"]
campaign = dados["campaign"]
campaignxorder = dados["campaignxorder"]

periodo, restaurante, canal, pedido, df_loja = menu.render_header(store, storeorder)

df_filtrado = funcs.filtrar_periodo(df_loja, periodo, "createdat")
status16 = df_filtrado[df_filtrado["status"] == 16]
if status16.empty or df_filtrado.empty:
    st.warning("Sem pedidos no período e loja selecionados. Tente um filtro diferente.")
    st.stop()
status8 = df_filtrado[df_filtrado["status"] == 8]
status11 = df_filtrado[df_filtrado["status"] == 11]
status14 = df_filtrado[df_filtrado["status"] == 14]
if restaurante != "Todas":
    store_id = dados["store"].loc[dados["store"]["name"] == restaurante, "id"].iloc[0]
    cxo_filtrado = campaignxorder[campaignxorder["storeid"] == store_id]
else:
    cxo_filtrado = campaignxorder.copy()
status2 = cxo_filtrado[cxo_filtrado["status"] == 2]
status4 = cxo_filtrado[cxo_filtrado["status"] == 4]

# ---------------------------------------------------------------------------
# Cálculos (mesma ordem e fórmulas do relatório original — sem alteração de regras)
# ---------------------------------------------------------------------------

subtotal = status16["subtotalamount"].sum()
descontos = status16["discountamount"].sum()
impostos = status16["taxamount"].sum()
receita = status16["totalamount"].sum()
porcent_subtotal = (subtotal / receita) * 100
porcent_impostos = (impostos / receita) * 100

rlc = subtotal - descontos
desconto_subtotal = (descontos / subtotal) * 100

qnt_pedido = len(status16)
ticket_medio = receita / qnt_pedido
universo = len(df_filtrado)
receita_pot = universo * ticket_medio
taxa_realizar = safe_div(receita, receita_pot) * 100

n_concluido = universo - qnt_pedido
n_receita = n_concluido * ticket_medio
porc_receita = safe_div(n_receita, receita) * 100

cancel_efetivos = len(status8) + len(status11) + len(status14)
taxa_cancel = safe_div(cancel_efetivos, universo) * 100

cancel_store = safe_div(len(status8), universo) * 100
cancel_cliente = safe_div(len(status11), universo) * 100
cancel_timeout = safe_div(len(status14), universo) * 100

receita_perdida = cancel_efetivos * ticket_medio if qnt_pedido > 0 else 0.0
porc_receita_perdida = safe_div(receita_perdida, receita) * 100

lojas = len(store["id"])
loja_ativa = len(status16["storeid"].unique())
taxa_ativa = safe_div(loja_ativa, lojas) * 100

rec_loja_ativa = safe_div(receita, loja_ativa)
receita_mensal = safe_div(rec_loja_ativa, 9)

df_filtrado["scheduledat"] = pd.to_datetime(df_filtrado["scheduledat"], format="ISO8601")
df_filtrado["scheduledat"] = pd.to_datetime(df_filtrado["scheduledat"], format="ISO8601", errors="coerce")
sched_min = df_filtrado["scheduledat"].min()
sched_max = df_filtrado["scheduledat"].max()

if pd.isna(sched_min) or pd.isna(sched_max):
    periodo_dia = 1
else:
    periodo_dia = max(1, (sched_max - sched_min).days + 1)
receita_dia = safe_div(receita, periodo_dia)
pedido_dia = safe_div(qnt_pedido, periodo_dia)

pedidos_loja = safe_div(qnt_pedido, loja_ativa)
pedidos_mes = safe_div(pedidos_loja, 9)

cliente_concluido = len(status16["customerid"].unique())
arpu = safe_div(receita, cliente_concluido)

share_canal = status16.groupby("saleschannel")["totalamount"].sum()
share_canal = share_canal / share_canal.sum()
hhi_canal = ((share_canal**2).sum()) * 10000
max_share_canal = share_canal.max() * 100
maior_canal = share_canal.idxmax()

share_loja = status16.groupby("storeid")["totalamount"].sum()
share_loja = share_loja / share_loja.sum()
hhi_loja = ((share_loja**2).sum()) * 10000
max_share_loja = share_loja.max() * 100
maior_loja_id = share_loja.idxmax()
msk_loja = store["id"].astype(str) == str(maior_loja_id)
maior_loja = str(store.loc[msk_loja, "name"].iloc[0]) if msk_loja.any() else str(maior_loja_id)

share_ordenado = share_loja.sort_values(ascending=False)
top1 = share_ordenado.head(1).sum() * 100
top4 = share_ordenado.head(4).sum() * 100
top10 = share_ordenado.head(10).sum() * 100


def top20_percent(share, valor):
    share_ordenado_inner = share.sort_values(ascending=False)
    percent = max(1, int(len(share_ordenado_inner) * valor))
    return share_ordenado_inner.head(percent).sum() * 100


top20_porc = top20_percent(share_loja, 0.2)

receita_loja = share_loja.sort_values()
valores = receita_loja.values
n = len(valores)
if n > 0 and np.sum(valores) > 0:
    gini = (2 * np.sum((np.arange(1, n + 1) * valores))) / (n * np.sum(valores)) - (n + 1) / n
else:
    gini = float("nan")

invest_promo = status16["discountamount"].sum()
ip_receita = (invest_promo / receita) * 100
ip_subtotal = (invest_promo / subtotal) * 100

pedidos_descont = status16.loc[status16["discountamount"] > 0, "discountamount"].count()
pedidos_benef = (pedidos_descont / qnt_pedido) * 100
subtotal_benef = status16.loc[status16["discountamount"] > 0, "subtotalamount"].sum()
prof_media = (invest_promo / subtotal_benef) * 100 if subtotal_benef else float("nan")
if pedidos_descont:
    dma = invest_promo / pedidos_descont
else:
    dma = float("nan")

com_desc = status16.loc[status16["discountamount"] > 0, "totalamount"].mean()
sem_desc = status16.loc[status16["discountamount"] == 0, "totalamount"].mean()
if pd.notna(sem_desc) and sem_desc != 0 and pd.notna(com_desc):
    uplift = ((com_desc - sem_desc) / sem_desc) * 100
else:
    uplift = float("nan")

if pedidos_descont:
    custo_pedido_geral = invest_promo / pedidos_descont
else:
    custo_pedido_geral = float("nan")
custo_pedido = invest_promo / qnt_pedido
if pedidos_descont and pd.notna(custo_pedido_geral):
    cpd = custo_pedido_geral - custo_pedido
else:
    cpd = float("nan")

msg_enviadas = status2["message_id"].count()
conv_atribuidas = status4["message_id"].count()
tax_conver = (conv_atribuidas / msg_enviadas) * 100 if msg_enviadas else 0.0
rec_atribuida = status4["totalamount"].sum()
porc_rec_atrib = (rec_atribuida / receita) * 100
receita_msg = rec_atribuida / msg_enviadas if msg_enviadas else 0.0

status16 = status16.copy()
status16["scheduledat"] = pd.to_datetime(status16["scheduledat"], format="ISO8601")
status16["ano_mes"] = status16["scheduledat"].dt.to_period("M")
mes_inicio = status16["ano_mes"].min()
receita_inicio = status16.loc[status16["ano_mes"] == mes_inicio, "totalamount"].sum()

# Variação MoM receita (apenas para exibição em st.metric — não altera KPIs base)
mom_receita_pct = None
try:
    g_m = (
        status16.groupby(status16["scheduledat"].dt.to_period("M"))["totalamount"]
        .sum()
        .sort_index()
    )
    if len(g_m) >= 2:
        mom_receita_pct = float((g_m.iloc[-1] - g_m.iloc[-2]) / g_m.iloc[-2] * 100)
except Exception:
    mom_receita_pct = None

# Health score (índice executivo derivado dos KPIs já calculados — composição documentada na UI)
s_cancel = max(0.0, 100.0 - min(taxa_cancel * 2.2, 88.0))
s_ativa = min(100.0, taxa_ativa * 1.05)
s_hi = max(0.0, 100.0 - min(hhi_loja / 55.0, 92.0))
s_real = float(min(100.0, max(0.0, taxa_realizar))) if receita_pot > 0 else 50.0
health_score = int(round(0.32 * s_cancel + 0.26 * s_ativa + 0.22 * s_hi + 0.20 * s_real))
health_score = max(0, min(100, health_score))

# ---------------------------------------------------------------------------
# Cabeçalho executivo
# ---------------------------------------------------------------------------
try:
    ult_dado = pd.to_datetime(df_filtrado["createdat"], errors="coerce").max()
    ult_txt = ult_dado.strftime("%d/%m/%Y %H:%M") if pd.notna(ult_dado) else "—"
except Exception:
    ult_txt = "—"

st.markdown(
    f"""
<div class="exec-hero">
  <h1>Cannoli Food Tech</h1>
  <div class="sub">Central de Inteligência Operacional · Cannoli Food Tech</div>
  <div class="exec-pills">
    <span class="exec-pill ok">● Sistema online</span>
    <span class="exec-pill brand">● {fmt_milhares(universo)} pedidos na base</span>
    <span class="exec-pill">● Último dado: {ult_txt}</span>
    <span class="exec-pill ok">● LGPD compliant</span>
    <span class="exec-pill">● Filtro período: {periodo}</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("##### Resumo rápido")
st.metric("Parceiro no filtro", restaurante)
st.metric("Pedidos (universo)", f"{universo:,}".replace(",", "."))
st.metric("Receita realizada", funcs.formatar_moeda(receita))
st.caption("Métricas globais refletem a base carregada pelo ETL (sem mudança de regras).")

# KPIs principais
if restaurante == "Todas":
    k2, k3, k4, k5, k6 = st.columns(5)

    k6.metric("Lojas ativas", f"{loja_ativa} / {lojas}", delta=f"{taxa_ativa:.1f}% ativação")
else:
    k2, k3, k4, k5 = st.columns(4)
k2.metric("Ticket médio", funcs.formatar_moeda(ticket_medio))
k3.metric("Pedidos concluídos", f"{qnt_pedido:,}".replace(",", "."))
k4.metric("Taxa cancelamento", f"{taxa_cancel:.2f}%", delta_color="inverse")
k5.metric("ARPU", funcs.formatar_moeda(arpu))

row_h = st.columns([1, 1.15])
with row_h[0]:
    st.plotly_chart(
        dch.fig_health_gauge(health_score, "Health Score executivo"),
        use_container_width=True,
        key="gauge_health",
    )
    if health_score >= 72:
        st.success("Saúde operacional **favorável** — cancelamento e ativação sob controle relativo.")
    elif health_score >= 48:
        st.warning("Saúde operacional **moderada** — revisar concentração e cancelamentos.")
    else:
        st.error("Saúde operacional **pressionada** — priorizar ações de risco e ativação de parceiros.")

with row_h[1]:
    st.markdown("##### Central de alertas")
    alertas: list[str] = []
    canal_txt = str(maior_canal).lower()
    if "ifood" in canal_txt or "i food" in canal_txt:
        alertas.append("Alta exposição ao canal dominante (possível dependência de marketplace).")
    if max_share_canal > 42:
        alertas.append(f"Maior canal concentra {max_share_canal:.1f}% da receita concluída.")
    if taxa_ativa < 60:
        alertas.append(f"Apenas {taxa_ativa:.1f}% das lojas cadastradas estão ativas.")
    if top1 > 32:
        alertas.append("Receita muito concentrada no top-1 parceiro (risco operacional).")
    if porc_rec_atrib >= 15:
        alertas.append(f"Campanhas representam ~{porc_rec_atrib:.1f}% da receita — monitorar mix orgânico/pago.")
    if not alertas:
        alertas.append("Nenhum alerta crítico automático — manter monitoramento periódico.")
    for a in alertas[:6]:
        st.markdown(f'<div class="alert-strip">⚠ {a}</div>', unsafe_allow_html=True)

st.markdown("### Insights estratégicos")
col_i1, col_i2 = st.columns(2)
with col_i1:
    if pd.notna(uplift) and uplift < 0:
        st.info(
            f"Ticket **com desconto** está **{abs(uplift):.1f}%** abaixo do ticket sem desconto — revisar política promocional."
        )
    elif pd.notna(uplift):
        st.success(
            f"Ticket com desconto **{uplift:.1f}%** acima do sem desconto — uplift positivo no mix atual."
        )
    else:
        st.caption("Uplift de ticket indisponível (dados insuficientes para comparar com/sem desconto).")
    if hhi_loja >= 2500:
        st.warning(f"HHI por loja **{hhi_loja:.0f}** indica concentração elevada na rede.")
    else:
        st.success(f"HHI por loja **{hhi_loja:.0f}** — concentração {'moderada' if hhi_loja >= 1500 else 'mais distribuída'}.")
with col_i2:
    if msg_enviadas and tax_conver > 0:
        st.success(f"Conversão de campanhas **{tax_conver:.2f}%** (mensagens 2 → conversões 4).")
    if not np.isnan(gini) and gini > 0.7:
        st.error(f"Gini por loja **{gini:.3f}** — desigualdade de receita entre parceiros elevada.")
    elif not np.isnan(gini) and gini >= 0.5:
        st.warning(f"Gini **{gini:.3f}** — desigualdade alta entre parceiros.")
    elif not np.isnan(gini):
        st.info(f"Gini **{gini:.3f}** — desigualdade entre parceiros mais contida.")

tabs = st.tabs(
    [
        "Visão geral",
        "Receita",
        "Operação",
        "Risco",
        "Campanhas",
        "Crescimento",
    ]
)

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(dch.fig_receita_mensal(status16), use_container_width=True, key="tab0_rm")
    with c2:
        st.plotly_chart(dch.fig_pedidos_por_dia(df_filtrado), use_container_width=True, key="tab0_pd")
    st.plotly_chart(dch.fig_concentracao_canal(share_canal), use_container_width=True, key="tab0_tr")
    hm = dch.fig_heatmap_rf(status16)
    if hm is not None:
        st.plotly_chart(hm, use_container_width=True, key="tab0_hm")

with tabs[1]:
    st.plotly_chart(dch.fig_receita_mensal(status16), use_container_width=True, key="tab1_rm")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Subtotal concluídos", funcs.formatar_moeda(subtotal))
    r2.metric("Descontos", funcs.formatar_moeda(descontos))
    r3.metric("Impostos", funcs.formatar_moeda(impostos))
    r4.metric("% subtotal / receita", f"{porcent_subtotal:.2f}%")
    st.plotly_chart(dch.fig_receita_por_loja(status16, store), use_container_width=True, key="tab1_loja")
    with st.expander("Detalhamento contábil (estrutura de receita — entrega acadêmica)", expanded=False):
        st.markdown(
            f"""
- Receita líquida comercial (RLC): **{funcs.formatar_moeda(rlc)}** · Taxa desconto/subtotal: **{desconto_subtotal:.2f}%**
- Receita potencial: **{funcs.formatar_moeda(receita_pot)}** · Realizada: **{funcs.formatar_moeda(receita)}** · Taxa realização: **{taxa_realizar:.2f}%**
- Custo oportunidade não concluídos: **{funcs.formatar_moeda(n_receita)}** (**{porc_receita:.2f}%** da receita)
- % impostos sobre receita: **{porcent_impostos:.2f}%**
"""
        )

with tabs[2]:
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Receita / dia", funcs.formatar_moeda(receita_dia))
    o2.metric("Pedidos / dia", f"{pedido_dia:.0f}")
    o3.metric("Pedidos / loja ativa", f"{pedidos_loja:.0f}")
    o4.metric("Pedidos / loja / mês (÷9)", f"{pedidos_mes:.0f}")
    st.plotly_chart(dch.fig_pedidos_por_dia(df_filtrado), use_container_width=True, key="tab2_pd")
    with st.expander("Detalhamento operacional", expanded=False):
        st.markdown(
            f"""
- Lojas cadastradas: **{lojas}** · Ativas: **{loja_ativa}** · Taxa ativação: **{taxa_ativa:.2f}%**
- Receita média por loja ativa: **{funcs.formatar_moeda(rec_loja_ativa)}** · Rec. mensal média/loja (÷9): **{funcs.formatar_moeda(receita_mensal)}**
- Janela operacional: **{periodo_dia}** dias
- Clientes com pedido concluído: **{cliente_concluido}**
"""
        )

with tabs[3]:
    st.plotly_chart(
        dch.fig_cancelamentos_origem(cancel_store, cancel_cliente, cancel_timeout),
        use_container_width=True,
        key="tab3_can",
    )
    z1, z2, z3 = st.columns(3)
    z1.metric("Cancelamentos efetivos", f"{cancel_efetivos}")
    z2.metric("Receita perdida (estim.)", funcs.formatar_moeda(receita_perdida))
    z3.metric("% receita perdida", f"{porc_receita_perdida:.2f}%")
    st.plotly_chart(dch.fig_concentracao_canal(share_canal), use_container_width=True, key="tab3_tr")
    with st.expander("Detalhamento risco & concentração", expanded=False):
        gini_txt = f"{gini:.3f}" if pd.notna(gini) else "—"
        st.markdown(
            f"""
- HHI canal: **{hhi_canal:.0f}** · Maior canal: **{maior_canal}** (**{max_share_canal:.2f}%**)
- HHI loja: **{hhi_loja:.0f}** · Maior parceiro: **{maior_loja}** (**{max_share_loja:.2f}%**)
- Curva ABC: Top1 **{top1:.2f}%** · Top4 **{top4:.2f}%** · Top10 **{top10:.2f}%** · Top20% lojas **{top20_porc:.2f}%**
- Coef. Gini: **{gini_txt}**
"""
        )

with tabs[4]:
    st.plotly_chart(dch.fig_campanhas_funil(int(msg_enviadas), int(conv_atribuidas)), use_container_width=True, key="tab4_fun")
    st.plotly_chart(dch.fig_ticket_desconto(com_desc, sem_desc), use_container_width=True, key="tab4_tk")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Mensagens enviadas (2)", f"{int(msg_enviadas):,}".replace(",", "."))
    p2.metric("Conversões (4)", f"{int(conv_atribuidas):,}".replace(",", "."))
    p3.metric("Taxa conversão", f"{tax_conver:.2f}%")
    p4.metric("Receita atribuída", funcs.formatar_moeda(rec_atribuida))
    with st.expander("Detalhamento campanhas & promoção", expanded=False):
        prof_txt = f"{prof_media:.2f}%" if pd.notna(prof_media) else "—"
        dma_txt = funcs.formatar_moeda(dma) if pd.notna(dma) else "—"
        upl_txt = f"{uplift:.2f}%" if pd.notna(uplift) else "—"
        cpg_txt = funcs.formatar_moeda(custo_pedido_geral) if pd.notna(custo_pedido_geral) else "—"
        cpd_txt = funcs.formatar_moeda(cpd) if pd.notna(cpd) else "—"
        st.markdown(
            f"""
- Investimento promocional: **{funcs.formatar_moeda(invest_promo)}** (**{ip_receita:.2f}%** receita · **{ip_subtotal:.2f}%** subtotal)
- Pedidos c/ desconto: **{int(pedidos_descont)}** (**{pedidos_benef:.2f}%**) · Profundidade média: **{prof_txt}** · DMA: **{dma_txt}**
- Uplift ticket: **{upl_txt}**
- Custo pedido c/ desc.: **{cpg_txt}** · Diluído: **{cpd_txt}**
- % receita atribuída campanhas: **{porc_rec_atrib:.2f}%** · Receita/msg: **{funcs.formatar_moeda(receita_msg)}**
"""
        )

with tabs[5]:
    st.plotly_chart(dch.fig_receita_mensal(status16), use_container_width=True, key="tab5_rm")
    st.metric("Receita no primeiro mês da série", funcs.formatar_moeda(receita_inicio))
    with st.expander("Nota metodológica (sazonalidade)", expanded=False):
        st.caption(
            "Indicador 6.1 original: receita agregada no primeiro mês (`ano_mes` mínimo) da série de pedidos concluídos."
        )
