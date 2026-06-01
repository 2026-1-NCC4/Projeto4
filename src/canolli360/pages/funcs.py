import math
import numpy as np
import pandas as pd
from paths import DATA_DIR, PACKAGE_DIR


#region FUNÇÕES AUXILIARES E FILTROS

def _calcular_inicio(data_max, periodo):
    """Calcula a data inicial com base no período selecionado."""
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


def filtrar_periodo(df, periodo, coluna_data='scheduledat'):
    """Filtra o DataFrame com base em uma coluna de data e um período."""
    df = df.copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')

    data_max = df[coluna_data].max()
    inicio = _calcular_inicio(data_max, periodo)

    if inicio is None:
        return df

    return df[df[coluna_data] >= inicio]


def formatar_moeda(valor):
    """Formata um valor numérico para a string de moeda brasileira (R$)."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")




#region  MÉTRICAS E CÁLCULOS DE VENDAS

def receita_total(df):
    """Calcula a receita total para pedidos concluídos (status 16)."""
    return df[df['status'] == 16]['totalamount'].sum()


def total_pedidos(df):
    """Conta a quantidade de pedidos concluídos (status 16)."""
    return df[df['status'] == 16]['id'].count()


def ticket_medio(df, receita):
    """Calcula o ticket médio dos pedidos concluídos (status 16)."""
    df_16 = df[df['status'] == 16]
    quantidade = len(df_16)
    return receita / quantidade if quantidade > 0 else 0


def clientes_ativos(df_orders, df_customers, periodo):
    """Retorna o número de clientes ativos em um determinado período."""
    df_orders = filtrar_periodo(df_orders, periodo, 'createdat')
    clientes_ativos = df_customers[df_customers["status"] == 1]

    df_merge = df_orders.merge(
        clientes_ativos,
        left_on="customerid",
        right_on="id",
        how="inner"
    )
    return df_merge["customerid"].nunique()


def valor_per_mes(StoreOrder, periodo):
    """Agrupa a receita dos pedidos concluídos (status 16) por mês."""
    df = filtrar_periodo(StoreOrder, periodo, 'createdat')
  
    valor_por_mes = (
        df[df['status'] == 16]
        .set_index('createdat')
        .resample('ME')['totalamount']
        .sum()
        .reset_index()
    )
    return valor_por_mes



#region CAMPANHAS E ENGAJAMENTO


def campanhas_por_loja(campaignxorder, campaign, store):
    """Volume de mensagens de campanha por loja (para gráficos de engajamento)."""
    del campaign  # join opcional com tabela de campanha — métrica usa só pedidos x loja
    df = campaignxorder.merge(
        store[["id", "name"]],
        left_on="storeid",
        right_on="id",
        how="left",
    )
    return (
        df.groupby(["storeid", "name"], as_index=False)["message_id"]
        .count()
        .rename(columns={"message_id": "qtd_mensagens"})
        .sort_values("qtd_mensagens", ascending=False)
    )


def taxa_conversao_campanha(campaignxorder: pd.DataFrame) -> tuple[float, float, int, int]:
    """Taxa de conversão mensagens enviadas (status 2) → conversão atribuída (status 4)."""
    env = campaignxorder[campaignxorder["status"] == 2]
    conv = campaignxorder[campaignxorder["status"] == 4]
    
    n_env = len(env)
    n_conv = len(conv)
    
    taxa = (n_conv / n_env * 100) if n_env else 0.0
    rec_conv = float(conv["totalamount"].sum()) if n_conv else 0.0
    
    return taxa, rec_conv, n_env, n_conv

#region diabo encarnado
def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Limites inferiores e superiores (~95%) da taxa de conversão em %."""

    # evita divisão inválida
    if n <= 0:
        return (0.0, 0.0)

    # garante que essa bomba não exploda 
    if successes < 0:
        successes = 0

    if successes > n:
        successes = n

    p = successes / n

    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom

    rad = (z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)/ denom) #porque professor?? porque??

    lo = max(0.0, (centre - rad) * 100)
    hi = min(100.0, (centre + rad) * 100)

    return lo, hi


def filtrar_periodo_mes(df: pd.DataFrame, periodo: str, coluna_data: str) -> pd.DataFrame:
    """Filtra o DataFrame pelo período no formato 'YYYY-MM' vindo do menu.render_header.

    Complementa filtrar_periodo() que aceita strings como 'Último mês'.
    Retorna o df inteiro quando periodo == 'Todos'.
    """
    df = df.copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
    if periodo == "Todos":
        return df
    try:
        p = pd.Period(periodo, freq="M")
        mask = df[coluna_data].dt.to_period("M") == p
        return df[mask]
    except Exception:
        return df


def _normalizar_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out


def _moda_texto(series: pd.Series) -> str | None:
    s = series.dropna().astype(str).str.strip()
    s = s[s != ""]
    if s.empty:
        return None
    return str(s.mode().iloc[0])


def metadados_campanhas(
    campaignxorder: pd.DataFrame, campaign: pd.DataFrame
) -> pd.DataFrame:
    """Mapeia campaignid → nome legível (e metadados) a partir de CAMPAIGN."""
    cxo = _normalizar_cols(campaignxorder)
    camp = _normalizar_cols(campaign)

    if "campaignid" not in cxo.columns:
        return pd.DataFrame(columns=["campaignid", "name", "type", "sendat"])

    ids = list(cxo["campaignid"].dropna().unique())
    nomes: dict = {cid: None for cid in ids}
    tipos: dict = {cid: None for cid in ids}
    sendats: dict = {cid: None for cid in ids}

    def _preencher(mapa: pd.DataFrame, col_id: str) -> None:
        if col_id not in mapa.columns or "name" not in mapa.columns:
            return
        base = mapa.dropna(subset=["name"]).drop_duplicates(subset=[col_id])
        for _, row in base.iterrows():
            cid = row[col_id]
            if cid not in nomes or nomes[cid] is not None:
                continue
            nomes[cid] = str(row["name"]).strip()
            if "type" in row.index and pd.notna(row.get("type")):
                tipos[cid] = row["type"]
            if "sendat" in row.index and pd.notna(row.get("sendat")):
                sendats[cid] = row["sendat"]

    for col_id in ("campaignid", "segmentid", "templateid"):
        _preencher(camp, col_id)

    if {"storeid", "customerid", "name"} <= set(camp.columns):
        cols_camp = ["storeid", "customerid", "name"] + [
            c for c in ["type", "sendat", "description"] if c in camp.columns
        ]
        j = cxo[["campaignid", "storeid", "customerid"]].drop_duplicates().merge(
            camp[cols_camp],
            on=["storeid", "customerid"],
            how="left",
        )
        if "description" in j.columns:
            j["name"] = j["name"].fillna(j["description"])

        agg: dict = {"name": _moda_texto}
        if "type" in j.columns:
            agg["type"] = _moda_texto
        if "sendat" in j.columns:
            agg["sendat"] = "first"

        por_id = j.groupby("campaignid", as_index=False).agg(agg)
        for _, row in por_id.iterrows():
            cid = row["campaignid"]
            if nomes.get(cid) is None and row.get("name"):
                nomes[cid] = str(row["name"]).strip()
            if tipos.get(cid) is None and pd.notna(row.get("type")):
                tipos[cid] = row["type"]
            if sendats.get(cid) is None and pd.notna(row.get("sendat")):
                sendats[cid] = row["sendat"]

    return pd.DataFrame(
        {
            "campaignid": ids,
            "name": [nomes[i] for i in ids],
            "type": [tipos.get(i) for i in ids],
            "sendat": [sendats.get(i) for i in ids],
        }
    )


def nome_campanha_exibicao(name, campaignid) -> str:
    """Rótulo amigável para UI (sem UUID)."""
    if name is not None and pd.notna(name) and str(name).strip():
        return str(name).strip()
    return "Campanha sem nome"


def ranking_campanhas(
    campaignxorder: pd.DataFrame, campaign: pd.DataFrame
) -> pd.DataFrame:
    """Ranking de campanhas com métricas individuais de conversão e receita.

    Retorna um DataFrame com uma linha por campanha contendo:
    name, type, sendat, n_enviadas, n_conversoes, taxa_conversao, receita_conv.
    """
    cxo = _normalizar_cols(campaignxorder)
    env = cxo[cxo["status"] == 2].groupby("campaignid").agg(
        n_enviadas=("message_id", "count")
    )
    conv = cxo[cxo["status"] == 4].groupby("campaignid").agg(
        n_conversoes=("message_id", "count"),
        receita_conv=("totalamount", "sum"),
    )
    df = env.join(conv, how="outer").fillna(0).reset_index()
    df["taxa_conversao"] = df.apply(
        lambda r: (r["n_conversoes"] / r["n_enviadas"] * 100) if r["n_enviadas"] > 0 else 0.0,
        axis=1,
    )

    meta = metadados_campanhas(campaignxorder, campaign)
    df = df.merge(meta, on="campaignid", how="left")
    df["name"] = df.apply(
        lambda r: nome_campanha_exibicao(r.get("name"), r["campaignid"]),
        axis=1,
    )

    return df.sort_values("taxa_conversao", ascending=False).reset_index(drop=True)


def campanhas_por_loja_detalhado(
    campaignxorder: pd.DataFrame, store: pd.DataFrame
) -> pd.DataFrame:
    """Métricas de conversão cruzando campanha × loja.

    Retorna um DataFrame com colunas:
    campaignid, storeid, nome_loja, n_enviadas, n_conversoes, taxa_conversao, receita_conv.
    """
    env = (
        campaignxorder[campaignxorder["status"] == 2]
        .groupby(["campaignid", "storeid"], as_index=False)
        .agg(n_enviadas=("message_id", "count"))
    )
    conv = (
        campaignxorder[campaignxorder["status"] == 4]
        .groupby(["campaignid", "storeid"], as_index=False)
        .agg(n_conversoes=("message_id", "count"), receita_conv=("totalamount", "sum"))
    )
    df = env.merge(conv, on=["campaignid", "storeid"], how="outer").fillna(0)
    df["taxa_conversao"] = df.apply(
        lambda r: (r["n_conversoes"] / r["n_enviadas"] * 100) if r["n_enviadas"] > 0 else 0.0,
        axis=1,
    )
    df = df.merge(store[["id", "name"]].rename(columns={"name": "nome_loja"}),
                  left_on="storeid", right_on="id", how="left")
    df["nome_loja"] = df["nome_loja"].fillna("—")
    return df.sort_values(["campaignid", "taxa_conversao"], ascending=[True, False]).reset_index(drop=True)




def resumo_loja(df_lojas: pd.DataFrame, store: pd.DataFrame) -> pd.DataFrame:
    """Resumo por loja: total de mensagens, conversões, taxa e receita."""
    df = (
        df_lojas.groupby("nome_loja", as_index=False)
        .agg(
            n_enviadas=("n_enviadas", "sum"),
            n_conversoes=("n_conversoes", "sum"),
            receita_conv=("receita_conv", "sum"),
            n_campanhas=("campaignid", "nunique"),
        )
    )
    df["taxa_conversao"] = df.apply(
        lambda r: r["n_conversoes"] / r["n_enviadas"] * 100 if r["n_enviadas"] > 0 else 0.0,
        axis=1,
    )
    return df.sort_values("n_enviadas", ascending=False).reset_index(drop=True)

# region ANÁLISE AVANÇADA (RFM) E GRÁFICOS

def calcular_rfm(storeorder: pd.DataFrame, periodo: str, store: pd.DataFrame) -> pd.DataFrame:
    """RFM (Recência, Frequência, Valor) em pedidos concluídos (status 16).

    Inclui o nome do parceiro (loja) conforme o último pedido concluído do cliente no recorte.
    """
    df = filtrar_periodo(storeorder.copy(), periodo, "createdat")
    df = df[df["status"] == 16].copy()
    df["createdat"] = pd.to_datetime(df["createdat"], errors="coerce")
    
    ref = df["createdat"].max()
    if pd.isna(ref) or df.empty:
        return pd.DataFrame(
            columns=[
                "customerid", "parceiro", "recencia_dias", "frequencia", 
                "valor", "R", "F", "M", "segmento"
            ]
        )

    if store is not None and not store.empty and "id" in store.columns and "name" in store.columns:
        lojas = store[["id", "name"]].drop_duplicates(subset=["id"]).copy()
        lojas["_sk"] = lojas["id"].astype(str)
        df["_sk"] = df["storeid"].astype(str)
        df = df.merge(lojas[["_sk", "name"]], on="_sk", how="left").rename(columns={"name": "_parceiro"})
        df = df.drop(columns=["_sk"], errors="ignore")
        df["_parceiro"] = df["_parceiro"].fillna("—")
    else:
        df["_parceiro"] = "—"

    # Nome do parceiro = loja do último pedido concluído (maior data) no período filtrado
    ult = df.sort_values(["customerid", "createdat"]).groupby("customerid").tail(1)
    mapa_parceiro = ult.set_index("customerid")["_parceiro"]

    g = (
        df.groupby("customerid", as_index=False)
        .agg(
            recencia_dias=(
                "createdat",
                lambda s: int((ref - s.max()).days) if pd.notna(s.max()) else np.nan
            ),
            frequencia=("id", "count"),
            valor=("totalamount", "sum"),
        )
    )
    g["parceiro"] = g["customerid"].map(mapa_parceiro).fillna("—")

    def _qcut_safe(serie: pd.Series, labels: list[int]) -> pd.Series:
        s = serie.astype(float)
        if len(s) < 5 or s.nunique() < 2:
            return pd.Series(3, index=s.index, dtype="int64")

        try:
            q = pd.qcut(s, 5, labels=labels, duplicates="drop")
            return q.fillna(3).astype(int)
        except ValueError:
            return pd.Series(3, index=s.index, dtype="int64")

    # Menos dias desde a última compra = melhor recência (nota 5 no primeiro quintil).
    g["R"] = _qcut_safe(g["recencia_dias"], [5, 4, 3, 2, 1])
    g["F"] = _qcut_safe(g["frequencia"], [1, 2, 3, 4, 5])
    g["M"] = _qcut_safe(g["valor"], [1, 2, 3, 4, 5])

    def _segmento(row) -> str:
        r, f = int(row["R"]), int(row["F"])
        if r >= 4 and f >= 4:
            return "Campeões"
        if r <= 2 and f >= 3:
            return "Em risco"
        if r <= 2 and f <= 2:
            return "Hibernando / churn"
        if f >= 3:
            return "Leais"
        return "Oportunidade"

    g["segmento"] = g.apply(_segmento, axis=1)
    return g