import pandas as pd


# leitura dos dados
Campaign = pd.read_csv("CAMPAIGN.csv", sep=",")
Campaignxorder = pd.read_csv("CAMPAIGNXORDER.csv", sep=",")
Customer = pd.read_csv("CUSTOMER.csv", sep=",")
Customeraddress = pd.read_csv("CUSTOMERADDRESS.csv", sep=",")
Store = pd.read_csv("STORE.csv", sep=",")
Storeorder = pd.read_csv("STOREORDER.csv", sep=",")



# contagem de todos os status
StatusAll = Storeorder["status"].value_counts()
qtd_status_16 = StatusAll.get(16, 0)

#pedidos que foram entregues
status_16_df = Storeorder[Storeorder["status"] == 16]

#total de receita
receita = status_16_df["totalamount"].sum()
print(receita)