from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

from fastapi import Body
from src.generation.generator import Generator
from src.retrieval.retriever import Retriever

generator = Generator()
retriever = Retriever()


@app.post("/ask")
async def ask_question(data: dict = Body(...)):
    question = data.get("question")

    # 1. Retrieve relevant chunks
    retrieved_chunks = retriever.retrieve(question, top_k=5)

    # 2. Generate answer with context
    answer = generator.generate(question, retrieved_chunks.get("documents", []))

    return {
        "answer": answer,
        "retrieved": retrieved_chunks
    }