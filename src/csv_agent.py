import os
import sqlite3
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

load_dotenv()

class CSVAgent:
    def __init__(self, db_path="data/csv/", local_agent=False): 
        self.db_path = db_path
        self.local_agent = local_agent  
        self.llm_model = None
        self.cadena = None
        self.current_db = None

        self.set_up_models()
        self.load_existing_db()

    def set_up_models(self):
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("Falta la clave de OpenAI. Asegúrate de haberla configurado en el archivo .env")

        self.llm_model = ChatOpenAI(temperature=0,top_p=0.1,max_tokens=200, model_name='gpt-3.5-turbo', openai_api_key=openai_api_key)

    def load_existing_db(self):
       
        try:

            for filename in os.listdir(self.db_path):
                if filename.endswith(".db"):
                    print(f"Archivo .db encontrado: {filename}. Configurando cadena...")
                    self.set_up_db_chain(filename)
                    break
        except Exception as e:
            print(f"Error al cargar la base de datos existente: {e}")

    def set_up_db_chain(self, db_file):

        if self.cadena is None or self.current_db != db_file:
            db_uri = f"sqlite:///{self.db_path}{db_file}"
            print(f"Conectando a la base de datos en: {db_uri}")
            try:
                db = SQLDatabase.from_uri(db_uri)
                self.cadena = SQLDatabaseChain(llm=self.llm_model, database=db, verbose=True)
                self.current_db = db_file
                print("Cadena de consulta inicializada correctamente.")
            except Exception as e:
                print(f"Error al inicializar la cadena: {e}")
                raise
    
    def query(self, question: str):
        if self.cadena is None:
            return {"error": "La cadena de consulta no está inicializada. Por favor cargue el documento CSV primero."}

        formato = f"""
        Dada una pregunta del usuario:
        1. Ten en cuenta los nombres de las columnas.
        2. Crea una consulta de SQLite3 sin usar LIMIT.
        3. Revisa y estructura la consulta para asegurar que no haya errores de sintaxis.
        4. Si es necesario, ordena o limita los resultados directamente en la consulta, pero evita el uso de múltiples declaraciones en una sola línea.
        5. Devuelve el resultado en formato claro y conciso.
        6. Si tienes que hacer alguna aclaración o devolver cualquier texto, siempre en español.
        
        Pregunta del usuario:
        {question}
        """

        consulta_sql = formato.format(question=question)

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
