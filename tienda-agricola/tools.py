from langchain.tools import tool
import json

@tool
def calcular_dosis(hectareas: float, litros_por_ha: float) -> str:
    """
    Calcula la cantidad total de producto (en litros) necesaria para tratar una superficie.
    Usar cuando el usuario pregunte cuánto producto necesita, cuánto debe comprar
    o qué dosis aplicar para un terreno, por ejemplo "¿cuánto herbicida necesito para 5 hectáreas?".

    Args:
        hectareas: Superficie a tratar, en hectáreas.
        litros_por_ha: Dosis recomendada del producto, en litros por hectárea.
    """
    return f"{hectareas * litros_por_ha:.2f} litros"