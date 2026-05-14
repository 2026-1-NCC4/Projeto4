#landpage


import streamlit as st

if st.button("Ir para Dashboard"):
   	st.switch_page("pages/dashboard.py")

if st.button("Login"):
	st.switch_page("pages/login.py")