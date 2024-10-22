import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

load_dotenv()

class CSVAgent:
    def __init__(self, db_path="data/csv/", local_agent: bool = False):
       
        self.db_path = db_path
        self.llm_model = None
        self.cadena = None
        self.sessions_history = {}
        self.local_agent = local_agent

        self.set_up_models()

    def set_up_models(self):
       
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("Falta la clave de OpenAI. Asegúrate de haberla configurado en el archivo .env")

        self.llm_model = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo', openai_api_key=openai_api_key)

    def set_up_db_chain(self, db_file):
        db_uri = f"sqlite:///{self.db_path}{db_file}"
        try:
            db = SQLDatabase.from_uri(db_uri)
            self.cadena = SQLDatabaseChain(llm=self.llm_model, database=db, verbose=True)

        except Exception as e:
            print(f"Error al configurar la base de datos: {str(e)}")
            raise


    def query(self, question: str):
       
        if self.cadena is None:
            return {"error": "La cadena de consulta no está inicializada. Asegúrate de configurar la base de datos correctamente."}
        
        formato = """
        Dada una pregunta del usuario:
        1. Ten en cuenta el nombre de las variables de la base de datos.
        2. Crea una consulta de SQLite3.
        3. Revisa los resultados.
        4. Devuelve el dato.
        5. Si tienes que hacer alguna aclaración o devolver cualquier texto, siempre en español.
        #{question}
        """

        consulta_sql = formato.format(question=question)
        print("Consulta SQL generada:", consulta_sql)  

        try:
            resultado = self.cadena.invoke(consulta_sql)
            return resultado
        except Exception as e:
            print(f"Error en la consulta SQL: {str(e)}")
            return {"error": f"No se pudo realizar la consulta: {str(e)}"}


    def configure_session(self):
       
        session_id = str(uuid.uuid4())
        if session_id not in self.sessions_history:
            self.sessions_history[session_id] = []
        return session_id

    def get_session_history(self, session_id):
       
        return self.sessions_history.get(session_id, [])

    def verify_session_history_exists(self, session_id):
       
        return session_id in self.sessions_history
