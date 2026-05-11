import streamlit as st
import tratamento
import graficos

# Função para formatar valores em padrão de moeda brasileira
def valor_formatado(valor):
    valor_formatado = f"R$ {valor:,.2f}" \
        .replace(",", "X") \
        .replace(".", ",") \
        .replace("X", ".")
    return valor_formatado


# Título da barra lateral
st.sidebar.title("Lojas")

# Lista de opções: todas as lojas + lojas existentes no dataset
opcoes = ['Todas as lojas'] + tratamento.lojas

# Selectbox para escolher a loja
loja_selecionada = st.sidebar.selectbox(
    "Escolha uma loja",
    opcoes
)

# Filtra os dados conforme a loja selecionada
if loja_selecionada == 'Todas as lojas':
    df_filtrado = tratamento.dfCxOLJ
else:
    df_filtrado = tratamento.dfCxOLJ[tratamento.dfCxOLJ['Nome_Loja'] == loja_selecionada]

# Define o título principal do dashboard
if loja_selecionada == 'Todas as lojas':
    st.title("Análise de Vendas das Campanhas")
else:
    st.title(f"{loja_selecionada}")

# Soma o valor total de vendas (sem duplicar pedidos)
valor_total = (
    df_filtrado
    .drop_duplicates(subset='order_id')['totalamount']
    .sum()
)

# ===========================
# DASHBOARD - TODAS AS LOJAS
# ===========================
if loja_selecionada == 'Todas as lojas':
    # Cria colunas para métricas
    venda1, venda2, mensagens1 = st.columns(3)
    valor1, valor2= st.columns(2)
    conversao1, conversao2 = st.columns(2)
    # Métricas gerais do dataset inteiro
    venda1.metric("Vendas Totais das Campanhas", f"{tratamento.total_vendas_campanha}")
    valor1.metric("Valor das Vendas das Campanhas", f"{valor_formatado(tratamento.total_valor_campanhas)}")
    mensagens1.metric("Mensagens Totais", f"{tratamento.total_mensagens:,.0f}")
    venda2.metric("Vendas Totais Lojas", f"{tratamento.total_vendas}")
    valor2.metric("Valor das Vendas Lojas", f"{valor_formatado(tratamento.total_valor_storeorder)}")
    conversao1.metric("Taxa de Conversão", f"{tratamento.taxa_conversao:,.2f}%")
    conversao2.metric("Taxa de conversão por Valor", f"{tratamento.taxa_conversao_valor:,.2f}%")

# ===========================
# DASHBOARD - LOJA ESPECÍFICA
# ===========================
else:
    # Cria colunas para métricas da loja selecionada
    venda1, valor1, mensagens1 = st.columns(3)
    campanhas1, vendas2, conversao1 = st.columns(3)

    # Quantidade de vendas únicas
    if df_filtrado['order_id'].nunique() == 0:
        venda1.metric("Vendas", "0 ou N/A")
    else:
        venda1.metric("Quantidade de Vendas", f"{df_filtrado['order_id'].nunique():,.0f}")

    # Total de mensagens enviadas
    if df_filtrado['message_id'].nunique() == 0:
        mensagens1.metric("Mensagens", "0 ou N/A")
    else:
        mensagens1.metric("Total Mensagens", f"{df_filtrado['message_id'].count():,.0f}")

    # Faturamento da loja
    if valor_total == 0:
        valor1.metric("Faturamento", "0 ou N/A")
    else:
        valor1.metric("Faturamento do Estabelecimento", f"{valor_total:,.2f} R$")

    # Taxa de conversão (vendas da loja / total geral)
    if valor_total == 0:
        conversao1.metric("Taxa de conversão", "0 ou N/A")
    else:
        conversao1.metric(
            "Taxa de conversão",
            f"{((df_filtrado['order_id'].nunique() / tratamento.total_vendas) * 100):.2f} %"
        )

    # Total de campanhas na loja
    if valor_total == 0:
        campanhas1.metric("Campanhas", "0 ou N/A")
    else:
        campanhas1.metric("Total de Campanhas", f"{df_filtrado['campaignid'].nunique()}")

        # Gráfico de mensagens por campanha
        chart_mensagens = graficos.MensagensPorCampanha(df_filtrado)
        st.header("Mensagens por Campanha")
        st.altair_chart(chart_mensagens, use_container_width=True)

        # Tabela auxiliar do gráfico
        st.header("Tabela auxiliar")
        mensagens_por_campanha = (
            df_filtrado.groupby('campaignid')['message_id']
            .nunique()
            .reset_index(name='Quantidade_Mensagens')
        )
        st.dataframe(mensagens_por_campanha)

# ===========================
# GRÁFICOS (TODAS AS LOJAS)
# ===========================
if loja_selecionada == 'Todas as lojas':

    # Criação dos gráficos principais
    LojaMaiorValorChart = graficos.LojaMaiorValor(df_filtrado)
    LojaMaiorQuantidadeChart = graficos.LojaMaiorQuantidade(df_filtrado)
    LojaMaiorCampanhasChart = graficos.LojaMaiorCampanhas(df_filtrado)

    # Exibição dos gráficos
    st.subheader("Lojas com maior Valor em vendas")
    st.altair_chart(LojaMaiorValorChart, use_container_width=True)

    st.subheader("Lojas com maior Quantidade de vendas")
    st.altair_chart(LojaMaiorQuantidadeChart, use_container_width=True)

    st.subheader("Top 10 Campanhas com mais Mensagens")
    st.altair_chart(LojaMaiorCampanhasChart, use_container_width=True)

# ===========================
# TABELA FINAL
# ===========================
if loja_selecionada == "Todas as lojas":
    st.dataframe(df_filtrado)
else:
    st.header("Tabela de dados da loja")
    st.dataframe(df_filtrado)