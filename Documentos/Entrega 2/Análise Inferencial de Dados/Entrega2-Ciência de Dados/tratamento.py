import pandas as pd

# ===========================
# LEITURA DOS ARQUIVOS CSV
# ===========================
dfCxO = pd.read_csv("dados/CAMPAIGNxORDER.CSV", sep=",")  # campanhas x pedidos
dfLJ = pd.read_csv("dados/STORE.csv", sep=",")            # lojas
dfSO = pd.read_csv("dados/STOREORDER.csv", sep=",")       # pedidos das lojas


# ===========================
# AGRUPAMENTO DE DADOS CAMPAIGN x ORDER
# ===========================
dfCxO.groupby(['storeid', 'campaignid']).agg({
    'message_id': 'nunique',   # mensagens únicas
    'order_id': 'nunique',     # pedidos únicos
    'totalamount': 'sum'       # soma do valor
}).reset_index()


# ===========================
# CRIAÇaO DE DATAFRAME DE LOJAS
# ===========================
dfLJ = pd.DataFrame({
    'Nome_Loja': dfLJ['name'].unique(),  # nomes únicos
    'ID_Loja': dfLJ['id'].unique()       # ids únicos
})


# ===========================
# MERGE DOS DADOS
# ===========================
dfCxOLJ = pd.merge(
    dfLJ,
    dfCxO,
    left_on='ID_Loja',
    right_on='storeid',
    how='left'
)

# remove coluna duplicada após merge
dfCxOLJ.drop(columns=['storeid'], inplace=True)


# ===========================
# LISTA DE LOJAS
# ===========================
lojas = sorted(dfCxOLJ['Nome_Loja'].unique().tolist())
print(f"lojas: {lojas}")


# ===========================
# MÉTRICAS GERAIS (CAMPANHAS)
# ===========================

# total de vendas únicas em campanhas
total_vendas_campanha = dfCxOLJ['order_id'].nunique()
print(f"total em vendas: {total_vendas_campanha}")

# valor total das campanhas (sem duplicar pedidos)
total_valor_campanhas = dfCxOLJ.drop_duplicates(subset='order_id')['totalamount'].sum()
print(f"total Valor campanhas: {total_valor_campanhas}")

# total de mensagens enviadas
total_mensagens = dfCxOLJ['message_id'].count()
print(f"total Mensagens: {total_mensagens}")


# ===========================
# MÉTRICAS (STORE ORDER)
# ===========================

# total de pedidos na tabela de lojas
total_vendas = dfSO['id'].nunique()
print(f"total em vendas STORE ORDER: {total_vendas}")

# soma total de valores das vendas
total_valor_storeorder = dfSO['totalamount'].sum()
print(f"total Valor STORE ORDER: {total_valor_storeorder}")


# ===========================
# TAXA DE CONVERSÃO
# ===========================

# conversão de campanhas em vendas
taxa_conversao = (total_vendas_campanha / total_vendas) * 100
print(f"taxa de conversao: {taxa_conversao}")

# ===========================
# 2. TAXA DE CONVERSÃO (VALOR)
# ===========================
taxa_conversao_valor = (total_valor_campanhas / total_valor_storeorder) * 100
print(f"taxa de conversao valor: {taxa_conversao_valor}")

# ===========================
# MENSAGENS POR CAMPANHA
# ===========================

df_mensagens = dfCxOLJ.groupby('campaignid')['message_id'].count().reset_index()
print(df_mensagens)


# ===========================
# RELAÇÃO VALOR x MENSAGENS
# ===========================

taxa_valor = (total_valor_storeorder / total_mensagens) * 100
print(f"\ntaxa valor: {taxa_valor}")


# outro resumo de mensagens por campanha (duplicado do anterior)
mensagenspercampanha = dfCxOLJ.groupby('campaignid')['message_id'].count().reset_index()