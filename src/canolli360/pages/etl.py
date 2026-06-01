"""
Ingestão de dados (ETL leve) — upload na sessão, sem cache Streamlit e sem gravar CSV no disco.
"""
from __future__ import annotations

import io
import logging
import sys
import zipfile
import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger("cannoli360.etl")
if not logger.handlers:
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

# Nome do arquivo (maiúsculas) → chave interna do dashboard
ARQUIVOS_OBRIGATORIOS: dict[str, str] = {
    "STORE.CSV": "store",
    "CUSTOMER.CSV": "customer",
    "STOREORDER.CSV": "storeorder",
    "CUSTOMERADDRESS.CSV": "customeraddress",
    "CAMPAIGN.CSV": "campaign",
    "CAMPAIGNXORDER.CSV": "campaignxorder",
}

_CSV_FILES = {v: k for k, v in ARQUIVOS_OBRIGATORIOS.items()}


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out


def _preparar_storeorder(df: pd.DataFrame) -> pd.DataFrame:
    out = _normalizar_colunas(df)
    if "saleschannel" not in out.columns:
        out["saleschannel"] = "Não informado"
    if "ordertype" not in out.columns:
        out["ordertype"] = "Não informado"
    if "createdat" not in out.columns and "scheduledat" in out.columns:
        out["createdat"] = out["scheduledat"]
    return out


def _preparar_campaignxorder(df: pd.DataFrame) -> pd.DataFrame:
    out = _normalizar_colunas(df)
    if "sent_at" not in out.columns:
        out["sent_at"] = pd.NaT
    return out


def _preparar_conjunto(dados: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    out = dict(dados)
    if "storeorder" in out:
        out["storeorder"] = _preparar_storeorder(out["storeorder"])
    if "campaignxorder" in out:
        out["campaignxorder"] = _preparar_campaignxorder(out["campaignxorder"])
    if "store" in out:
        out["store"] = _normalizar_colunas(out["store"])
    return out


def _ler_csv_bytes(conteudo: bytes, rotulo: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(io.BytesIO(conteudo))
        logger.info("Carregado %s (%s linhas)", rotulo, len(df))
        return df
    except Exception:
        logger.exception("Erro ao ler %s", rotulo)
        raise


def _mapear_nome_arquivo(nome: str) -> str | None:
    base = nome.replace("\\", "/").split("/")[-1].strip().upper()
    return ARQUIVOS_OBRIGATORIOS.get(base)


def _extrair_csvs_de_zip(zip_bytes: bytes) -> dict[str, bytes]:
    encontrados: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.lower().endswith(".csv"):
                continue
            chave = _mapear_nome_arquivo(info.filename)
            if chave and chave not in encontrados:
                encontrados[chave] = zf.read(info)
    return encontrados


def _extrair_csvs_uploads(
    arquivos_upload: list,
) -> dict[str, bytes]:
    """Aceita arquivos .csv soltos ou um .zip com a pasta dados."""
    encontrados: dict[str, bytes] = {}

    for up in arquivos_upload or []:
        nome = (up.name or "").lower()
        if nome.endswith(".zip"):
            for chave, conteudo in _extrair_csvs_de_zip(up.getvalue()).items():
                encontrados.setdefault(chave, conteudo)
            continue
        if nome.endswith(".csv"):
            chave = _mapear_nome_arquivo(up.name)
            if chave:
                encontrados[chave] = up.getvalue()
            continue
        raise ValueError(f"Arquivo não permitido: {up.name}. Use apenas CSV ou ZIP.")

    return encontrados


def _carregar_de_bytes(por_chave: dict[str, bytes]) -> dict[str, pd.DataFrame]:
    faltando = [k for k in ARQUIVOS_OBRIGATORIOS.values() if k not in por_chave]
    if faltando:
        nomes = ", ".join(_CSV_FILES[k] for k in faltando)
        raise ValueError(f"Arquivos obrigatórios ausentes: {nomes}")

    out: dict[str, pd.DataFrame] = {}
    for chave, conteudo in por_chave.items():
        if chave in ARQUIVOS_OBRIGATORIOS.values():
            rotulo = _CSV_FILES[chave]
            out[chave] = _ler_csv_bytes(conteudo, rotulo)
    return _preparar_conjunto(out)


def _gerar_demonstracao() -> dict[str, pd.DataFrame]:
    """
    Base sintética gerada no código (não lê CSV da Cannoli).

    Usada quando não há arquivos reais: números aleatórios com seed fixa (42)
    para sempre repetir o mesmo cenário de teste — 10 lojas fictícias,
    ~800 clientes, ~3.500 pedidos e campanhas simuladas.
    """
    rng = np.random.default_rng(42)
    n_lojas = 10
    n_clientes = 800
    n_pedidos = 3500

    store = pd.DataFrame(
        {
            "id": np.arange(1, n_lojas + 1),
            "name": [f"Cozinha Piloto {i+1}" for i in range(n_lojas)],
        }
    )
    customer = pd.DataFrame(
        {
            "id": np.arange(1, n_clientes + 1),
            "status": rng.choice([0, 1], size=n_clientes, p=[0.12, 0.88]),
        }
    )
    customeraddress = pd.DataFrame(
        {
            "id": np.arange(1, n_clientes + 1),
            "customerid": np.arange(1, n_clientes + 1),
            "city": rng.choice(["São Paulo", "Campinas", "Curitiba"], n_clientes),
        }
    )

    t0 = pd.Timestamp("2023-01-01")
    datas = t0 + pd.to_timedelta(rng.integers(0, 500, size=n_pedidos), unit="D")
    status = rng.choice([16, 8, 11, 14, 6], size=n_pedidos, p=[0.72, 0.08, 0.06, 0.04, 0.10])

    storeorder = pd.DataFrame(
        {
            "id": np.arange(1, n_pedidos + 1),
            "storeid": rng.integers(1, n_lojas + 1, size=n_pedidos),
            "customerid": rng.integers(1, n_clientes + 1, size=n_pedidos),
            "status": status,
            "subtotalamount": rng.uniform(25, 180, n_pedidos).round(2),
            "discountamount": rng.uniform(0, 25, n_pedidos).round(2),
            "taxamount": rng.uniform(0, 8, n_pedidos).round(2),
            "totalamount": 0.0,
            "createdat": datas,
            "scheduledat": datas,
            "saleschannel": rng.choice(["app", "web", "balcão"], n_pedidos),
            "ordertype": rng.choice(["delivery", "retirada", "mesa"], n_pedidos),
        }
    )
    storeorder["totalamount"] = (
        storeorder["subtotalamount"] - storeorder["discountamount"] + storeorder["taxamount"]
    ).round(2)

    camp_ids = np.array([101, 102, 103])
    n_cxo = 9000
    cxo_sent = t0 + pd.to_timedelta(rng.integers(0, 500, size=n_cxo), unit="D")
    campaignxorder = pd.DataFrame(
        {
            "campaignid": rng.choice(camp_ids, size=n_cxo),
            "storeid": rng.integers(1, n_lojas + 1, size=n_cxo),
            "message_id": np.arange(1, n_cxo + 1),
            "status": rng.choice([2, 4, 6], size=n_cxo, p=[0.55, 0.12, 0.33]),
            "order_id": rng.integers(1, n_pedidos + 1, size=n_cxo),
            "totalamount": rng.uniform(30, 200, n_cxo).round(2),
            "sent_at": cxo_sent,
        }
    )

    rows = []
    for sid in range(1, n_lojas + 1):
        for tid in camp_ids:
            rows.append({"templateid": int(tid), "storeid": int(sid), "title": f"Campanha {tid}"})
    campaign = pd.DataFrame(rows)

    return _preparar_conjunto(
        {
            "store": store,
            "customer": customer,
            "storeorder": storeorder,
            "customeraddress": customeraddress,
            "campaign": campaign,
            "campaignxorder": campaignxorder,
        }
    )


class _ArquivoUpload:
    """Wrapper mínimo para reutilizar _extrair_csvs_uploads com bytes em memória."""

    __slots__ = ("name", "_bytes")

    def __init__(self, name: str, data: bytes) -> None:
        self.name = name
        self._bytes = data

    def getvalue(self) -> bytes:
        return self._bytes


def _garantir_estado_upload() -> None:
    if "arquivos_dict" not in st.session_state:
        st.session_state.arquivos_dict = {}
    if "upload_widget_rev" not in st.session_state:
        st.session_state.upload_widget_rev = 0


def _limpar_selecao_upload() -> None:
    """Zera fila, dados importados e força file_uploader vazio (nova key)."""
    st.session_state.arquivos_dict = {}
    st.session_state.upload_widget_rev += 1
    st.session_state.pop("dados_conjunto", None)
    st.session_state.pop("dados_origem", None)
    st.session_state.pop("dados_upload_bytes", None)
    st.session_state.pop("upload_erro", None)
    for chave in list(st.session_state.keys()):
        if chave == "upload_dados_csv" or (
            isinstance(chave, str) and chave.startswith("upload_dados_")
        ):
            st.session_state.pop(chave, None)


def _sincronizar_arquivos_uploader(arquivos) -> None:
    """Espelha a seleção do file_uploader."""
    st.session_state.arquivos_dict = {
        arq.name: arq.getvalue() for arq in (arquivos or [])
    }


def _lista_arquivos_para_upload() -> list[_ArquivoUpload]:
    return [
        _ArquivoUpload(nome, dados)
        for nome, dados in st.session_state.get("arquivos_dict", {}).items()
    ]


def _aplicar_upload_arquivos() -> bool:
    """Importa os arquivos da fila selecionada. Retorna True se ok."""
    arquivos = _lista_arquivos_para_upload()
    if not arquivos:
        st.session_state["upload_erro"] = "Selecione os arquivos (CSV ou ZIP) antes de fazer upload."
        return False
    try:
        por_chave = _extrair_csvs_uploads(arquivos)
        st.session_state["dados_upload_bytes"] = por_chave
        st.session_state["dados_conjunto"] = _carregar_de_bytes(por_chave)
        st.session_state["dados_origem"] = "upload"
        st.session_state.pop("upload_erro", None)
        return True
    except Exception as exc:
        st.session_state["upload_erro"] = str(exc)
        st.session_state.pop("dados_conjunto", None)
        st.session_state.pop("dados_origem", None)
        return False


def render_secao_upload() -> None:
    """Painel na sidebar: upload da pasta dados (CSV ou ZIP), sem cache Streamlit."""
    _garantir_estado_upload()
    upload_concluido = (
        st.session_state.get("dados_origem") == "upload"
        and st.session_state.get("dados_conjunto") is not None
    )

    with st.sidebar:
        st.markdown(
            """
            <div class="bloco-upload-dados">
                <h3>Dados</h3>
                <p>Carregue os arquivos.</p>
                <p class="fmt-tipos">CSV ou ZIP</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # type=None evita o bug do Streamlit que exibe "CEP" no lugar de "zip"
        selecionados = st.file_uploader(
            "Adicionar arquivos",
            accept_multiple_files=True,
            key=f"upload_dados_{st.session_state.upload_widget_rev}",
            label_visibility="collapsed",
        )
        _sincronizar_arquivos_uploader(selecionados)

        if st.session_state.get("upload_erro"):
            st.error(st.session_state["upload_erro"])

        col_up, col_limpar = st.columns(2, gap="small")
        with col_up:
            if upload_concluido:
                st.button(
                    "Upload",
                    type="secondary",
                    use_container_width=True,
                    key="btn_carregar_dados_ok",
                    disabled=True,
                )
            elif st.button(
                "Upload",
                type="primary",
                use_container_width=True,
                key="btn_carregar_dados",
            ):
                if _aplicar_upload_arquivos():
                    st.rerun()
        with col_limpar:
            st.button(
                "Limpar",
                type="secondary",
                use_container_width=True,
                key="btn_limpar_dados",
                on_click=_limpar_selecao_upload,
            )

        if st.button(
            "Demonstração",
            type="secondary",
            use_container_width=True,
            key="btn_demo_dados",
        ):
            st.session_state["dados_conjunto"] = _gerar_demonstracao()
            st.session_state["dados_origem"] = "demo"
            st.session_state.pop("dados_upload_bytes", None)
            st.session_state.pop("upload_erro", None)
            st.rerun()


def render_rodape_sidebar() -> None:
    """Status e créditos fixos no final da sidebar."""
    with st.sidebar:
        st.markdown('<div class="sidebar-rodape-fixo">', unsafe_allow_html=True)
        if (
            st.session_state.get("dados_origem") == "upload"
            and st.session_state.get("dados_conjunto") is not None
        ):
            st.caption("Dados reais importados.")
        st.caption("Cannoli360 — PI TechTonics — extensão FECAP 2026")
        st.markdown("</div>", unsafe_allow_html=True)


def obter_dados() -> dict[str, pd.DataFrame] | None:
    """Retorna o conjunto da sessão (session_state apenas, sem cache Streamlit)."""
    conjunto = st.session_state.get("dados_conjunto")
    if conjunto is not None:
        return conjunto

    return None


def carregar_ou_demo() -> dict[str, pd.DataFrame]:
    """Compatibilidade com páginas existentes; interrompe a tela se não houver dados."""
    dados = obter_dados()
    if dados is None:
        st.markdown(
            """
            <div class="msg-inicio-app">
                <p>Carregue os arquivos.</p>
                <span>Use a sessão <strong>Dados</strong> na barra à esquerda, selecione os arquivos (CSV ou ZIP) e clique em <strong>Upload</strong>.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()
    return dados
