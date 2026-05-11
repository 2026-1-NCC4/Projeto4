import altair as alt

# ===========================
# GRaFICO LOJAS COM MAIOR FATURAMENTO
# ===========================
def LojaMaiorValor(df_filtrado):
    LojaMaiorValor = (
        df_filtrado
        .groupby('Nome_Loja')['totalamount']  # soma vendas por loja
        .sum()
        .sort_values(ascending=False)         # ordena do maior para o menor
        .head(10)                             # pega top 10 lojas
        .reset_index()
    )

    # cria gráfico de barras com Altair
    LojaMaiorValorChart = alt.Chart(LojaMaiorValor).mark_bar().encode(
        x=alt.X('Nome_Loja', sort=None),  # eixo X (nomes das lojas)
        y='totalamount'                   # eixo Y (valor total vendido)
    )

    return LojaMaiorValorChart


# ===========================
# GRaFICO: LOJAS COM MAIS VENDAS
# ===========================
def LojaMaiorQuantidade(df_filtrado):
    LojaMaiorQuantidade = (
        df_filtrado
        .groupby('Nome_Loja')['order_id']  # agrupa por loja
        .nunique()                         # conta vendas únicas
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    LojaMaiorQuantidadeChart = alt.Chart(LojaMaiorQuantidade).mark_bar(color='green').encode(
        x=alt.X('Nome_Loja', sort=None),  # nome da loja no eixo X
        y='order_id'                       # quantidade de vendas
    )

    return LojaMaiorQuantidadeChart


# ===========================
# GRaFICo MENSAGENS POR CAMPANHA
# ===========================
def MensagensPorCampanha(df_filtrado):

    mensagensporcampanha = (
        df_filtrado
        .groupby('campaignid')['message_id']  # agrupa por campanha
        .nunique()                           # conta mensagens únicas
        .reset_index()
        .sort_values(by='message_id', ascending=False)
    )

    # gráfico de barras com tooltip (info ao passar mouse)
    chart = alt.Chart(mensagensporcampanha).mark_bar(color='orange').encode(
        x=alt.X(
            'campaignid:N',  # N = categoria (texto)
            sort=None,
            title='Campanha'
        ),
        y=alt.Y(
            'message_id:Q',  # Q = número (quantitativo)
            title='Quantidade de Mensagens'
        ),
        tooltip=[
            'campaignid',   # mostra campanha
            'message_id'    # mostra quantidade
        ]
    )

    return chart


# ===========================
# GRÁFICO: TOP CAMPANHAS POR MENSAGENS
# ===========================
def LojaMaiorCampanhas(df_filtrado):

    LojaMaiorCampanhas = (
        df_filtrado
        .groupby('campaignid')['message_id']
        .nunique()
        .reset_index(name='Quantidade_Mensagens')
        .sort_values(by='Quantidade_Mensagens', ascending=False)
        .head(10)
    )

    chart = alt.Chart(LojaMaiorCampanhas).mark_bar(color='red').encode(
        x=alt.X(
            'campaignid:N',
            sort=None,
            title='Campanhas'
        ),
        y=alt.Y(
            'Quantidade_Mensagens:Q',
            title='Mensagens'
        ),
        tooltip=[
            'campaignid',
            'Quantidade_Mensagens'
        ]
    )

    return chart