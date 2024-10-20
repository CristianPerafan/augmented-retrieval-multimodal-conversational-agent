from fastapi import FastAPI

from src.schemas.request import QueryRequest

app = FastAPI()


@app.get("/")
def read_root():
    return "Hello World"

@app.post("/query")
def query(req: QueryRequest):
    return "Query: " + req.query


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)