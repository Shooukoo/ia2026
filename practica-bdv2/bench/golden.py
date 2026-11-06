"""Golden set para evaluar la búsqueda sobre politicas_empresa.txt.

Cada pregunta lleva el artículo correcto y una evidencia corta que debe
aparecer en el texto recuperado. Las preguntas están redactadas con palabras
distintas a las del documento. Al importar el módulo se verifica que cada
evidencia exista literalmente en el artículo indicado.
"""
import os
import re

ARCHIVO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "politicas_empresa.txt")

GOLDEN = [
    # --- Las 7 del enunciado ---
    {"pregunta": "¿Cuántos días de vacaciones me tocan después de 3 años?", "articulo": "Artículo 7", "evidencia": "Cada año adicional suma 2 días"},
    {"pregunta": "¿Cuándo me pagan el aguinaldo?", "articulo": "Artículo 14", "evidencia": "a más tardar el 20 de diciembre"},
    {"pregunta": "Mi papá falleció, ¿cuántos días me dan?", "articulo": "Artículo 21", "evidencia": "fallecimiento del cónyuge, padres, hijos o hermanos"},
    {"pregunta": "¿Puedo trabajar desde mi casa?", "articulo": "Artículo 35", "evidencia": "trabajar desde casa hasta 2 días por semana"},
    {"pregunta": "Llegué tarde varias veces, ¿qué pasa?", "articulo": "Artículo 5", "evidencia": "Tres retardos en un mismo mes"},
    {"pregunta": "¿Cuánto me pagan si trabajo el 16 de septiembre?", "articulo": "Artículo 19", "evidencia": "tres veces su salario diario"},
    {"pregunta": "¿Me pueden pagar mis vacaciones en dinero en vez de tomarlas?", "articulo": "Artículo 10", "evidencia": "No se pueden vender ni cambiar por dinero"},
    # --- Nuevas ---
    {"pregunta": "¿Qué porcentaje extra me pagan cuando salgo de descanso largo?", "articulo": "Artículo 8", "evidencia": "prima vacacional del 30%"},
    {"pregunta": "Me voy a casar, ¿me dan días libres?", "articulo": "Artículo 20", "evidencia": "5 días hábiles con goce de sueldo por su matrimonio"},
    {"pregunta": "¿Puedo faltar el día que cumplo años?", "articulo": "Artículo 24", "evidencia": "semana de su cumpleaños"},
    {"pregunta": "Estoy embarazada, ¿cuánto tiempo me dan antes y después del parto?", "articulo": "Artículo 32", "evidencia": "12 semanas de licencia"},
    {"pregunta": "Acaba de nacer mi bebé, ¿qué permiso me toca como papá?", "articulo": "Artículo 34", "evidencia": "10 días hábiles con goce de sueldo por el nacimiento"},
    {"pregunta": "¿Cuánto me pagan si me quedo más horas de las normales?", "articulo": "Artículo 38", "evidencia": "se pagan al doble del salario por hora"},
    {"pregunta": "¿La empresa me ayuda con el gasto de luz si trabajo en casa?", "articulo": "Artículo 36", "evidencia": "compensación mensual de 400 pesos"},
    {"pregunta": "Tengo cita con el dentista, ¿me dan permiso?", "articulo": "Artículo 22", "evidencia": "hasta 4 horas con goce de sueldo"},
    {"pregunta": "Amanecí enfermo y no puedo ir, ¿a qué hora debo avisar?", "articulo": "Artículo 29", "evidencia": "antes de las 10:00 horas"},
    {"pregunta": "¿Puedo pedir un tiempo sin sueldo para viajar?", "articulo": "Artículo 27", "evidencia": "hasta 30 días naturales al año"},
    {"pregunta": "Mi niño tiene fiebre, ¿puedo quedarme a cuidarlo?", "articulo": "Artículo 25", "evidencia": "hasta 3 días al año"},
    {"pregunta": "¿Hasta cuándo puedo usar mis vacaciones antes de perderlas?", "articulo": "Artículo 11", "evidencia": "seis meses siguientes"},
    {"pregunta": "¿Cuántas ausencias sin avisar me pueden costar el empleo?", "articulo": "Artículo 6", "evidencia": "más de tres faltas injustificadas"},
    # --- Sin respuesta en el documento (prueba del umbral) ---
    {"pregunta": "¿Cuál es el código de vestimenta?", "articulo": None, "evidencia": None},
    {"pregunta": "¿Tengo seguro de gastos médicos mayores para mi familia?", "articulo": None, "evidencia": None},
]

# Preguntas de intercambio / validación: NO usar para ajustar el chunking.
GOLDEN_EXTRA = [
    {"pregunta": "¿Con quién hablo si no entiendo alguna de estas reglas?", "articulo": "Artículo 40", "evidencia": "extensión 120"},
    {"pregunta": "¿Hasta qué hora trabajo en Nochebuena?", "articulo": "Artículo 18", "evidencia": "termina a las 14:00 horas"},
    {"pregunta": "Si renuncio en noviembre, ¿me pagan algo del aguinaldo?", "articulo": "Artículo 15", "evidencia": "parte proporcional dentro del finiquito"},
    {"pregunta": "Trabajo en el almacén, ¿puedo hacer home office?", "articulo": "Artículo 35", "evidencia": "no son elegibles para trabajo remoto"},
    {"pregunta": "Me voy a titular, ¿me dan permiso ese día?", "articulo": "Artículo 26", "evidencia": "un día con goce de sueldo"},
]


def _articulos(texto: str) -> dict[str, str]:
    """Devuelve {'Artículo N': texto_del_artículo}."""
    partes = re.split(r"(?m)^(Artículo \d+)\.", texto)
    return {partes[i]: partes[i + 1] for i in range(1, len(partes), 2)}


def _verificar():
    with open(ARCHIVO, encoding="UTF-8") as f:
        arts = _articulos(f.read())
    for g in GOLDEN + GOLDEN_EXTRA:
        if g["evidencia"] is None:
            continue
        cuerpo = arts[g["articulo"]]
        assert g["evidencia"] in cuerpo, f"Evidencia no está en {g['articulo']}: {g['evidencia']!r}"


_verificar()

if __name__ == "__main__":
    print(f"OK: {sum(1 for g in GOLDEN if g['evidencia'])} preguntas con respuesta, "
          f"{sum(1 for g in GOLDEN if not g['evidencia'])} sin respuesta, {len(GOLDEN_EXTRA)} extra")
