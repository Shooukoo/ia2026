import os
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer

ARCHIVO = "politicas_empresa.txt"
TABLA = "politicas_chunks"

load_dotenv()

# Crear la conexión con Supabase
cnn_supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# Crear modelo
modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

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

def main():
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", ARCHIVO)
    with open(ruta, encoding="UTF-8") as f:
        texto = f.read()
    
    chunks = crear_chunks(texto)
    
    print(f"{len(chunks)} fragmentos creados")
    
    # Codificar cada chunk generado
    embeddings = modelo.encode([c['content'] for c in chunks ])
    
    filas = []
    for c, emb in zip(chunks, embeddings):
        filas.append({
            "archivo": ARCHIVO,          
            "capitulo": c["capitulo"],                  
            "articulo": c["articulo"],                  
            "content": c["content"],          
            "embedding": emb.tolist(), 
        })
    
    # Borrar lo ingestado antes de este archivo para no duplicar filas
    cnn_supabase.table(TABLA).delete().eq("archivo", ARCHIVO).execute()
    
    # Eliminar filas de la base de datos de supabase
    # cnn_supabase.table(TABLA).delete().eq("archivo", ARCHIVO).execute()

    # Insertar en la base de datos de Supabase
    cnn_supabase.table(TABLA).insert(filas).execute()
    
    print("Filas insertadas!")
    
if __name__ == '__main__':
    main()