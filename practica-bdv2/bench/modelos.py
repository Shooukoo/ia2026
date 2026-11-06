"""Modelos de embeddings del banco de pruebas y su columna en chunks_bench."""
import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client

load_dotenv()

# clave -> (nombre en Hugging Face, columna en chunks_bench, dimensiones)
MODELOS = {
    "minilm": ("sentence-transformers/all-MiniLM-L6-v2", "emb_minilm", 384),
    "multi": ("paraphrase-multilingual-MiniLM-L12-v2", "emb_multi", 384),
    "bge": ("BAAI/bge-m3", "emb_bge", 1024),
}

TABLA = "chunks_bench"

_cache: dict[str, SentenceTransformer] = {}


def cargar_modelo(clave: str) -> SentenceTransformer:
    if clave not in _cache:
        # CPU: la GPU (3.7 GB) no alcanza para bge-m3 y así los tiempos son comparables
        _cache[clave] = SentenceTransformer(MODELOS[clave][0], device="cpu")
    return _cache[clave]


def cliente_supabase():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
