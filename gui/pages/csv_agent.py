import streamlit as st

from modules.nav import Navbar

#from gui.clients.agent_client import AgentClient
from clients.agent_client import AgentClient

def main():

    st.set_page_config(page_title="Agente CRM", page_icon='📊')
    st.title("Agente CRM 📊")

    st.write("""
        ¡Bienvenido al Agente CRM! Este agente puede responder preguntas sobre datos almacenados en un archivo CSV.
    """)

    # Inicializar el cliente de agente
    agent = AgentClient('localhost', 8000)

    # Inicializar el estado de mensajes en Streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("¿En qué puedo ayudarte?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            respuesta = agent.query_csv(user_input)
            message_placeholder.markdown(respuesta)

        st.session_state.messages.append({"role": "assistant", "content": respuesta})

    Navbar()



if __name__ == '__main__':
    main()
