"""Corre el golden set contra cada configuración y escribe resultados.md."""
import json
import os
import statistics

from buscar_bench import hacer_buscador
from chunkers import ESTRATEGIAS
from golden import GOLDEN, GOLDEN_EXTRA
from modelos import MODELOS

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
K = 3


def evaluar(golden, buscar, k=3):
    preguntas = [g for g in golden if g["evidencia"]]
    hits, rr = 0, 0.0
    for g in preguntas:
        resultados = buscar(g["pregunta"], k)
        posiciones = [i for i, r in enumerate(resultados, 1) if g["evidencia"] in r["content"]]
        if posiciones:
            hits += 1
            rr += 1 / posiciones[0]
    n = len(preguntas)
    return {"hit@k": hits / n, "mrr": rr / n, "hits": hits, "n": n}


def umbral(buscar):
    """Similitud top-1 media de preguntas respondibles vs. máxima de las sin respuesta."""
    con = [buscar(g["pregunta"], 1)[0]["similarity"] for g in GOLDEN if g["evidencia"]]
    sin = [buscar(g["pregunta"], 1)[0]["similarity"] for g in GOLDEN if not g["evidencia"]]
    return statistics.mean(con), min(con), max(sin)


def main():
    with open(os.path.join(RAIZ, "data", "tiempos_ingesta.json"), encoding="UTF-8") as f:
        tiempos = json.load(f)

    filas = []  # (config dict, resultado)

    # (a) Línea base: ingesta.py + buscar.py originales (politicas_chunks)
    try:
        from buscar import buscar as buscar_base
        filas.append((
            {"estrategia": "articulo (línea base)", "modelo": "multi", "busqueda": "vectorial", "ingesta": None},
            evaluar(GOLDEN, buscar_base, K),
        ))
    except Exception as e:  # tabla original vacía o sin RPC
        print(f"Línea base omitida: {e}")

    # (b-d) Matriz completa: estrategia x modelo x tipo de búsqueda
    buscadores = {}
    for estrategia in ESTRATEGIAS:
        for modelo in MODELOS:
            for hibrido in (False, True):
                b = hacer_buscador(modelo, estrategia, hibrido)
                buscadores[(estrategia, modelo, hibrido)] = b
                r = evaluar(GOLDEN, b, K)
                filas.append((
                    {"estrategia": estrategia, "modelo": modelo,
                     "busqueda": "híbrida" if hibrido else "vectorial",
                     "ingesta": tiempos[estrategia][modelo]},
                    r,
                ))
                print(f"{estrategia:14s} {modelo:7s} {'híbrida' if hibrido else 'vectorial':9s} "
                      f"Hit@3={r['hit@k']:.2f} MRR={r['mrr']:.2f}")

    # Mejor configuración -> validación con preguntas de intercambio (no usadas para ajustar)
    mejor_cfg, mejor_r = max(
        (f for f in filas if f[0]["ingesta"] is not None), key=lambda f: (f[1]["mrr"], f[1]["hit@k"])
    )
    h = mejor_cfg["busqueda"] == "híbrida"
    extra = evaluar(GOLDEN_EXTRA, buscadores[(mejor_cfg["estrategia"], mejor_cfg["modelo"], h)], K)

    # (e) Umbral de similitud, por modelo, con chunking por artículo
    umbrales = {m: umbral(buscadores[("articulo", m, False)]) for m in MODELOS}

    # --- resultados.md ---
    L = []
    L.append("# Resultados del banco de pruebas\n")
    L.append(f"Golden set: {mejor_r['n']} preguntas con respuesta (Hit@{K}, MRR). "
             f"Una diferencia de 1 pregunta = {1 / mejor_r['n']:.2f} de Hit@{K}: **es ruido**.\n")
    L.append("| Chunking | Modelo | Búsqueda | Hit@3 | MRR | Ingesta (s) | Costo |")
    L.append("|---|---|---|---|---|---|---|")
    for c, r in filas:
        ing = "—" if c["ingesta"] is None else f"{c['ingesta']:.2f}"
        L.append(f"| {c['estrategia']} | {MODELOS[c['modelo']][0]} | {c['busqueda']} | "
                 f"{r['hits']}/{r['n']} ({r['hit@k']:.2f}) | {r['mrr']:.3f} | {ing} | $0 (local) |")
    L.append("\nCosto: todos los modelos corren localmente, así que el costo en dinero es $0; "
             "el costo real es tiempo de cómputo y memoria. Contextual retrieval no se midió: "
             "añadiría una llamada a un LLM por chunk en cada ingesta.\n")
    L.append(f"## Mejor configuración (por MRR): {mejor_cfg['estrategia']} + "
             f"{MODELOS[mejor_cfg['modelo']][0]} + {mejor_cfg['busqueda']}\n")
    L.append(f"Validación con {extra['n']} preguntas de intercambio (no usadas para ajustar): "
             f"Hit@3 = {extra['hits']}/{extra['n']}, MRR = {extra['mrr']:.3f}. "
             f"Con tan pocas preguntas es solo orientativo.\n")
    L.append("## Umbral de similitud (chunking por artículo, búsqueda vectorial)\n")
    L.append("| Modelo | Similitud top-1 media (con respuesta) | Mínima (con respuesta) | Máxima (sin respuesta) |")
    L.append("|---|---|---|---|")
    for m, (media, minimo, maximo) in umbrales.items():
        L.append(f"| {MODELOS[m][0]} | {media:.3f} | {minimo:.3f} | {maximo:.3f} |")
    L.append("\nUn umbral solo separa bien si la máxima de las preguntas sin respuesta queda por debajo "
             "de la mínima de las que sí tienen respuesta.\n")

    with open(os.path.join(RAIZ, "docs", "resultados.md"), "w", encoding="UTF-8") as f:
        f.write("\n".join(L))
    print("\nEscrito resultados.md")


if __name__ == "__main__":
    main()
