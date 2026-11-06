import os
import time
from dotenv import load_dotenv
from supabase import create_client
# from sentence_transformers import SentenceTransformer
from langchain_google_genai import GoogleGenerativeAIEmbeddings

ARCHIVO = "politicas_empresa.txt"
TABLA = "politicas_chunks_gemini"
TASK_TYPE_INDEX = "RETRIEVAL_DOCUMENT"
DIMS = 3072

load_dotenv()

# Crear la conexión con Supabase
cnn_supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# Crear modelo
modelo = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type=TASK_TYPE_INDEX,
    output_dimensionality=DIMS
)

def crear_chunks(texto:str):
    chunks = []
    capitulo_actual = None
    articulo_actual = None
    lineas_actuales:list[str] = []
    
    def cerrar_articulo():
        if articulo_actual and lineas_actuales:
            cuerpo = "\n".join(lineas_actuales)
            chunks.append({
                "capitulo": capitulo_actual,
                "articulo": articulo_actual,
                "content": f"{capitulo_actual}\n\n{articulo_actual}\n{cuerpo}"
            })
    
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith("CAPÍTULO"):
            cerrar_articulo()
            articulo_actual = None
            lineas_actuales = []
            capitulo_actual = linea
        elif linea.startswith("Artículo"):
            cerrar_articulo()
            articulo_actual = linea
            lineas_actuales = []
        elif articulo_actual:
            lineas_actuales.append(linea)
            
    cerrar_articulo()
    return chunks

def embed_en_lotes(textos: list[str], tam_lote: int = 20) -> list[list[float]]:
    todos = []

    for i in range(0, len(textos), tam_lote):
        lote = textos[i:i + tam_lote]
        
        embedding_lote = modelo.embed_documents(lote)
        
        todos.extend(embedding_lote)
        
        # Pausa
        if i + tam_lote < len(textos):
            time.sleep(0.5)
    
    return todos

def main():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), ARCHIVO)
    with open(ruta, encoding="UTF-8") as f:
        texto = f.read()
    
    chunks = crear_chunks(texto)
    
    print(f"{len(chunks)} fragmentos creados")
    
    # Codificar cada chunk generado
    textos = [c['content'] for c in chunks ]
    embeddings = embed_en_lotes(textos, 20)
    
    filas = []
    for c, emb in zip(chunks, embeddings):
        filas.append({
            "archivo": ARCHIVO,          
            "capitulo": c["capitulo"],                  
            "articulo": c["articulo"],                  
            "content": c["content"],          
            "embedding": emb,
        })
    
    # Borrar lo ingestado antes de este archivo para no duplicar filas
    cnn_supabase.table(TABLA).delete().eq("archivo", ARCHIVO).execute()
    
    # Insertar en la base de datos de Supabase
    cnn_supabase.table(TABLA).insert(filas).execute()
    
    print("Filas insertadas!")
    
if __name__ == '__main__':
    main()