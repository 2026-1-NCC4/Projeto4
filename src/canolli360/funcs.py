import pandas as pd
import altair as alt
#region helpers


def _calcular_inicio(data_max, periodo):
    if periodo == "Última semana":
        return data_max - pd.Timedelta(weeks=1)
    elif periodo == "Último mês":
        return data_max - pd.DateOffset(months=1)
    elif periodo == "Último bimestre":
        return data_max - pd.DateOffset(months=2)
    elif periodo == "Último trimestre":
        return data_max - pd.DateOffset(months=3)
    elif periodo == "Último semestre":
        return data_max - pd.DateOffset(months=6)
    elif periodo == "Último ano":
        return data_max - pd.DateOffset(years=1)
    return None

#endregion


#region filtros
def filtrar_periodo(df, periodo, coluna_data='scheduledat'):
    df = df.copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')

    data_max = df[coluna_data].max()
    inicio = _calcular_inicio(data_max, periodo)

    if inicio is None:
        return df

    return df[df[coluna_data] >= inicio]


def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

#endregion


#region cálculos

def receita_total(df):
    return df[df['status'] == 16]['totalamount'].sum()




def total_pedidos(df):
    return df[df['status'] == 16]['id'].count()




def ticket_medio(df, receita):
    df_16 = df[df['status'] == 16]
    quantidade = len(df_16)
    return receita / quantidade if quantidade > 0 else 0




def clientes_ativos(df_orders, df_customers, periodo):
    df_orders = filtrar_periodo(df_orders, periodo, 'createdat')

    clientes_ativos = df_customers[df_customers["status"] == 1]

    df_merge = df_orders.merge(
        clientes_ativos,
        left_on="customerid",
        right_on="id",
        how="inner"
    )

    return df_merge["customerid"].nunique()




def mensagens_totais(Mensagens):
    return Mensagens.groupby("campaignid")["message_id"].count()





def ranking_lojas(Mensagens, Stores, Campanhas):
    df_msg_camp = Mensagens.merge(
        Campanhas,
        left_on=["campaignid", "storeid"],
        right_on=["templateid", "storeid"],
        how="left"
    )

    ranking_lojas = df_msg_camp.merge(
        Stores[["id", "name"]],
        left_on="storeid",
        right_on="id",
        how="left"
    )

    return (
        ranking_lojas
        .groupby(["storeid", "name"])["message_id"]
        .count()
        .reset_index()
        .sort_values(by="message_id", ascending=False)
    )


def valor_per_mes(StoreOrder, periodo):
    df = filtrar_periodo(StoreOrder, periodo, 'createdat')
  
    valor_por_mes = (
        df[df['status'] == 16]
        .set_index('createdat')
        .resample('ME')['totalamount']
        .sum()
        .reset_index()
    )

    return valor_por_mes
#endregion







#region gráficos
def grafico_receita_mensal(df):
    import altair as alt
    import pandas as pd

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
        .mark_line(point=True)
        .encode(
            x='createdat:T',
            y='totalamount:Q',
            tooltip=['createdat:T', 'totalamount:Q']
        )
    )

    return chart

#endregion