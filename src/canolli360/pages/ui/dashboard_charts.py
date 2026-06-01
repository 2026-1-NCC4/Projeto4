"""Gráficos Plotly alinhados ao design Figma (theme.css — charts 1–5)."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ui.dashboard_theme import (
    ACCENT,
    BORDER,
    CHART_2,
    CHART_4,
    MUTED,
    PLOTLY_LAYOUT,
    TEXT_MUTED,
)


def _layout(**kwargs):
    base = dict(PLOTLY_LAYOUT)
    base.update(kwargs)
    return base


def fig_receita_mensal(status16: pd.DataFrame) -> go.Figure:
    df = status16.copy()
    if "scheduledat" in df.columns:
        df["d"] = pd.to_datetime(df["scheduledat"], errors="coerce")
    else:
        df["d"] = pd.to_datetime(df["createdat"], errors="coerce")
    df = df.dropna(subset=["d"])
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_layout(title="Receita por mês"))
        return fig
    df["_m"] = df["d"].dt.to_period("M").astype(str)
    g = df.groupby("_m", as_index=False)["totalamount"].sum().rename(columns={"_m": "mes", "totalamount": "receita"})
    fig = px.area(g, x="mes", y="receita", markers=True)
    fig.update_traces(line_color=ACCENT, fillcolor="rgba(255,122,0,0.22)")
    fig.update_layout(**_layout(title="Receita por mês (pedidos concluídos)", yaxis_title="R$"))
    return fig


def fig_receita_por_loja(status16: pd.DataFrame, store: pd.DataFrame) -> go.Figure:
    agg = status16.groupby("storeid", as_index=False)["totalamount"].sum()
    if store is not None and not store.empty:
        st_map = store.drop_duplicates(subset=["id"]).copy()
        st_map["_sk"] = st_map["id"].astype(str)
        agg["_sk"] = agg["storeid"].astype(str)
        agg = agg.merge(st_map[["_sk", "name"]], on="_sk", how="left").drop(columns=["_sk"], errors="ignore")
        agg["nome"] = agg["name"].fillna(agg["storeid"].astype(str))
    else:
        agg["nome"] = agg["storeid"].astype(str)
    agg = agg.sort_values("totalamount", ascending=False).head(20)
    fig = px.bar(agg, x="totalamount", y="nome", orientation="h", text_auto=".2s")
    fig.update_layout(**_layout(title="Top 20 — receita por parceiro", yaxis_title="", xaxis_title="R$"))
    fig.update_traces(marker_color=ACCENT)
    return fig


def fig_pedidos_por_dia(storeorder: pd.DataFrame) -> go.Figure:
    df = storeorder.copy()
    if "scheduledat" in df.columns:
        df["d"] = pd.to_datetime(df["scheduledat"], errors="coerce")
    else:
        df["d"] = pd.to_datetime(df["createdat"], errors="coerce")
    df = df.dropna(subset=["d"])
    g = df.groupby(df["d"].dt.floor("D"), as_index=False).size()
    g.columns = ["dia", "pedidos"]
    fig = px.line(g, x="dia", y="pedidos", markers=True)
    fig.update_traces(line_color=CHART_2, marker=dict(size=5))
    fig.update_layout(**_layout(title="Pedidos por dia (todos os status)", yaxis_title="Pedidos"))
    return fig


def fig_cancelamentos_origem(
    cancel_store: float, cancel_cliente: float, cancel_timeout: float
) -> go.Figure:
    labels = ["Estabelecimento", "Cliente", "Expirado / timeout"]
    values = [cancel_store, cancel_cliente, cancel_timeout]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(line=dict(color=BORDER, width=2)),
                textinfo="percent+label",
                textposition="outside",
            )
        ]
    )
    fig.update_layout(**_layout(title="Cancelamento efetivo — % do universo por origem", showlegend=False))
    return fig


def fig_concentracao_canal(share_canal: pd.Series) -> go.Figure:
    df = share_canal.reset_index()
    df.columns = ["canal", "share"]
    df["share_pct"] = df["share"] * 100
    fig = px.treemap(df, path=["canal"], values="share_pct", color="share_pct", color_continuous_scale="Oranges")
    fig.update_layout(**_layout(title="Concentração de receita por canal"))
    return fig


def fig_curva_abc(share_loja_sorted: pd.Series) -> go.Figure:
    s = share_loja_sorted.cumsum() * 100
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=s.values,
            x=list(range(1, len(s) + 1)),
            fill="tozeroy",
            line=dict(color=ACCENT, width=2),
            name="% acumulado",
        )
    )
    fig.update_layout(
        **_layout(
            title="Curva ABC — receita acumulada por lojas (ordenadas)",
            xaxis_title="Ranking de lojas",
            yaxis_title="% receita acumulada",
        )
    )
    return fig


def fig_ticket_desconto(com_desc: float, sem_desc: float) -> go.Figure:
    df = pd.DataFrame(
        {
            "tipo": ["Com desconto", "Sem desconto"],
            "ticket": [float(com_desc) if pd.notna(com_desc) else 0, float(sem_desc) if pd.notna(sem_desc) else 0],
        }
    )
    fig = px.bar(df, x="tipo", y="ticket", text_auto=".2f")
    fig.update_traces(marker_color=[ACCENT, CHART_2])
    fig.update_layout(**_layout(title="Ticket médio — com vs sem desconto", yaxis_title="R$"))
    return fig


def fig_campanhas_funil(msg_enviadas: int, conv_atribuidas: int) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=["Mensagens enviadas (2)", "Conversões (4)"],
            y=[msg_enviadas, conv_atribuidas],
            marker_color=[ACCENT, CHART_4],
        )
    )
    fig.update_layout(**_layout(title="Campanhas — volume de mensagens e conversões", yaxis_title="Quantidade"))
    return fig


def fig_campanhas_top_parceiros(
    ranking: pd.DataFrame, n: int = 8, title: str = "Mensagens por parceiro (top)"
) -> go.Figure:
    """ranking: colunas `name`, `qtd_mensagens` (saída de campanhas_por_loja)."""
    if ranking is None or ranking.empty:
        fig = go.Figure()
        fig.update_layout(**_layout(title=title))
        return fig
    d = ranking.head(n).copy()
    d["nome"] = d["name"].fillna(d["storeid"].astype(str) if "storeid" in d.columns else "—")
    d = d.sort_values("qtd_mensagens", ascending=True)
    fig = px.bar(
        d,
        x="qtd_mensagens",
        y="nome",
        orientation="h",
        text_auto=True,
    )
    fig.update_traces(marker_color=ACCENT, textposition="outside")
    fig.update_layout(**_layout(title=title, xaxis_title="Mensagens", yaxis_title=""))
    return fig


def fig_heatmap_rf(status16: pd.DataFrame) -> go.Figure | None:
    """Heatmap semana x dia da semana (pedidos concluídos)."""
    df = status16.copy()
    if "scheduledat" in df.columns:
        df["d"] = pd.to_datetime(df["scheduledat"], errors="coerce")
    else:
        df["d"] = pd.to_datetime(df["createdat"], errors="coerce")
    df = df.dropna(subset=["d"])
    if df.empty:
        return None
    df["dow"] = df["d"].dt.day_name()
    df["week"] = df["d"].dt.to_period("W").astype(str)
    pivot = df.pivot_table(index="dow", columns="week", values="id", aggfunc="count", fill_value=0)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex([d for d in order if d in pivot.index])
    if pivot.shape[1] > 24:
        pivot = pivot.iloc[:, -24:]
    fig = px.imshow(
        pivot,
        labels=dict(x="Semana", y="Dia", color="Pedidos"),
        aspect="auto",
        color_continuous_scale="Blues",
    )
    fig.update_layout(**_layout(title="Mapa de calor — pedidos concluídos (dia × semana)"))
    return fig


def fig_health_gauge(score: int, title: str = "Health Score") -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=max(0, min(100, score)),
            number=dict(suffix="", font=dict(size=34, color="#101828")),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor=TEXT_MUTED, tickfont=dict(color=TEXT_MUTED)),
                bar=dict(color=ACCENT),
                bgcolor=MUTED,
                borderwidth=0,
                steps=[
                    dict(range=[0, 40], color="rgba(240,68,56,0.18)"),
                    dict(range=[40, 70], color="rgba(234,179,8,0.22)"),
                    dict(range=[70, 100], color="rgba(18,183,106,0.18)"),
                ],
            ),
            title=dict(text=title, font=dict(size=14, color="#101828")),
        )
    )
    fig.update_layout(**_layout(height=320, margin=dict(t=80, b=40)))
    return fig
