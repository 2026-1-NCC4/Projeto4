import streamlit as st
import re  #biblioteca padrão para expressões regulares


if "logado" not in st.session_state:
    st.session_state.logado = False

#configuração de colunas para centralizar o formulario
col1, col2, col3 = st.columns([1, 2, 1])

#usuários cadastrados para teste
usuarios = {
    "abc": "123",
    "b": "123",
    "c": "123"
}

# apenas letras maiusculas/minusculas e números, de 1 a 10 caracteres 
padrao_usuario = r"^[a-zA-Z0-9]{3,10}$"

with col2:
    st.title("Login")

    # Campos de entrada de dados
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")


    botao_entrar = st.button("Entrar")


if botao_entrar:
    

    if not usuario:
        st.warning("Por favor, digite o usuário.")
        

    elif not re.match(padrao_usuario, usuario):
        st.error("Usuário inválido! Use apenas letras e números (máx. 10 caracteres) e sem espaços.")
    

    elif usuario in usuarios and usuarios[usuario] == senha:
        st.session_state.logado = True
        st.session_state.usuario = usuario
        st.success("Login realizado com sucesso!")
        st.switch_page("pages/dashboard.py")
        

    else:
        st.error("Usuário ou senha incorretos.")
