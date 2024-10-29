import streamlit as st

from modules.nav import Navbar

from clients.agent_client import AgentClient
def main():
    # Configuración de la página
    st.set_page_config(page_title="Agente PDF", page_icon='📄')
    st.title("Agente PDF 📄")

    st.write("""
        ¡Bienvenido al Agente PDF! Este agente puede responder preguntas sobre datos extraídos de archivos PDF.
    """)

    # Inicializar el cliente de agente PDF
    agent = AgentClient('localhost', 8000)

    # Obtener `session_id` al cargar la página
    if "pdf_session_id" not in st.session_state:
        session_id = agent.get_session_id_pdf()
        if isinstance(session_id, str):
            st.session_state.pdf_session_id = session_id
        else:
            st.error("Error al configurar la sesión del agente PDF.")
            return

    # Inicializar el estado de mensajes en Streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    if user_input := st.chat_input("¿En qué puedo ayudarte?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Consulta al agente PDF con session_id
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            session_id = st.session_state.pdf_session_id
            respuesta = agent.query_pdf(user_input, session_id)
            message_placeholder.markdown(respuesta)

        st.session_state.messages.append({"role": "assistant", "content": respuesta})

    Navbar()


if __name__ == "__main__":
    main()
