import streamlit as st
from modules.nav import Navbar

def main():
    st.title("Multi-modal RAG Chatbot 🤖")
    st.text("Chatbot basado en RAG que permite cargar múltiples tipos de archivos y proporciona respuestas generadas a partir del contenido.")

    Navbar()


if __name__ == '__main__':
    main()
