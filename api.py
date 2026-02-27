from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import psycopg2
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RAG API")

# Load embedding model once at startup
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

class QueryRequest(BaseModel):
    question: str
    use_llm: bool = True

class QueryResponse(BaseModel):
    question: str
    fragments: list[dict]
    answer: str | None = None


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    # 1. Generate embedding
    vector = model.encode(req.question).tolist()

    # 2. Search top 3 fragments in pgvector
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, id_document, texte_fragment,
                   1 - (vecteur <=> %s::vector) AS similarity
            FROM embeddings
            ORDER BY vecteur <=> %s::vector
            LIMIT 3
            """,
            (vector, vector),
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    fragments = [
        {"id": r[0], "id_document": r[1], "texte_fragment": r[2], "similarity": round(float(r[3]), 4)}
        for r in rows
    ]

    if not fragments:
        raise HTTPException(status_code=404, detail="No fragments found")

    # 3. Optional LLM answer via OpenRouter
    answer = None
    if req.use_llm:
        context = "\n\n".join(f["texte_fragment"] for f in fragments)
        prompt = f"""Vous êtes un assistant expert en boulangerie et ingrédients.
Répondez à la question en vous basant uniquement sur le contexte fourni.

Contexte:
{context}

Question: {req.question}

Réponse:"""

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct"),
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 512,
                },
            )
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"].strip()
            else:
                answer = f"LLM error: {resp.status_code} - {resp.text}"

    return QueryResponse(question=req.question, fragments=fragments, answer=answer)


@app.get("/health")
def health():
    return {"status": "ok"}
