from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import json
import os

from memoria_simple import SimpleMemory
from tools import Tools

load_dotenv()

MEMORY_MAX_MESSAGES = 10
MAX_TOOL_ROUNDS = 5

client = Groq(api_key=os.getenv("API-KEY-MODEL"))
memory = SimpleMemory(MEMORY_MAX_MESSAGES)
tools_instance = Tools()

AVAILABLE_FUNCTIONS = {
    "analizar_dia": tools_instance.analizar_dia,
    "buscar_por_tema": tools_instance.buscar_por_tema,
}

_RFC = ("DEBEN estar en formato RFC3339 con offset de zona horaria. "
        "EJEMPLO: 2026-09-09T00:00:00-06:00. Si el usuario no da fecha y ya hay un rango en memoria, "
        "OMITE estos parametros y se usará el rango guardado.")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analizar_dia",
            "description": "Analiza la agenda en un intervalo: total de reuniones, horas ocupadas, primera y ultima reunion y huecos libres. "
                           "Usala para preguntas de tiempo libre, horas ocupadas o resumen del dia. " + _RFC,
            "parameters": {
                "type": "object",
                "properties": {
                    "time_ini": {"type": "string", "description": "Inicio del intervalo en RFC3339."},
                    "time_end": {"type": "string", "description": "Fin del intervalo en RFC3339."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_por_tema",
            "description": "Cuenta y lista las reuniones que contienen un tema (busqueda de texto libre en titulo o descripcion). "
                           "Usala para preguntas como 'cuantas reuniones de cliente tuve'. " + _RFC,
            "parameters": {
                "type": "object",
                "properties": {
                    "time_ini": {"type": "string", "description": "Inicio del intervalo en RFC3339."},
                    "time_end": {"type": "string", "description": "Fin del intervalo en RFC3339."},
                    "tema": {"type": "string", "description": "Palabra clave a buscar, ej. 'cliente'."},
                },
                "required": ["tema"],
            },
        },
    },
]

SYSTEM_PROMPT = (
    "Eres un asistente de productividad. El usuario NO quiere que crees ni borres nada, solo que analices su agenda. "
    "NUNCA inventes número de reuniones. Siempre llama a analizar_dia o buscar_por_tema. "
    "Si no hay datos, di 'No se encontraron eventos' no inventes. "
    "Si el usuario hace una pregunta de seguimiento sin dar fecha, reutiliza el rango guardado en memoria sin preguntar la fecha de nuevo. "
    "Al responder con analizar_dia incluye SIEMPRE: total de reuniones, horas ocupadas, primera y última reunión y huecos libres. "
    "Al responder con buscar_por_tema incluye SIEMPRE: el tema, el total de reuniones y la lista de títulos. "
    "Si el usuario pregunta por reuniones 'próximas' o sin dar fecha ni rango en memoria, consulta desde ahora hasta 7 días adelante. "
    "Responde siempre en español de forma clara y concisa."
)


def system_message():
    hoy = datetime.now().astimezone()
    texto = f"{SYSTEM_PROMPT}\nFecha y hora actual: {hoy.isoformat(timespec='minutes')} (usa este offset para ayer, hoy, etc.)."
    if memory.rango:
        texto += f"\nRango en memoria (último consultado): time_ini={memory.rango[0]}, time_end={memory.rango[1]}."
    return {"role": "system", "content": texto}


def run_tool(name, args):
    function = AVAILABLE_FUNCTIONS.get(name)
    if function is None:
        return {"error": f"Herramienta '{name}' no encontrada"}
    if args.get("time_ini") and args.get("time_end"):
        memory.set_rango(args["time_ini"], args["time_end"])
    elif args.get("time_ini") or args.get("time_end"):
        return {"success": False, "error": "Se necesitan time_ini y time_end juntos."}
    elif memory.rango:
        args["time_ini"], args["time_end"] = memory.rango
    else:
        return {"success": False, "error": "Falta el rango de fechas y no hay uno en memoria. Pregunta la fecha al usuario."}
    return function(**args)


def process_response(client: Groq, memory_messages: list[dict], user_input: str):
    messages = [system_message()] + memory_messages
    messages.append({"role": "user", "content": user_input})
    tool_choice = "required" 
    for _ in range(MAX_TOOL_ROUNDS):
        res = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            tools=TOOLS,
            tool_choice=tool_choice,
            max_tokens=400,
        )
        tool_choice = "auto"
        msg = res.choices[0].message

        if not getattr(msg, "tool_calls", None):
            return msg.content or "No hay respuesta del modelo."

        messages.append({
            "role": "assistant",
            "content": msg.content or '',
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })

        for tool_call in msg.tool_calls:
            try:
                result = run_tool(tool_call.function.name, json.loads(tool_call.function.arguments))
            except (ValueError, TypeError, AttributeError) as e:  # args mal formados del modelo
                result = {"success": False, "error": f"Argumentos inválidos: {e}"}
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": json.dumps(result, ensure_ascii=False),
            })
    return "No pude completar la consulta, intenta reformular la pregunta."


if __name__ == "__main__":
    print("Agente Auditor de Tiempo")

    while True:
        user_input = input("Escribe tu pregunta: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit"):
            break

        assistant_text = process_response(client, memory.messages(), user_input)
        print("Respuesta del modelo:", assistant_text)

        memory.add("user", user_input)
        memory.add("assistant", assistant_text)
