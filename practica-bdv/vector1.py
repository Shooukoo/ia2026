from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
import os

load_dotenv()

# Crear cliente de supabase
supabase = create_client(
    os.environ["SUPABASE-URL"],
    os.environ["SUPABASE-KEY"]
)

modelo = SentenceTransformer('intfloat/multilingual-e5-small')

documentos = [
    # Bases de datos vectoriales
    "Una base de datos vectorial almacena embeddings y permite buscar información por similitud semántica en lugar de coincidencia exacta de palabras.",
    "Las bases de datos vectoriales se utilizan en Inteligencia Artificial Agéntica para dar memoria de largo plazo a los agentes.",
    "pgvector es una extensión de PostgreSQL que agrega el tipo de dato vector y operadores para calcular distancias entre embeddings.",
    "Supabase ofrece PostgreSQL administrado con pgvector, lo que permite guardar documentos y sus embeddings en la misma tabla.",
    "La similitud coseno mide el ángulo entre dos vectores: un valor cercano a 1 indica que los textos tienen un significado parecido.",
    "Los índices HNSW e IVFFlat aceleran la búsqueda de vecinos más cercanos sacrificando un poco de exactitud a cambio de velocidad.",

    # Embeddings y modelos de lenguaje
    "Un embedding es una representación numérica de un texto en forma de vector, donde textos con significado similar quedan cerca entre sí.",
    "El modelo multilingual-e5-base genera embeddings de 768 dimensiones y funciona con más de cien idiomas, incluido el español.",
    "Los modelos de lenguaje grandes (LLM) predicen la siguiente palabra de un texto a partir de patrones aprendidos durante su entrenamiento.",
    "La tokenización divide un texto en unidades más pequeñas llamadas tokens antes de que el modelo de lenguaje lo procese.",
    "La ventana de contexto es la cantidad máxima de tokens que un modelo de lenguaje puede considerar en una sola consulta.",

    # RAG y agentes
    "RAG (generación aumentada por recuperación) consiste en buscar documentos relevantes y entregarlos al modelo para que responda con información actualizada.",
    "Dividir los documentos largos en fragmentos pequeños (chunking) mejora la precisión de la recuperación en un sistema RAG.",
    "Un agente de inteligencia artificial es un sistema que planifica, usa herramientas y toma decisiones para cumplir un objetivo de forma autónoma.",
    "Las alucinaciones ocurren cuando un modelo de lenguaje genera información falsa pero la presenta con seguridad, como si fuera cierta.",
    "El prompt engineering es la práctica de redactar instrucciones claras para obtener mejores respuestas de un modelo de lenguaje.",

    # Aprendizaje automático
    "El aprendizaje supervisado entrena un modelo con ejemplos etiquetados para que aprenda a predecir la etiqueta de datos nuevos.",
    "El aprendizaje no supervisado busca patrones y agrupa datos similares sin necesidad de etiquetas previas.",
    "Una red neuronal está formada por capas de neuronas artificiales que ajustan sus pesos para reducir el error de sus predicciones.",
    "El sobreajuste ocurre cuando un modelo memoriza los datos de entrenamiento y falla al generalizar con datos que nunca ha visto.",
    "La arquitectura Transformer usa mecanismos de atención para relacionar todas las palabras de una oración entre sí.",

    # Temas no relacionados (sirven de contraste al probar la búsqueda semántica)
    "El mole poblano es un platillo mexicano que combina chiles secos, especias y chocolate en una salsa espesa.",
    "La fotosíntesis es el proceso por el cual las plantas convierten la luz solar, el agua y el dióxido de carbono en glucosa y oxígeno.",
    "La selección mexicana de fútbol juega sus partidos de local en el Estadio Azteca de la Ciudad de México.",
    "Dormir entre siete y ocho horas diarias mejora la memoria, la concentración y el estado de ánimo.",
    "El río Amazonas es el más caudaloso del mundo y atraviesa la selva tropical más extensa del planeta.",
    "La Revolución Mexicana comenzó en 1910 como un levantamiento contra la dictadura de Porfirio Díaz.",
]

"""

for doc in documentos:
    embedding = modelo.encode(doc).tolist()
    supabase.table("documents").insert({
        "content": doc,
        "embedding": embedding,
    }).execute()
    
print(f"Número de documentos insertados {len(documentos)}")

"""

def buscar(pregunta:str, top_k: int = 4):
    query_embedding = modelo.encode(pregunta).tolist()
    resultado = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_count": top_k,
        "match_threshold": 0.0
    }).execute()
    return resultado.data

# Pregunta
pregunta = "¿Para que es una base da datos vectorial?"
result = buscar(pregunta, 3)

for r in result:
    print(r)

""" Ejercicio.
Leer de un documento txt, cada linea se convertira en un vector y se guardara. Después se buscara de acuerdo al contenido y se mostraran los vectores.
"""
