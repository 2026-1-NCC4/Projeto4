import streamlit as st
import matplotlib.pyplot as plt
import funcs

def card_valor(titulo, valor, delta, positivo=None):
    cor = "#e9820c"
    if positivo is True:
        cor = "#16a34a"  # verde mais bonito
    elif positivo is False:
        cor = "#dc2626"  # vermelho mais bonito

    st.markdown(f"""
    <div style="
        width: 100%;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 20px;
        background-color: #f5f6fa;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    ">
        <div style="font-size:14px; color:#66785; margin-bottom:8px;">
            {titulo}
        </div>
        <div style="font-size:30px; font-weight:700; margin-bottom:6px;">
            {valor}
        </div>
        <div style="color:{cor}; font-size:14px;">
            {delta}
        </div>
    </div>
    """, unsafe_allow_html=True)


def card_pizza5(campaignxorder, campaign, store, Titulo):
        ranking_lojas = funcs.campanhas_por_loja(campaignxorder, campaign, store)
        top5 = ranking_lojas.head(5)

        fig, ax = plt.subplots()

        ax.pie(
            top5["qtd_mensagens"],
            labels=top5["name"],
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "black"}
        )
        ax.set_title(Titulo)
        return st.pyplot(fig)

