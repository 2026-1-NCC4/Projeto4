"""
Pseudonimização para exibição (LGPD — minimização de dados identificáveis).
Mantém `id` de loja para filtros e joins; substitui `name` por rótulo neutro.
"""
import hashlib
import pandas as pd


def _rotulo_parceiro(loja_id) -> str:
    h = hashlib.sha256(str(loja_id).encode()).hexdigest()[:5].upper()
    return f"Parceiro #{h}"


def mascarar_tabela_lojas(store: pd.DataFrame) -> pd.DataFrame:
    if store is None or store.empty or "id" not in store.columns:
        return store
    out = store.copy()
    if "name" in out.columns:
        out["name"] = out["id"].map(_rotulo_parceiro)
    return out


def mascarar_id_cliente(series: pd.Series, prefix: str = "CLI") -> pd.Series:
    """Não expõe identificadores brutos (numéricos ou UUID)."""

    def _um(val) -> str:
        tail = hashlib.sha256(str(val).encode()).hexdigest()[:6].upper()
        return f"{prefix}-{tail}"

    return series.apply(_um)
