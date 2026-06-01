import pandas as pd
import altair as alt
import numpy as np

def grafico_receita_mensal(df):
    """Gera o gráfico Altair de receita mensal por linha com pontos."""
    df = df.copy()
    df['createdat'] = pd.to_datetime(df['createdat'], errors='coerce')
    
    df = (
        df.set_index('createdat')
        .resample('ME')['totalamount']
        .sum()
        .reset_index()
    )

    chart = (
        alt.Chart(df)
        .mark_bar(point=True, color='#ff7a00', 
                  opacity=0.8, 
                  width=45, 
                  cornerRadiusTopLeft=10, 
                  cornerRadiusTopRight=10,
                  cursor='pointer',
        )
        .encode(
            x='createdat:T',
            y='totalamount:Q',
            tooltip=['createdat:T', 'totalamount:Q']
        )
    )
    return chart



ValorGraficoML=20

dados = pd.DataFrame({"ValorGraficoML": [ValorGraficoML]})

grafico=alt.Chart(dados).mark_arc(

    innerRadius=130, 
    outerRadius=150,
    color="#ff7a00"

    ).encode(
    theta=alt.value(-np.pi/2),  # Começa na esquerda (-90°)
    # Calcula dinamicamente o ponto de parada baseado no slider
    theta2=alt.value(-np.pi / 2 + (ValorGraficoML / 100) * np.pi)
).properties(
    width=300, height=500
)


grafico2=alt.Chart(dados).mark_arc(
    innerRadius=115, 
    outerRadius=165,
    color="#f2d4d5",

    ).encode(
    theta=alt.value(-np.pi/2),  # Começa na esquerda (-90°)
    # Calcula dinamicamente o ponto de parada baseado no slider
    theta2=alt.value(-np.pi/2 + (0.4 * np.pi))
).properties(
    width=300, height=500
)

grafico3=alt.Chart(dados).mark_arc(
    innerRadius=115, 
    outerRadius=165,
    color="#f0e6c2",
    

    ).encode(
    theta=alt.value(-np.pi/2 + (0.4 * np.pi)),
    # Calcula dinamicamente o ponto de parada baseado no slider
    theta2=alt.value(-np.pi/2 + (0.7 * np.pi))
).properties(
    width=300, height=500
)




grafico4=alt.Chart(dados).mark_arc(
    innerRadius=115, 
    outerRadius=165,
    color="#cae9de",

    ).encode(
    theta=alt.value(-np.pi/2 + (0.7 * np.pi)),
    # Calcula dinamicamente o ponto de parada baseado no slider
    theta2=alt.value(np.pi/2)
).properties(
    width=300, height=500
)


texto = alt.Chart(
        pd.DataFrame({
            "x":[0],
            "y":[0],
            "txt":[f"{ValorGraficoML}"]
        })


    ).mark_text(
        fontSize=30

    ).encode(
        x=alt.X("x", axis=None),
        y=alt.Y("y", axis=None),
        text="txt"
    )


grafico_final = texto + grafico2 + grafico3 + grafico4 + grafico 



# ── gráficos Altair para campanhas ─────────────────────────────────────────

def _altair_barras_h(
    df: pd.DataFrame,
    col_label: str,
    col_valor: str,
    titulo: str,
    cor: str = "#7F77DD",
    formato_valor: str = ".1f",
    sufixo: str = "%",
) -> alt.Chart:
    """Gráfico de barras horizontais Altair genérico para rankings de campanha."""
    df = df.copy()
    df[col_label] = df[col_label].astype(str).str[:30]
    chart = (
        alt.Chart(df, title=titulo)
        .mark_bar(color=cor, cornerRadiusEnd=4)
        .encode(
            x=alt.X(col_valor, title=None, axis=alt.Axis(grid=False, labels=False, ticks=False)),
            y=alt.Y(col_label, sort="-x", title=None, axis=alt.Axis(labelLimit=160)),
            tooltip=[
                alt.Tooltip(col_label, title="Campanha"),
                alt.Tooltip(col_valor, title=titulo, format=formato_valor),
            ],
        )
        .properties(height=180)
        .configure_view(strokeWidth=0)
        .configure_axis(labelFontSize=12, domainWidth=0)
        .configure_title(fontSize=13, anchor="start", fontWeight=500)
    )
    return chart


def graf_top5_taxa_conversao(df_ranking: pd.DataFrame) -> alt.Chart:
    """Top 5 campanhas por taxa de conversão (barras horizontais, roxo)."""
    top = df_ranking.nlargest(5, "taxa_conversao")[["name", "taxa_conversao"]].copy()
    return _altair_barras_h(top, "name", "taxa_conversao", "Top 5 — maior taxa de conversão", "#7F77DD", ".1f", "%")


def graf_bottom5_taxa_conversao(df_ranking: pd.DataFrame) -> alt.Chart:
    """Bottom 5 campanhas por taxa de conversão (barras horizontais, vermelho)."""
    bot = df_ranking.nsmallest(5, "taxa_conversao")[["name", "taxa_conversao"]].copy()
    return _altair_barras_h(bot, "name", "taxa_conversao", "Bottom 5 — menor taxa de conversão", "#E24B4A", ".1f", "%")


def graf_top5_receita(df_ranking: pd.DataFrame) -> alt.Chart:
    """Top 5 campanhas por receita atribuída (barras horizontais, verde)."""
    top = df_ranking.nlargest(5, "receita_conv")[["name", "receita_conv"]].copy()
    return _altair_barras_h(top, "name", "receita_conv", "Top 5 — maior receita atribuída", "#1D9E75", ",.0f", "")


def graf_bottom5_receita(df_ranking: pd.DataFrame) -> alt.Chart:
    """Bottom 5 campanhas por receita atribuída (barras horizontais, laranja)."""
    bot = df_ranking.nsmallest(5, "receita_conv")[["name", "receita_conv"]].copy()
    return _altair_barras_h(bot, "name", "receita_conv", "Bottom 5 — menor receita atribuída", "#BA7517", ",.0f", "")


def graf_mensagens_por_loja(df_lojas: pd.DataFrame) -> alt.Chart:
    """Barras horizontais: mensagens enviadas por loja."""
    df = df_lojas.groupby("nome_loja", as_index=False)["n_enviadas"].sum()
    df = df.sort_values("n_enviadas", ascending=False).head(15)
    return _altair_barras_h(df, "nome_loja", "n_enviadas", "Mensagens enviadas por loja", "#7F77DD", ",.0f", "")


def graf_conversao_por_loja(df_lojas: pd.DataFrame) -> alt.Chart:
    """Barras horizontais: taxa de conversão média por loja."""
    df = (
        df_lojas.groupby("nome_loja", as_index=False)
        .apply(lambda g: pd.Series({
            "taxa_conversao": (g["n_conversoes"].sum() / g["n_enviadas"].sum() * 100)
            if g["n_enviadas"].sum() > 0 else 0.0
        }))
        .reset_index(drop=True)
    )
    df = df.sort_values("taxa_conversao", ascending=False).head(15)
    return _altair_barras_h(df, "nome_loja", "taxa_conversao", "Taxa de conversão por loja", "#1D9E75", ".1f", "%")
