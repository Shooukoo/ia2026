"""Tres estrategias de chunking: por artículo, tamaño fijo y tamaño fijo con traslape.

Cada función recibe el texto completo y devuelve una lista de
{"articulo": str | None, "content": str}.
"""
import bisect
import os
import re

ARCHIVO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "politicas_empresa.txt")

TAM = 400
TRASLAPE = 80


def por_articulo(texto: str) -> list[dict]:
    """Un chunk por artículo, con su capítulo al inicio (igual que ingesta.py)."""
    chunks = []
    capitulo = articulo = None
    lineas: list[str] = []

    def cerrar():
        if articulo and lineas:
            chunks.append({
                "articulo": articulo,
                "content": f"{capitulo}\n\n{articulo}\n" + "\n".join(lineas),
            })

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith("CAPÍTULO"):
            cerrar()
            articulo, lineas, capitulo = None, [], linea
        elif linea.startswith("Artículo"):
            cerrar()
            articulo, lineas = linea, []
        elif articulo:
            lineas.append(linea)
    cerrar()
    return chunks


def _cuerpo_plano(texto: str) -> str:
    """Texto desde el primer capítulo, sin líneas en blanco."""
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    inicio = next(i for i, l in enumerate(lineas) if l.startswith("CAPÍTULO"))
    return "\n".join(lineas[inicio:])


def _ventanas(texto: str, tam: int, paso: int) -> list[dict]:
    # Posición de cada encabezado "Artículo N." para etiquetar cada chunk por su inicio
    marcas = [(m.start(), m.group(0).strip()) for m in re.finditer(r"(?m)^Artículo \d+\.[^\n]*", texto)]
    posiciones = [p for p, _ in marcas]
    chunks = []
    for ini in range(0, len(texto), paso):
        trozo = texto[ini:ini + tam]
        if not trozo.strip():
            continue
        i = bisect.bisect_right(posiciones, ini) - 1
        chunks.append({"articulo": marcas[i][1] if i >= 0 else None, "content": trozo})
        if ini + tam >= len(texto):
            break
    return chunks


def tamano_fijo(texto: str, n: int = TAM) -> list[dict]:
    return _ventanas(_cuerpo_plano(texto), n, n)


def tamano_fijo_traslape(texto: str, n: int = TAM, overlap: int = TRASLAPE) -> list[dict]:
    return _ventanas(_cuerpo_plano(texto), n, n - overlap)


ESTRATEGIAS = {
    "articulo": por_articulo,
    "fijo": tamano_fijo,
    "fijo_traslape": tamano_fijo_traslape,
}


def cargar_texto() -> str:
    with open(ARCHIVO, encoding="UTF-8") as f:
        return f.read()


if __name__ == "__main__":
    from golden import GOLDEN, GOLDEN_EXTRA

    texto = cargar_texto()
    for nombre, fn in ESTRATEGIAS.items():
        chunks = fn(texto)
        partidas = [
            g["evidencia"] for g in GOLDEN + GOLDEN_EXTRA
            if g["evidencia"] and not any(g["evidencia"] in c["content"] for c in chunks)
        ]
        print(f"{nombre:14s} {len(chunks):3d} chunks | evidencias partidas: {len(partidas)}")
        for e in partidas:
            print("   -", e)
