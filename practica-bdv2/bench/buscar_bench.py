"""Buscadores sobre chunks_bench con la misma firma que buscar.buscar."""
import re

from modelos import cargar_modelo, cliente_supabase

_db = cliente_supabase()


def _tsquery_or(pregunta: str) -> str:
    """'¿Cuándo me pagan el aguinaldo?' -> 'cuándo | pagan | aguinaldo' (OR entre términos)."""
    palabras = [p for p in re.findall(r"\w+", pregunta.lower()) if len(p) > 2]
    return " | ".join(dict.fromkeys(palabras))


def hacer_buscador(modelo: str, estrategia: str, hibrido: bool = False):
    """Devuelve buscar(pregunta, k) -> list[{'content', 'articulo', 'similarity'}]."""
    enc = cargar_modelo(modelo)

    def buscar(pregunta: str, top_k: int = 3):
        emb = enc.encode(pregunta).tolist()
        if hibrido:
            rpc, args = f"match_bench_hibrido_{modelo}", {
                "query_embedding": emb,
                "query_text": _tsquery_or(pregunta),
                "p_estrategia": estrategia,
                "match_count": top_k,
            }
        else:
            rpc, args = f"match_bench_{modelo}", {
                "query_embedding": emb,
                "p_estrategia": estrategia,
                "match_count": top_k,
            }
        return _db.rpc(rpc, args).execute().data

    return buscar
