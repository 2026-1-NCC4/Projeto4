# dependências
import streamlit as st
import pandas as pd

# arquivos
import cards
import funcs
import menu

#cache no streamlit que faz não carregar por 100 milhões de anos um calculo sempre que atualiza 
#  >:(
@st.cache_data
def carregar_dados():
    return {
        "store": pd.read_csv("dados/STORE.csv"),
        "customer": pd.read_csv("dados/CUSTOMER.CSV"),
        "storeorder": pd.read_csv("dados/STOREORDER.csv"),
        "customeraddress": pd.read_csv("dados/CUSTOMERADDRESS.CSV"),
        "campaign": pd.read_csv("dados/CAMPAIGN.CSV"),
        "campaignxorder": pd.read_csv("dados/CAMPAIGNxORDER.CSV"),
    }

dados = carregar_dados()

store = dados["store"]
customer = dados["customer"]
storeorder = dados["storeorder"]


periodo, restaurante, df_loja = menu.render_header(store, storeorder)

# FILTRO
df_filtrado = funcs.filtrar_periodo(df_loja, periodo, 'createdat')

# SIDEBAR
menu.render_sidebar()

# CÁLCULOS
receita = funcs.receita_total(df_filtrado)
total_vendas = funcs.total_pedidos(df_filtrado)
ticket_medio_valor = funcs.ticket_medio(df_filtrado, receita)
clientesTot = funcs.clientes_ativos(df_loja, customer, periodo)

# FORMATADOS
receita_formatada = funcs.formatar_moeda(receita)
ticket_formatado = funcs.formatar_moeda(ticket_medio_valor)

# LAYOUT
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    cards.card_valor("Receita Total", receita_formatada, "+12.5% vs mês anterior", True)

with col2:
    cards.card_valor("Total Vendas", f"{total_vendas}", "+15.2% melhoria trimestral", True)

with col3:
    cards.card_valor("Ticket Médio", ticket_formatado, "-2.3% vs semana anterior", False)

with col4:
    cards.card_valor("Clientes Ativos", clientesTot, "+8.7% vs mês anterior", True)

# GRÁFICO
df_mes = funcs.valor_per_mes(df_filtrado, periodo)

st.markdown("### Receita por Mês")
st.caption("Evolução da receita ao longo do tempo")

grafico = funcs.grafico_receita_mensal(df_mes)

st.altair_chart(grafico, use_container_width=True)

st.sidebar.image("imagens/cat.gif")