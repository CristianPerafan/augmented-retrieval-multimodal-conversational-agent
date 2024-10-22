from pydantic import BaseModel


class QueryPDFAgentRequest(BaseModel):
    question: str
    session_id: str

class SetUpPDFAgentRequest(BaseModel):
    initial_prompt: str

class QueryCSVRequest(BaseModel):
    question: str
