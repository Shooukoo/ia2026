""" Ejercicio.
Leer de un documento txt, cada linea se convertira en un vector y se guardara.
Después se buscara de acuerdo al contenido y se mostraran los vectores.
"""

from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
import json
import os

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE-URL"],
    os.environ["SUPABASE-KEY"]
)

modelo = SentenceTransformer('intfloat/multilingual-e5-small')

ARCHIVO = "datos.txt"
VALORES_A_MOSTRAR = 10


def leer_lineas(ruta: str) -> list[str]:
    with open(ruta, "r", encoding="utf-8") as archivo:
        return [linea.strip() for linea in archivo if linea.strip()]


def guardar(lineas: list[str]) -> int:
    insertados = 0
    for linea in lineas:
        existente = supabase.table("documents").select("id").eq("content", linea).execute()
        if existente.data:
            continue
        embedding = modelo.encode(linea).tolist()
        supabase.table("documents").insert({
            "content": linea,
            "embedding": embedding,
        }).execute()
        insertados += 1
    return insertados


def buscar(pregunta: str, top_k: int = 4):
    query_embedding = modelo.encode(pregunta).tolist()
    resultado = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_count": top_k,
        "match_threshold": 0.0
    }).execute()
    return resultado.data


def obtener_vectores(ids: list[int]) -> dict[int, list[float]]:
    # match_documents no devuelve el vector, asi que se pide a la tabla por id
    filas = supabase.table("documents").select("id, embedding").in_("id", ids).execute()
    # Supabase devuelve el vector como texto  json.loads lo vuelve lista
    return {fila["id"]: json.loads(fila["embedding"]) for fila in filas.data}


def mostrar(resultados: list[dict]):
    # Obtiene los vectores de todos los resultados en una sola consulta
    vectores = obtener_vectores([r["id"] for r in resultados])
    for posicion, r in enumerate(resultados, start=1):
        # Vector correspondiente al documento encontrado
        vector = vectores[r["id"]]
        # Imprime la posición y la similitud coseno con 4 decimales
        print(f"\n{posicion}. Similitud: {r['similarity']:.4f}")
        print(f"   Contenido: {r['content']}")
        print(f"   Dimensiones del vector: {len(vector)}")
        print(f"   Vector: {vector[:VALORES_A_MOSTRAR]}")


lineas = leer_lineas(ARCHIVO)

print(f"Lineas leidas de {ARCHIVO}: {len(lineas)}")

insertados = guardar(lineas)

print(f"Número de documentos insertados: {insertados}")

# Pregunta
pregunta = "¿Cómo guardo el historial de cambios de mi código?"

print(f"\nPregunta: {pregunta}")

result = buscar(pregunta, 3)

mostrar(result)
