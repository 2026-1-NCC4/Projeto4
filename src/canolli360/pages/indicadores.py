import streamlit as st
import pandas as pd
import numpy as np

# importando o menu
import menu
import funcs


if "logado" not in st.session_state or not st.session_state.logado:
    st.error("Acesso negado! Por favor, faça o login primeiro.")
    st.stop()

store = pd.read_csv("dados/STORE.csv", sep=",")
customer = pd.read_csv("dados/CUSTOMER.CSV", sep=",")
storeorder = pd.read_csv("dados/STOREORDER.csv", sep=",")
customeraddress = pd.read_csv("dados/CUSTOMERADDRESS.CSV", sep=",")
campaign = pd.read_csv("dados/CAMPAIGN.CSV", sep=",")
campaignxorder = pd.read_csv("dados/CAMPAIGNxORDER.CSV", sep=",")


status16 = storeorder[storeorder['status'] == 16]
# renderização do menu
periodo, restaurante, canal, pedido, df_loja = menu.render_header(store, storeorder)
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


st.header("**7.0 - Recorrência e Valor do Cliente**")

#region 7.1

st.subheader("**7.1** - ***Taxa de Recorrência***")

st.markdown(f"**Clientes com pedido concluído**: {cliente_concluido} pessoas")

pedido_cliente = status16.groupby('customerid')['id'].count()
recorrentes_index = (pedido_cliente[pedido_cliente > 1])
recorrentes = recorrentes_index.count()
st.markdown(f"**Clientes recorrentes**: {recorrentes} pessoas")

taxa_recorrencia = (recorrentes / cliente_concluido) * 100
st.markdown(f"**Taxa de Recorrência**: {taxa_recorrencia:.2f}%")

#endregion

st.markdown("---")

#region 7.2

st.subheader("**7.2** - ***Participação dos Recorrentes na Receita***")

recorrente_receita = status16.loc[status16['customerid'].isin(recorrentes_index.index), 'totalamount'].sum()
st.markdown(f"**Receita dos clientes recorrentes**: {funcs.formatar_moeda(recorrente_receita)}")

percent_recorrentes = (recorrente_receita / receita) * 100
st.markdown(f"**Porcentagem sobre receita total**: {percent_recorrentes:.2f}%")

nrecorrente_receita = receita - recorrente_receita
st.markdown(f"**Receita dos clientes não recorrentes**: {funcs.formatar_moeda(nrecorrente_receita)}")

percent_nrecorentes = (nrecorrente_receita / receita) * 100
st.markdown(f"**Porcentagem sobre receita total**: {percent_nrecorentes:.2f}%")

#endregion

st.markdown("---")

#region 7.3

st.subheader("**7.3** - ***Frequência Média de Compra***")

tds_pedido_cliente = qnt_pedido / cliente_concluido
st.markdown(f"**Frequência média de compra por cliente**: {tds_pedido_cliente:.2f} pedidos/cliente")

nrecorrente = cliente_concluido - recorrentes
tds_pedido_nrecorente = (qnt_pedido - nrecorrente) / recorrentes
st.markdown(f"**Frequência média de compra por cliente recorrente**: {tds_pedido_nrecorente:.2f} pedidos/cliente recorrente")

#endregion

st.markdown("---")

#region 7.4

st.subheader("**7.4** - ***ARPU Diferenciado***")

arpu_recorrente = recorrente_receita / recorrentes
st.markdown(f"**ARPU dos clientes recorrentes**: {funcs.formatar_moeda(arpu_recorrente)}")

arpu_nrecorrente = nrecorrente_receita / nrecorrente
st.markdown(f"**ARPU dos clientes não recorrentes**: {funcs.formatar_moeda(arpu_nrecorrente)}")

multiplicador_arpu = arpu_recorrente / arpu_nrecorrente
st.markdown(f"**Multiplicador de ARPU**: {multiplicador_arpu:.2f}x")

#endregion

st.markdown("---")


st.header("**8.0 - Margem e Ponto de Equilibrio**")

#region 8.1

st.subheader("**8.1** - ***Margem de Contribuição Estimada***")

st.markdown(f"**Receita Total**: {funcs.formatar_moeda(receita)}")

cmv = receita * 0.32
st.markdown(f"**CMV estimado**: {funcs.formatar_moeda(cmv)}")

comissao = receita * 0.18
st.markdown(f"**Comissão estimada**: {funcs.formatar_moeda(comissao)}")

op_variavel = receita * 0.08
st.markdown(f"**Operação variável estimada**: {funcs.formatar_moeda(op_variavel)}")

margem_contrib = receita - cmv - comissao - op_variavel
st.markdown(f"**Margem de contribuição estimada**: {funcs.formatar_moeda(margem_contrib)}")

porcent_margem = (margem_contrib / receita) * 100
st.markdown(f"**Porcentagem da margem sobre receita**: {porcent_margem:.2f}%")

#endregion

st.markdown("---")

#region 8.2

st.subheader("**8.2** - ***DRE Gerencial Sintético***")

st.markdown(f"**Receita Total**: {funcs.formatar_moeda(receita)}")

st.markdown(f"**(-) CMV**: {funcs.formatar_moeda(cmv)}")

st.markdown(f"**(-) Comissão**: {funcs.formatar_moeda(comissao)}")

st.markdown(f"**(-) Operação Variável**: {funcs.formatar_moeda(op_variavel)}")

margem_dre = op_variavel * 0.42
st.markdown(f"**Margem estimada após custos fixos**: {funcs.formatar_moeda(margem_dre)}")

if margem_dre < margem_contrib:
    st.markdown(f"**Interpretação**: {funcs.formatar_moeda(margem_dre)} <= MC")
elif margem_dre == margem-contrib:
    st.markdown(f"**Interpretação**: {funcs.formatar_moeda(margem_dre)} = MC")
elif margem_dre > margem_contrib:
    st.markdown(f"**Interpretação**: {funcs.formatar_moeda(margem_dre)} >= MC")

#endregion

st.markdown("---")

#region 8.3

st.subheader("**8.3** - ***Taxa de Realização da Receita***:")

mc_unitario = ticket_medio * 0.42
st.markdown(f"**Margem unitária por pedido**: {funcs.formatar_moeda(mc_unitario)}")

breakeven_50k = 50000 / mc_unitario
st.markdown(f"**Ponto de equilíbrio para R$50.000 de margem**: {breakeven_50k:.0f} pedidos/mês")

breakeven_100k = 100000 / mc_unitario
st.markdown(f"**Ponto de equilíbrio para R$100.000 de margem**: {breakeven_100k:.0f} pedidos/mês")

breakeven_200k = 200000 / mc_unitario
st.markdown(f"**Ponto de equilíbrio para R$200.000 de margem**: {breakeven_200k:.0f} pedidos/mês")

#endregion

st.markdown("---")

#region 8.4

st.subheader("**8.4** - ***Margem Bruta do Canal (variando comissão)***")

top1 = share_ordenado.iloc[0]
receita_por_canal = status16.groupby('saleschannel')['totalamount'].sum()
receita_por_canal = receita_por_canal.sort_values(ascending=False)
receita_top1 = receita_por_canal.iloc[0]
margem_top1 = receita_top1 * (1 - top1)
st.markdown(f"**Margem do Top 1**: {funcs.formatar_moeda(receita_top1)}")

receita_top2 = receita_por_canal.iloc[1]
top2 = share_ordenado.iloc[1]
margem_top2 = receita_top2 * (1 - top2)
st.markdown(f"**Margem do Top 2**: {funcs.formatar_moeda(receita_top2)}")

receita_top3 = receita_por_canal.iloc[2]
top3 = share_ordenado.iloc[2]
margem_top3 = receita_top3 * (1 - top3)
st.markdown(f"**Margem do Top 3**: {funcs.formatar_moeda(receita_top3)}")

receita_top4 = receita_por_canal.iloc[3]
top4 = share_ordenado.iloc[3]
margem_top4 = receita_top4 * (1 - top4)
st.markdown(f"**Margem do Top 4**: {funcs.formatar_moeda(receita_top4)}")

receita_top5 = receita_por_canal.iloc[4]
top5 = share_ordenado.iloc[4]
margem_top5 = receita_top5 * (1 - top5)
st.markdown(f"**Margem do Top 4**: {funcs.formatar_moeda(receita_top5)}")

st.markdown(f"{top1}")
st.markdown(f"{top2}")
st.markdown(f"{top3}")
st.markdown(f"{top4}")
st.markdown(f"{top5}")

#endregion