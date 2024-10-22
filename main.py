import os
import sqlite3
import pandas as pd
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException,status
from fastapi.params import Form
from langchain_core.documents import Document

from src.schemas.request import QueryCSVRequest, QueryPDFAgentRequest, SetUpPDFAgentRequest
from src.pdf_agent import PDFAgent
from src.csv_agent import CSVAgent
from src.utils.file_processor import load_pdfs, chunk_text




pdf_agent = PDFAgent(local_agent=True, use_refinement=False)
csv_agent = CSVAgent(local_agent=False)




app = FastAPI()
@app.get("/")
def read_root():
    return "Hello World"

@app.post("/set-up-pdf-agent",status_code=status.HTTP_201_CREATED)
def set_up_pdf_agent(files: List[UploadFile] = File(...), task_description: str = Form(...)):

    try:
        # Save the files
        for file in files:
            with open(f"data/pdf/{file.filename}", "wb") as f:
                f.write(file.file.read())

        pdf_agent.task_description = task_description

        documents = load_pdfs("data/pdf")

        chunks:list[Document] = chunk_text(documents)

        pdf_agent.set_up_vector_db(chunks)

        return {"message": "PDFAgent setup successful"}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/configure-session-pdf-agent", response_model=str)
def configure_session_pdf_agent():
    try:
        session_id = pdf_agent.configure_session()
        return {"session_id": session_id}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.post("/query-pdf-agent")
def query_pdf_agent(req: QueryPDFAgentRequest):
    try:
        if not pdf_agent.verify_session_history_exists(req.session_id):
            return  HTTPException(status_code=400, detail="Session history does not exist")
        response = pdf_agent.query(req.question, req.session_id)
        return {"response": response}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.post("/upload-csv", status_code=status.HTTP_201_CREATED)
def upload_csv(files: List[UploadFile] = File(...)):
    try:
        for file in files:
            file_location = f"data/csv/{file.filename}"
            db_file_name = os.path.splitext(file.filename)[0] + ".db"
            db_file_path = os.path.join(csv_agent.db_path, db_file_name)

            with open(file_location, "wb") as f:
                f.write(file.file.read())

            data = pd.read_csv(file_location)
            conn = sqlite3.connect(db_file_path)
            data.to_sql('data', conn, if_exists='replace', index=False)
            conn.close()

            csv_agent.set_up_db_chain(db_file_name)

        return {"message": "Archivo CSV subido y convertido exitosamente a base de datos.", "db_path": db_file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")



@app.post("/query-csv")
def query_csv(req: QueryCSVRequest):
    try:
        
        respuesta = csv_agent.query(req.question)
        if respuesta.get('result') is not None:
            return {"respuesta": respuesta['result']}
        else:
            raise HTTPException(status_code=400, detail="No se pudo procesar la consulta.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

