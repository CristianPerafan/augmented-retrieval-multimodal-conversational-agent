import requests


class AgentClient:
    def __init__(self, host, port):
        self.url = f"http://{host}:{port}"

    def query_csv(self, query):
        try:
            response = requests.post(f"{self.url}/query-csv", json={"question": query})
            return response.json().get("respuesta")
        except requests.exceptions.RequestException as e:
            return f"Ocurrió un error al procesar la consulta: {str(e)}"

    def get_session_id_pdf(self):
        try:
            response = requests.get(f"{self.url}/configure-session-pdf-agent")
            return response.json().get("session_id")
        except requests.exceptions.RequestException as e:
            return f"Ocurrió un error al configurar la sesión: {str(e)}"

    def query_pdf(self, query, session_id):
        try:
            response = requests.post(f"{self.url}/query-pdf-agent", json={"question": query, "session_id": session_id})
            return response.json().get("response")
        except requests.exceptions.RequestException as e:
            return f"Ocurrió un error al procesar la consulta: {str(e)}"