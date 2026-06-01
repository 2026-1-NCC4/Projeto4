import html

import streamlit as st

st.set_page_config(
    page_title="Campanhas | Cannoli Food Tech",
    layout="wide",
    initial_sidebar_state="expanded",
)

import etl
import funcs
import menu
import graficos
from ui.dashboard_theme import inject_executive_dashboard_css

inject_executive_dashboard_css()

st.session_state.menu_ativo = "Campanhas"
#region PRINCIPAL

# ── dados ───────────────────────────────────────────────────────────────────
dados = etl.carregar_ou_demo()
store        = dados["store"]
campaign     = dados["campaign"]
campaignxorder = dados["campaignxorder"]

# ── header e sidebar ────────────────────────────────────────────────────────
periodo, restaurante = menu.render_header_campanhas(store, campaignxorder)
menu.render_sidebar()

# ── filtros ─────────────────────────────────────────────────────────────────
if restaurante != "Todas":
    map_store = dict(zip(store["name"], store["id"]))
    sid = map_store[restaurante]
    cxo = campaignxorder[campaignxorder["storeid"] == sid].copy()
else:
    cxo = campaignxorder.copy()

cxo = funcs.filtrar_periodo_mes(cxo, periodo, "sent_at")

# ── cálculos globais (funções existentes, sem alteração) ────────────────────
taxa, rec_conv, n_env, n_conv = funcs.taxa_conversao_campanha(cxo)
lo, hi = funcs.wilson_ci(n_conv, n_env)

# ── dados enriquecidos ───────────────────────────────────────────────────────
df_ranking  = funcs.ranking_campanhas(cxo, campaign)
df_lojas    = funcs.campanhas_por_loja_detalhado(cxo, store)
df_res_loja = funcs.resumo_loja(df_lojas, store)

safe_loja   = html.escape(str(restaurante))
safe_periodo = html.escape(str(periodo))

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"""
<div class="exec-hero">
  <h1>Campanhas e engajamento</h1>
  <div class="sub">Mensagens enviadas, conversões e receita vinculada — análise por campanha e loja.</div>
  <div class="exec-pills">
    <span class="exec-pill brand">Parceiro: {safe_loja}</span>
    <span class="exec-pill">Período: {safe_periodo}</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


#region CARDS GLOBAIS 

m1, m2, m3, m4 = st.columns(4)
m1.metric("Mensagens enviadas (2)",    f"{n_env:,}".replace(",", "."))
m2.metric("Conversões atribuídas (4)", f"{n_conv:,}".replace(",", "."))
m3.metric("Taxa de conversão",         f"{taxa:.2f}%")
m4.metric("Receita atribuída (conv.)", funcs.formatar_moeda(rec_conv))

_nev = f"{n_env:,}".replace(",", ".")
_ncv = f"{n_conv:,}".replace(",", ".")
st.markdown(
    f"""
<div class="alert-strip">
  <strong>Intervalo Wilson (~95%)</strong> para a taxa de conversão:
  <strong>{lo:.2f}%</strong> a <strong>{hi:.2f}%</strong>
  (amostra: {_nev} mensagens · conversões observadas: {_ncv}).
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# region ABAS
# ══════════════════════════════════════════════════════════════════════════════
aba_camp, aba_lojas, aba_espec = st.tabs([" Campanhas", " Lojas", " Específico"])


# ─────────────────────────────────────────────────────────────────────────────
# region ABA 1 — CAMPANHAS
# ─────────────────────────────────────────────────────────────────────────────
with aba_camp:

    if df_ranking.empty:
        st.info("Sem dados de campanha para o período e loja selecionados.")
    else:
        # ── gráficos top/bottom ──────────────────────────────────────────────
        g1, g2 = st.columns(2)
        with g1:
            st.altair_chart(graficos.graf_top5_taxa_conversao(df_ranking),    use_container_width=True)
        with g2:
            st.altair_chart(graficos.graf_top5_receita(df_ranking),           use_container_width=True)

        g3, g4 = st.columns(2)
        with g3:
            st.altair_chart(graficos.graf_bottom5_taxa_conversao(df_ranking), use_container_width=True)
        with g4:
            st.altair_chart(graficos.graf_bottom5_receita(df_ranking),        use_container_width=True)

        st.markdown("---")

        # ── ranking completo ─────────────────────────────────────────────────
        st.markdown("**Ranking completo de campanhas**")

        ctrl_busca, ctrl_qtd, ctrl_todas = st.columns([3, 1.2, 0.8])
        with ctrl_busca:
            busca_rank = st.text_input(
                "Buscar no ranking",
                placeholder="Filtrar por nome de campanha...",
                key="rank_busca",
                label_visibility="collapsed",
            )
        with ctrl_qtd:
            n_vis = st.slider(
                "Visíveis", min_value=3, max_value=20, value=5, step=1, key="rank_n"
            )
        with ctrl_todas:
            ver_todas = st.checkbox("Ver todas", key="rank_todas")

        # aplica filtro de busca
        df_rank_exib = df_ranking.copy()
        if busca_rank.strip():
            mask = df_rank_exib["name"].astype(str).str.contains(
                busca_rank.strip(), case=False, na=False
            )
            df_rank_exib = df_rank_exib[mask]

        total_camp = len(df_rank_exib)
        df_rank_exib = df_rank_exib if ver_todas else df_rank_exib.head(n_vis)
        exib_camp   = len(df_rank_exib)

        st.caption(f"Exibindo {exib_camp} de {total_camp} campanhas")

        # constrói cards em dois loops paralelos (conversão | receita)
        col_rank, col_rec = st.columns([1.4, 1])

        with col_rank:
            st.caption("Conversão")
            receita_max_rank = df_ranking["receita_conv"].max() or 1
            itens = ""
            for _, row in df_rank_exib.iterrows():
                nome   = html.escape(str(row.get("name", f"Campanha {row['campaignid']}")))  
                tipo   = str(row.get("type", "")) 
                tipo   = html.escape(tipo) if tipo not in ("", "nan") else "—"
                n_e    = int(row["n_enviadas"])
                n_c    = int(row["n_conversoes"])
                taxa_c = float(row["taxa_conversao"])
                barra  = min(taxa_c / 20, 1.0)

                #porque html??? porque :(((((((((
                itens += f"""
<div style="margin-bottom:8px;padding:9px 11px;
     border:0.5px solid rgba(128,128,128,.2);border-radius:8px;">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:3px;">
    <span style="font-weight:500;font-size:13px;">{nome}</span>
    <span style="font-size:13px;font-weight:600;color:#534AB7;">{taxa_c:.1f}%</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
    <span style="font-size:10px;background:#EEEDFE;color:#3C3489;
          padding:1px 6px;border-radius:99px;">{tipo}</span>
    <span style="font-size:11px;color:gray;">{n_e:,} env · {n_c:,} conv</span>
  </div>
  <div style="background:rgba(128,128,128,.12);border-radius:3px;height:5px;">
    <div style="width:{barra*100:.0f}%;background:#7F77DD;border-radius:3px;height:5px;"></div>
  </div>
</div>"""

            altura = min(exib_camp * 82, 600)
            st.markdown(
                f'<div style="height:{altura}px;overflow-y:auto;padding-right:4px;">{itens}</div>',
                unsafe_allow_html=True,
            )

        with col_rec:
            st.caption("Receita atribuída")
            receita_max_exib = df_rank_exib["receita_conv"].max() or 1
            itens_r = ""
            for _, row in df_rank_exib.iterrows():
                nome  = html.escape(str(row.get("name", f"Campanha {row['campaignid']}")))
                rec   = float(row["receita_conv"])
                barra = rec / receita_max_exib
                itens_r += f"""
<div style="margin-bottom:8px;padding:9px 11px;
     border:0.5px solid rgba(128,128,128,.2);border-radius:8px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
    <span style="font-size:13px;">{nome}</span>
    <span style="font-size:13px;font-weight:500;">{funcs.formatar_moeda(rec)}</span>
  </div>
  <div style="background:rgba(128,128,128,.12);border-radius:3px;height:5px;">
    <div style="width:{barra*100:.0f}%;background:#1D9E75;border-radius:3px;height:5px;"></div>
  </div>
</div>"""

            st.markdown(
                f'<div style="height:{altura}px;overflow-y:auto;padding-right:4px;">{itens_r}</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# region ABA 2 — LOJAS
# ─────────────────────────────────────────────────────────────────────────────
with aba_lojas:

    if df_lojas.empty:
        st.info("Sem dados de lojas para o período selecionado.")
    else:
        n_lojas_ativas = df_res_loja["nome_loja"].nunique()
        total_msgs_loja = int(df_res_loja["n_enviadas"].sum())

        c1, c2 = st.columns(2)
        c1.metric("Lojas com campanhas no período", str(n_lojas_ativas))
        c2.metric("Total de mensagens (todas as lojas)", f"{total_msgs_loja:,}".replace(",", "."))

        st.markdown("")

        gl1, gl2 = st.columns(2)
        with gl1:
            st.altair_chart(graficos.graf_mensagens_por_loja(df_lojas),   use_container_width=True)
        with gl2:
            st.altair_chart(graficos.graf_conversao_por_loja(df_lojas),   use_container_width=True)

        st.markdown("---")
        st.markdown("**Resumo por loja**")
        st.dataframe(
            df_res_loja.rename(columns={
                "nome_loja":      "Loja",
                "n_campanhas":    "Campanhas",
                "n_enviadas":     "Enviadas",
                "n_conversoes":   "Conversões",
                "taxa_conversao": "Taxa (%)",
                "receita_conv":   "Receita (R$)",
            }).assign(**{
                "Taxa (%)":     lambda d: d["Taxa (%)"].round(2),
                "Receita (R$)": lambda d: d["Receita (R$)"].round(2),
            }),
            use_container_width=True,
            hide_index=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# region ABA 3 — ESPECÍFICO
# ─────────────────────────────────────────────────────────────────────────────
with aba_espec:

    col_camp_esp, col_loja_esp = st.columns(2)

    # ── busca por campanha ───────────────────────────────────────────────────
    with col_camp_esp:
        st.markdown("**Buscar por campanha**")
        busca_camp = st.text_input(
            "Campanha",
            placeholder="Digite o nome da campanha...",
            key="esp_camp_busca",
            label_visibility="collapsed",
        )

        if df_ranking.empty:
            st.info("Sem campanhas disponíveis.")
        else:
            nomes_camp = df_ranking["name"].astype(str).tolist()
            if busca_camp.strip():
                nomes_filt = [n for n in nomes_camp if busca_camp.strip().lower() in n.lower()]
            else:
                nomes_filt = nomes_camp

            if not nomes_filt:
                st.info(f"Nenhuma campanha encontrada para '{busca_camp}'.")
            else:
                for nome in nomes_filt:
                    row = df_ranking[df_ranking["name"].astype(str) == nome].iloc[0]
                    tipo   = str(row.get("type", "")) 
                    tipo   = tipo if tipo not in ("", "nan") else "—"
                    sendat = str(row.get("sendat", "")) 
                    sendat = sendat if sendat not in ("", "nan", "NaT") else "—"
                    n_e    = int(row["n_enviadas"])
                    n_c    = int(row["n_conversoes"])
                    taxa_c = float(row["taxa_conversao"])
                    rec    = float(row["receita_conv"])

                    # lojas vinculadas a esta campanha
                    camp_id = row["campaignid"]
                    lojas_camp = df_lojas[df_lojas["campaignid"] == camp_id]["nome_loja"].unique().tolist()
                    lojas_str  = " · ".join(lojas_camp) if lojas_camp else "—"

                    with st.expander(f"{nome}", expanded=(len(nomes_filt) == 1)):
                        ec1, ec2, ec3 = st.columns(3)
                        ec1.metric("Enviadas",    f"{n_e:,}".replace(",", "."))
                        ec2.metric("Conversões",  f"{n_c:,}".replace(",", "."))
                        ec3.metric("Taxa",        f"{taxa_c:.2f}%")
                        st.markdown(
                            f"**Receita atribuída:** {funcs.formatar_moeda(rec)}  \n"
                            f"**Tipo:** {html.escape(tipo)}  \n"
                            f"**Data envio:** {html.escape(sendat)}  \n"
                            f"**Lojas:** {html.escape(lojas_str)}"
                        )

    #region dor pura e encarnada
    # ── busca por loja ───────────────────────────────────────────────────────
    with col_loja_esp:
        st.markdown("**Buscar por loja**")
        busca_loja = st.text_input(
            "Loja",
            placeholder="Digite o nome da loja...",
            key="esp_loja_busca",
            label_visibility="collapsed",
        )

        if df_res_loja.empty:
            st.info("Sem lojas disponíveis.")
        else:
            nomes_loja = df_res_loja["nome_loja"].astype(str).tolist()
            if busca_loja.strip():
                nomes_loja_filt = [n for n in nomes_loja if busca_loja.strip().lower() in n.lower()]
            else:
                nomes_loja_filt = nomes_loja

            if not nomes_loja_filt:
                st.info(f"Nenhuma loja encontrada para '{busca_loja}'.")
            else:
                for nome_loja in nomes_loja_filt:
                    row_l = df_res_loja[df_res_loja["nome_loja"].astype(str) == nome_loja].iloc[0]
                    n_el    = int(row_l["n_enviadas"])
                    n_cl    = int(row_l["n_conversoes"])
                    taxa_l  = float(row_l["taxa_conversao"])
                    rec_l   = float(row_l["receita_conv"])
                    n_cl_ativas = int(row_l["n_campanhas"])

                    # campanhas loja com nome
                    sid_l = store[store["name"] == nome_loja]["id"].values
                    if len(sid_l):
                        camps_loja = df_lojas[df_lojas["storeid"] == sid_l[0]]["campaignid"].unique()
                        nomes_camps_loja = []
                        for cid in camps_loja:
                            rows_c = df_ranking[df_ranking["campaignid"] == cid]
                            if not rows_c.empty:
                                nomes_camps_loja.append(str(rows_c.iloc[0]["name"]))
                            else:
                                nomes_camps_loja.append(f"Campanha {cid}")
                        camps_str = " · ".join(nomes_camps_loja) if nomes_camps_loja else "—"
                    else:
                        camps_str = "—"

                    with st.expander(f"{nome_loja}", expanded=(len(nomes_loja_filt) == 1)):
                        el1, el2, el3 = st.columns(3)
                        el1.metric("Mensagens",  f"{n_el:,}".replace(",", "."))
                        el2.metric("Conversões", f"{n_cl:,}".replace(",", "."))
                        el3.metric("Taxa",       f"{taxa_l:.2f}%")
                        st.markdown(
                            f"**Receita atribuída:** {funcs.formatar_moeda(rec_l)}  \n"
                            f"**Campanhas ativas:** {n_cl_ativas}  \n"
                            f"**Campanhas:** {html.escape(camps_str)}"
                        )
#region Notas metodológicas
#── notas metodológicas ──────────────────────────────────────────────────────
with st.expander("Notas metodológicas (extensão FECAP)", expanded=False):
    st.markdown(
        """
- **Taxa de conversão**: razão entre mensagens com status **4** (conversão atribuída) e status **2** (enviadas), conforme regras do projeto.
- **Wilson**: intervalo para proporção binomial; útil quando o denominador é pequeno.
- **Filtro de período**: aplica-se à coluna `sent_at` de `CAMPAIGNXORDER` usando o mês selecionado no cabeçalho (`YYYY-MM`).
- **Ranking**: usa `ranking_campanhas()` — join de `CAMPAIGN` com `CAMPAIGNXORDER` agrupado por `campaignid`.
- **Lojas**: usa `campanhas_por_loja_detalhado()` e `resumo_loja()` — agrupamento por `campaignid × storeid`.
- **Gráficos**: Altair (barras horizontais) para top/bottom 5 e comparativos por loja.
"""
    )