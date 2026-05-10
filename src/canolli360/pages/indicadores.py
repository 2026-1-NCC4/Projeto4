import streamlit as st
import pandas as pd
import numpy as np

# importando o menu
import menu
import funcs

store = pd.read_csv("dados/STORE.csv", sep=",")
customer = pd.read_csv("dados/CUSTOMER.CSV", sep=",")
storeorder = pd.read_csv("dados/STOREORDER.csv", sep=",")
customeraddress = pd.read_csv("dados/CUSTOMERADDRESS.CSV", sep=",")
campaign = pd.read_csv("dados/CAMPAIGN.CSV", sep=",")
campaignxorder = pd.read_csv("dados/CAMPAIGNxORDER.CSV", sep=",")


status16 = storeorder[storeorder['status'] == 16]
# renderização do menu
periodo, restaurante, df_loja = menu.render_header(store, storeorder)
menu.render_sidebar()


st.title("Demonstração dos índices")

st.header("1.0 - Estrutura de receita")

#region 1.1

st.subheader("**1.1** - ***Decomposição da Receita Repostara:***")

subtotal = status16['subtotalamount'].sum()
st.markdown(f"**Subtotal dos pedidos concluídos**: {funcs.formatar_moeda(subtotal)}")

descontos = status16['discountamount'].sum()
st.markdown(f"**Total de descontos aplicados aos pedidos concluídos**: {funcs.formatar_moeda(descontos)}")

impostos = status16['taxamount'].sum()
st.markdown(f"**Total de impostos aplicados aos pedidos concluídos**: {funcs.formatar_moeda(impostos)}")

receita = status16['totalamount'].sum()
st.markdown(f"**Receita total dos pedidos concluídos**: {funcs.formatar_moeda(receita)}")

porcent_subtotal = (subtotal/receita)*100
st.markdown(f"**Porcentagem do total da receita**: {porcent_subtotal:.2f}%")

porcent_impostos = (impostos/receita)*100
st.markdown(f"**Porcentagem de impostos dos pedidos concluídos sobre receita**: {porcent_impostos:.2f}%")

#endregion

st.markdown("---")

#region 1.2

st.subheader("**1.2** - ***Receita Líquida Comercial:***")

rlc = subtotal - descontos
st.markdown(f"**Receita Líquida Comercial**: {funcs.formatar_moeda(rlc)}")

desconto_subtotal = (descontos/subtotal)*100
st.markdown(f"**Taxa de desconto sobre subtotal**: {desconto_subtotal:.2f}%")

#endregion

st.markdown("---")

#region 1.3

st.subheader("**1.3** - ***Taxa de Realização da Receita:***")

qnt_pedido = len(status16)
ticket_medio = receita / qnt_pedido
universo = len(storeorder)
receita_pot = universo * ticket_medio
st.markdown(f"**Receita Potêncial**: {funcs.formatar_moeda(receita_pot)}")

st.markdown(f"**Receita Realizada**: {funcs.formatar_moeda(receita)}")

taxa_realizar = (receita / receita_pot) * 100
st.markdown(f"**Taxa de realização**: {taxa_realizar:.2f}%")

#endregion

st.markdown("---")

#region 1.4

st.subheader("**1.4** - ***Custo de Oportunidade dos Não-Concluídos***")

n_concluido = universo - qnt_pedido
st.markdown(f"**Pedidos não realizados**: {n_concluido} pedidos")

n_receita = n_concluido * ticket_medio
st.markdown(f"**Receita não realizada**: {funcs.formatar_moeda(n_receita)}")

porc_receita = (n_receita / receita) * 100
st.markdown(f"**Procentagem sobre Receita Realizada**: {porc_receita:.2f}%")

#endregion

st.markdown("---")


st.header("**2.0 - Cancelamento e Qualidade**")

#region 2.1

st.subheader("**2.1** - ***Taxa de Cancelamento Efetivo***")

status8 = storeorder[storeorder['status'] == 8]
status11 = storeorder[storeorder['status'] == 11]
status14 = storeorder[storeorder['status'] == 14]
cancel_efetivos = len(status8) + len(status11) + len(status14)
st.markdown(f"**Cancelamentos efetivos**: {cancel_efetivos} pedidos")

st.markdown(f"**Universo total**: {universo} pedidos")

taxa_cancel = (cancel_efetivos / universo) * 100
st.markdown(f"**Taxa de Cancelamento**: {taxa_cancel:.2f}%")

#endregion

st.markdown("---")

#region 2.2

st.subheader("**2.2** - ***Decomposição do Cancelamento por Origem***")

cancel_store = (len(status8) / universo) * 100
st.markdown(f"**Cancelamento pelo estabeleciemnto**: {cancel_store:.2f}%")

cancel_cliente = (len(status11) / universo) * 100
st.markdown(f"**Cancelamento pelo cliente**: {cancel_cliente:.2f}%")

cancel_timeout = (len(status14) / universo) * 100
st.markdown(f"**Expirado/Timeout**: {cancel_timeout:.2f}%")

#endregion

st.markdown("---")

#region 2.3

st.subheader("**2.3** - ***Receita Perdida por Cancelamento Efetivo***")

st.markdown(f"**Cancelamentos efetivos**: {cancel_efetivos} pedidos")

receita_perdida = cancel_efetivos * ticket_medio
st.markdown(f"**Receita perdida**: {funcs.formatar_moeda(receita_perdida)}")

porc_receita_perdida = (receita_perdida / receita) * 100
st.markdown(f"**Porcentagem sobre Receita Realizada**: {porc_receita_perdida:.2f}%")

#endregion

st.markdown("---")


st.header("**3.0 - Eficiência e Produtividade**")

#region 3.1

st.subheader("**3.1** - ***Taxa de Ativação por Loja***")

lojas = len(store['id'])
st.markdown(f"**Lojas cadastradas**: {lojas} lojas")

loja_ativa = len(status16['storeid'].unique())
st.markdown(f"**Lojas ativas**: {loja_ativa} lojas")

taxa_ativa = (loja_ativa / lojas) * 100
st.markdown(f"**Taxa de Ativação**: {taxa_ativa:.2f}%")

#endregion

st.markdown("---")

#region 3.2

st.subheader("**3.2** - ***Receita Média por Loja Ativa***")

st.markdown(f"**Receita total**: {funcs.formatar_moeda(receita)}")

st.markdown(f"**Lojas ativas**: {loja_ativa} lojas")

rec_loja_ativa = receita / loja_ativa
st.markdown(f"**Receita por loja ativa**: {funcs.formatar_moeda(rec_loja_ativa)}")

receita_mensal = rec_loja_ativa / 9
st.markdown(f"**Receita mensal média por loja**: {funcs.formatar_moeda(receita_mensal)}")

#endregion

st.markdown("---")

#region 3.3

st.subheader("**3.3** - ***Média Diária da Operação***")

storeorder['scheduledat'] = pd.to_datetime(storeorder['scheduledat'], format='ISO8601')
periodo_dia = (
    storeorder['scheduledat'].max() - storeorder['scheduledat'].min()
).days + 1
st.markdown(f"**Período**: {periodo_dia} dias")

receita_dia = receita / periodo_dia
st.markdown(f"**Receita ao dia**: {funcs.formatar_moeda(receita_dia)}")

pedido_dia = qnt_pedido / periodo_dia
st.markdown(f"**Pedidos ao dia**: {pedido_dia:.0f} pedidos")

#endregion

st.markdown("---")

#region 3.4

st.subheader("**3.4** - ***Volume Médio por Loja Ativa***")

pedidos_loja = qnt_pedido / loja_ativa
st.markdown(f"**Pedidos por loja ativa**: {pedidos_loja:.0f} pedidos")

pedidos_mes = pedidos_loja / 9
st.markdown(f"**Pedidos por loja ao mês**: {pedidos_mes:.0f} pedidos/mês")

#endregion

st.markdown("---")

#region 3.5

st.subheader("**3.5** - ***ARPU - Receita Média por Cliente***")

cliente_concluido = len(status16['customerid'].unique())
st.markdown(f"**Clientes com pedido concluído**: {cliente_concluido} pessoas")

arpu = receita / cliente_concluido
st.markdown(f"**ARPU**: {funcs.formatar_moeda(arpu)}")

#endregion

st.markdown("---")


st.header("**4.0 - Concentração e Risco**")

#region 4.1

st.subheader("**4.1** - ***Concentração por Canal de Venda***")

share_canal = status16.groupby('saleschannel')['totalamount'].sum()
share_canal = share_canal / share_canal.sum()
hhi_canal = ((share_canal ** 2).sum()) * 10000
st.markdown(f"**HHI (Canal)**: {hhi_canal:.0f}")

max_share_canal = share_canal.max() * 100
maior_canal = share_canal.idxmax()
st.markdown(f"**Maior canal**: {maior_canal} = {max_share_canal:.2f}%")

st.markdown(f"**Verificação parcial do maior canal**: {(max_share_canal ** 2):.0f}")

if hhi_canal < 1500:
    st.markdown("**Classificação**: Desconcentração")
elif hhi_canal >= 1500 and hhi_canal < 2500:
    st.markdown("**Classificação**: Moderada")
elif hhi_canal >= 2500 and hhi_canal < 5000:
    st.markdown("**Classificação**: Alta")
elif hhi_canal >= 5000:
    st.markdown("**Classificação**: Monopólio Efetivo")

#endregion

st.markdown("---")

#region 4.2

st.subheader("**4.2** - ***Concentração por Loja***")

share_loja = status16.groupby('storeid')['totalamount'].sum()
share_loja = share_loja / share_loja.sum()
hhi_loja = ((share_loja ** 2).sum()) * 10000
st.markdown(f"**HHI (Loja)**: {hhi_loja:.0f}")

max_share_loja = share_loja.max() * 100
maior_loja = share_loja.idxmax()
maior_loja = store.loc[store['id'] == maior_loja, 'name'].values[0]
st.markdown(f"**Maior canal**: {maior_loja} = {max_share_loja:.2f}%")

st.markdown(f"**Verificação parcial da maior loja**: {(max_share_loja ** 2):.0f}")

if hhi_loja < 1500:
    st.markdown("**Classificação**: Desconcentração")
elif hhi_loja >= 1500 and hhi_canal < 2500:
    st.markdown("**Classificação**: Moderada")
elif hhi_loja >= 2500 and hhi_canal < 5000:
    st.markdown("**Classificação**: Alta")
elif hhi_loja >= 5000:
    st.markdown("**Classificação**: Monopólio Efetivo")

#endregion

st.markdown("---")

#region 4.3

st.subheader("**4.3** - ***Curva ABS da Receita por Loja***")

share_ordenado = share_loja.sort_values(ascending=False)
top1 = share_ordenado.head(1)
top1 = top1.sum() * 100
st.markdown(f"**Top 1 loja**: {top1:.2f}%")

top4 = share_ordenado.head(4)
top4 = top4.sum() * 100
st.markdown(f"**Top 4 lojas**: {top4:.2f}%")

top10 = share_ordenado.head(10)
top10 = top10.sum() * 100
st.markdown(f"**Top 10 lojas**: {top10:.2f}%")

def top20_percent(share, valor):
    share_ordenado = share.sort_values(ascending=False)
    percent = max(1, int(len(share_ordenado) * valor))
    return share_ordenado.head(percent).sum() * 100
top20_porc = top20_percent(share_loja, 0.2)
st.markdown(f"**Top 20% lojas**: {top20_porc:.2f}%")

#endregion

st.markdown("---")

#region 4.4

st.subheader("**4.4** - ***Coeficiente de Gini de Receita por Loja***")

receita_loja = share_loja.sort_values()
valores = receita_loja.values
n = len(valores)
gini = (2 * np.sum((np.arange(1, n+1) * valores))) / (n * np.sum(valores)) - (n + 1) / n
st.markdown(f"**Gini das lojas**: {gini:.3f}")

if gini < 0.5:
    st.markdown(f"**Interpretação**: Desigualdade Baixa")
elif 0.5 <= gini <= 0.7:
    st.markdown(f"**Interpretação**: Desigualdade Alta")
else:
    st.markdown(f"**Interpretação**: Desigualdade Muito ALta")

#endregion

st.markdown("---")


st.header("**5.0 - Indicadores Promocionais**")

#region 5.1

st.subheader("**5.1** - ***Investimento Promocional como Porcentagem da Receita***")

invest_promo = status16['discountamount'].sum()
st.markdown(f"**Investimento Promocional**: {funcs.formatar_moeda(invest_promo)}")

ip_receita = (invest_promo / receita) * 100
st.markdown(f"**Porcentagem sobre Receita Total**: {ip_receita:.2f}%")

ip_subtotal = (invest_promo / subtotal) * 100
st.markdown(f"**Porcentagem sobre Subtotal**: {ip_subtotal:.2f}%")

#endregion

st.markdown("---")

#region 5.2

st.subheader("**5.2** - ***Profundidade Média do Desconto***")

pedidos_descont = status16.loc[status16['discountamount'] > 0, 'discountamount'].count()
st.markdown(f"**Pedidos com desconto**: {pedidos_descont} pedidos")

pedidos_benef = (pedidos_descont / qnt_pedido) * 100
st.markdown(f"**Pedidos Beneficiados**: {pedidos_benef:.2f}%")

subtotal_benef = status16.loc[status16['discountamount'] > 0, 'subtotalamount'].sum()
st.markdown(f"**Subtotal dos beneficiados**: {funcs.formatar_moeda(subtotal_benef)}")

prof_media = (invest_promo / subtotal_benef) * 100
st.markdown(f"**Profundidade Média**: {prof_media:.2f}%")

dma = invest_promo / pedidos_descont
st.markdown(f"**Desconto Médio Absoluto**: {funcs.formatar_moeda(dma)}")

#endregion

st.markdown("---")

#region 5.3

st.subheader("**5.3** - ***Análise de Uplift — Ticket COM e SEM Desconto***")

com_desc = status16.loc[status16['discountamount'] > 0, 'totalamount'].mean()
st.markdown(f"**Pedidos com desconto**: {funcs.formatar_moeda(com_desc)}")

sem_desc = status16.loc[status16['discountamount'] == 0, 'totalamount'].mean()
st.markdown(f"**Pedidos sem desconto**: {funcs.formatar_moeda(sem_desc)}")

uplift = ((com_desc - sem_desc) / sem_desc) * 100
st.markdown(f"**Uplift do ticket**: {uplift:.2f}%")

if uplift < 0:
    st.markdown("**Interpretação**: Negativo")
else:
    st.markdown("**Interpretação**: Positivo")

#endregion

st.markdown("---")

#region 5.4

st.subheader("**5.4** - ***Custo Promocional por Pedido Beneficiado***")

custo_pedido_geral = invest_promo / pedidos_descont
st.markdown(f"**Custo do pedido com desconto**: {funcs.formatar_moeda(custo_pedido_geral)}")

custo_pedido = invest_promo / qnt_pedido
st.markdown(f"**Custo do pedido no geral**: {funcs.formatar_moeda(custo_pedido)}")

cpd = custo_pedido_geral - custo_pedido
st.markdown(f"**Custo Promocional Diluído**: {funcs.formatar_moeda(cpd)}")

#endregion

st.markdown("---")

#region 5.5

st.subheader("**5.5** - ***Receita Atribuída às Campanhas***")

status2 = campaignxorder[campaignxorder['status'] == 2]
msg_enviadas = status2['message_id'].count()
st.markdown(f"**Menagens enviadas**: {msg_enviadas} mensagens")

status4 = campaignxorder[campaignxorder['status'] == 4]
conv_atribuidas = status4['message_id'].count()
st.markdown(f"**Menagens enviadas**: {conv_atribuidas} conversões")

tax_conver = (conv_atribuidas / msg_enviadas) * 100
st.markdown(f"**Taxa de conversão**: {tax_conver:.2f}%")

rec_atribuida = status4['totalamount'].sum()
st.markdown(f"**Receita atribuída**: {funcs.formatar_moeda(rec_atribuida)}")

porc_rec_atrib = (rec_atribuida / receita) * 100
st.markdown(f"**Porcentagem sobre receita total**: {porc_rec_atrib:.2f}%")

receita_msg = rec_atribuida / msg_enviadas
st.markdown(f"**Receita por mensagem convertida**: {funcs.formatar_moeda(receita_msg)}")

#endregion

st.markdown("---")

st.header("**6.0 - Crescimento e Sazonalidade**")

#region 6.1

status16['scheduledat'] = pd.to_datetime(status16['scheduledat'], format='ISO8601')
status16['ano_mes'] = status16['scheduledat'].dt.to_period('M')
mes_inicio = status16['ano_mes'].min()
receita_inicio = status16.loc[status16['ano_mes'] == mes_inicio, 'totalamount'].sum()
st.markdown(f"**Receita até 2022**: {funcs.formatar_moeda(receita_inicio)}")

#endregion