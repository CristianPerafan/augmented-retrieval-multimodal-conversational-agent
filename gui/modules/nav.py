import streamlit as st


def Navbar():
    with st.sidebar:
        st.page_link('app.py', label='Home', icon='🏠')
        st.page_link('pages/csv_agent.py', label='Agente CRM', icon='📊')
        st.page_link('pages/pdf_agent.py', label='Agente PDF', icon='📄')
