import os

from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Crear el modelo 
modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def buscar(pregunta:str, top_k:int = 3):
    query_embedding = modelo.encode(pregunta).tolist()
    
    respuesta = supabase.rpc("match_politicas", {
        "query_embedding": query_embedding,
        "match_count": top_k,
    }).execute()
    
    return respuesta.data

def main():
    preguntas = [
        "Tengo 3 años de antiguedad, ¿A cuantos días de vacaciones tengo derecho?",
        "¿Cuándo se paga el aguinaldo?",
        "¿Mis familiales directos pueden tener servicio médico?"
    ]
    
    """
    for p in preguntas:
            print(p)
            for r in buscar(p):
                print(r['content'], f"\nSimilaridad{r['similarity']:.2f}")
    """
    
    # Modo interactivo
    while True:
        p = input("\nPregunta: ").strip()
        if p.upper() in ('EXIT', 'SALIR', ' '):
            break
        for r in buscar(p):
            print(r['content'], f"\nSimilaridad{r['similarity']:.2f}")

if __name__ == '__main__':
    main()