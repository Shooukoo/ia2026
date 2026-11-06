import os
import psycopg
import psycopg.rows

from dotenv import load_dotenv

class LongTermMemory():
    def __init__(self):
        self.database_url = os.environ["DATABASE-URL"]

    # Obtener conexión a la base de datos
    def get_conection(self):
        return psycopg.connect(self.database_url, row_factory=psycopg.rows.dict_row)
    
    # Obtener las memorias
    def get_long_term_memory(self, user_id:str, limit:int=20):
        with self.get_conection() as conection, conection.cursor() as cur:
            cur.execute(
                """
                    select created_at, memory
                    from public."Memorias"
                    where user_id = %s
                    order by created_at desc
                    limit %s
                """,
                (
                    user_id,
                    limit
                )
            )
            # Regresar el resultado de la consulta
            return cur.fetchall()
    
    # Insertar memorias
    def insert_long_term_memory(self, user_id:str, memory:str):
        print(f"Insertar memorias del usuario: {user_id} \n con mensaje: {memory}")
        # Verificar que la memoria no este vacia
        if memory is None or memory.strip() == '':
            return {"ok": False, "error": "La memoria está vacía"}

        with self.get_conection() as conection, conection.cursor() as cur:
            cur.execute(
                """
                    insert into public."Memorias"(user_id, memory)
                    values(%s, %s)
                """,
                (
                    user_id,
                    memory
                )
            )
        return {"ok": True}

    # Dar formato a las memorias (orden cronológico, una línea por memoria)
    def format_memories(self, memories):
        if not memories:
            return ""

        lineas = []
        for m in sorted(memories, key=lambda m: m['created_at']):
            # Colapsar saltos de línea/espacios internos para que cada memoria ocupe una sola línea
            memoria = " ".join(m['memory'].split())
            lineas.append(f"- [{m['created_at']:%Y-%m-%d}] {memoria}")

        return "\n".join(lineas)
    
        
#if __name__ == '__main__':
#    load_dotenv()
#    ltm = LongTermMemory()
    # ltm.insert_long_term_memory(1, "Memoria creada desde código en python")
#    result = ltm.get_long_term_memory(user_id="1")
#    print(ltm.format_memories(result))
