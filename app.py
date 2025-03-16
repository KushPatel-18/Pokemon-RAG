from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag_utils import search_pokemon

app = FastAPI()

# Enable CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin (Change this to a specific domain in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allows all headers
)

@app.get("/search/")
async def search(query: str):
    return {"results": search_pokemon("pokemon-index", query)}
