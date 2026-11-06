"""Ingesta del banco de pruebas: estrategia de chunking x modelo de embeddings.

Para cada estrategia inserta los chunks en chunks_bench y llena la columna de
cada modelo. Mide el tiempo de ingesta (encode + escritura) por combinación y
lo guarda en tiempos_ingesta.json.
"""
import json
import os
import time

from chunkers import ESTRATEGIAS, cargar_texto
from modelos import MODELOS, TABLA, cargar_modelo, cliente_supabase

SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tiempos_ingesta.json")


def main():
    db = cliente_supabase()
    texto = cargar_texto()

    # Cargar modelos antes de medir, para no contar la descarga/carga en la ingesta
    for clave in MODELOS:
        print(f"Cargando {MODELOS[clave][0]} ...")
        cargar_modelo(clave)

    tiempos: dict[str, dict[str, float]] = {}

    for estrategia, crear in ESTRATEGIAS.items():
        chunks = crear(texto)
        print(f"\n[{estrategia}] {len(chunks)} chunks")

        # Re-ingesta limpia de esta estrategia
        db.table(TABLA).delete().eq("estrategia", estrategia).execute()
        filas = [{"estrategia": estrategia, "articulo": c["articulo"], "content": c["content"]} for c in chunks]
        ids = [r["id"] for r in db.table(TABLA).insert(filas).execute().data]
        tiempos[estrategia] = {}

        for clave, (nombre, columna, _dim) in MODELOS.items():
            modelo = cargar_modelo(clave)
            t0 = time.perf_counter()
            embs = modelo.encode([c["content"] for c in chunks])
            # upsert por id para llenar solo la columna del modelo
            lote = [
                {"id": i, "estrategia": estrategia, "articulo": c["articulo"],
                 "content": c["content"], columna: e.tolist()}
                for i, c, e in zip(ids, chunks, embs)
            ]
            db.table(TABLA).upsert(lote, on_conflict="id").execute()
            tiempos[estrategia][clave] = round(time.perf_counter() - t0, 2)
            print(f"  {clave:7s} {tiempos[estrategia][clave]:7.2f} s")

    with open(SALIDA, "w", encoding="UTF-8") as f:
        json.dump(tiempos, f, indent=2)
    print(f"\nTiempos guardados en {os.path.basename(SALIDA)}")


if __name__ == "__main__":
    main()
