from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.params import Form
from langchain_core.documents import Document

from src.schemas.request import QueryPDFAgentRequest, SetUpPDFAgentRequest
from src.pdf_agent import PDFAgent
from src.utils.file_processor import load_pdfs, chunk_text




pdf_agent = PDFAgent(local_agent=True)




app = FastAPI()
@app.get("/")
def read_root():
    return "Hello World"

@app.post("/set-up-pdf-agent")
def set_up_pdf_agent(files: List[UploadFile] = File(...), task_description: str = Form(...)):
    # Save the files
    for file in files:
        with open(f"data/pdf/{file.filename}", "wb") as f:
            f.write(file.file.read())

    pdf_agent.task_description = task_description

    documents = load_pdfs("data/pdf")

    chunks:list[Document] = chunk_text(documents)

    pdf_agent.set_up_vector_db(chunks)

@app.get("/configure-session-pdf-agent", response_model=str)
def configure_session_pdf_agent():
    session_id = pdf_agent.configure_session()
    return str(session_id)

@app.post("/query-pdf-agent")
def query_pdf_agent(req: QueryPDFAgentRequest):
    if not pdf_agent.verify_session_history_exists(req.session_id):
        return  HTTPException(status_code=400, detail="Session history does not exist")
    response = pdf_agent.query(req.question, req.session_id)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

