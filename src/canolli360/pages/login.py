import streamlit as st
col1,col2,col3=st.columns([1,2,1])

#usuários para teste:
usuarios = {
    "a":"123",
    "b":"123",
    "c":"123"
}



with col2:

    st.title("Login")

    usuario=st.text_input("Usuário")

    senha=st.text_input(
        "Senha",
        type="password"
    )

    st.button("Entrar")


    
if usuario in usuarios:

    if usuarios[usuario] == senha:

        st.session_state.logado=True
        st.session_state.usuario=usuario
        st.switch_page("pages/dashboard.py")

