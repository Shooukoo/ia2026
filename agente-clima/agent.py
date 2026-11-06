from dotenv import load_dotenv
from groq import Groq
import json
import os
import re
import shutil
import textwrap

from memoria_simple import SimpleMemory
from tools import Tools

# códigos ANSI para dar formato a la salida en terminal
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


def print_banner():
    ancho = min(shutil.get_terminal_size((80, 20)).columns, 80)
    print(Color.BOLD + Color.CYAN + "☁ Agente de Clima".center(ancho) + Color.RESET)
    print(Color.DIM + "-" * ancho + Color.RESET)
    print(Color.DIM + "Preguntá por el clima de cualquier ciudad. Escribí 'salir' para terminar." + Color.RESET)
    print()


def markdown_a_ansi(texto: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", Color.BOLD + r"\1" + Color.RESET, texto)


def print_respuesta(texto: str):
    ancho = min(shutil.get_terminal_size((80, 20)).columns, 80)
    etiqueta = f"{Color.BOLD}{Color.GREEN}Agente:{Color.RESET} "
    sangria = " " * len("Agente: ")
    primera_linea = True
    for parrafo in texto.split("\n"):
        lineas = textwrap.wrap(parrafo, width=ancho - len(sangria)) or [""]
        for linea in lineas:
            prefijo = etiqueta if primera_linea else sangria
            print(markdown_a_ansi(prefijo + linea))
            primera_linea = False
    print()


def print_error(texto: str):
    print(f"{Color.RED}{texto}{Color.RESET}\n")

# cargar las variables de entorno
load_dotenv()

# constante para la memoria
MEMORY_MAX_MESSAGES = 10

# obtener la API KEY de las variables de entorno
api_key = os.getenv("API-KEY-MODEL")

# crear el cliente de Groq con la API KEY
client = Groq(api_key=api_key)

# crear la memoria simple
memory = SimpleMemory(MEMORY_MAX_MESSAGES)

# crear la instancia de herramientas y el mapeo nombre -> función
tools_instance = Tools()

AVAILABLE_FUNCTIONS = {
    "get_lat_long": tools_instance.get_lat_long,
    "get_weather": tools_instance.get_weather,
}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres un asistente del clima. Cuando el usuario pregunte por el clima de una ciudad, "
        "primero usa la herramienta 'get_lat_long' para obtener su latitud y longitud, "
        "y luego usa 'get_weather' con esos valores para obtener el clima actual. "
        "Responde siempre en español de forma clara y concisa."
    )
}

# cargar herramientas
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_lat_long",
            "description": "Obtiene la latitud y longitud de una ciudad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Nombre de la ciudad de la que se quiere obtener la ubicación"
                    }
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Obtiene el clima actual a partir de una latitud y longitud.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "string",
                        "description": "Latitud de la ubicación"
                    },
                    "long": {
                        "type": "string",
                        "description": "Longitud de la ubicación"
                    }
                },
                "required": ["lat", "long"]
            }
        }
    }
]

# verificar conexión
print_banner()

def process_response(client: Groq, memory_messages: list[dict], user_input: str):
    # obtenemos la memoria de mensajes, anteponiendo el system prompt
    messages = [SYSTEM_PROMPT] + memory_messages

    # crear mensajes
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Ciclo para la iteracion del modelo
    while True:
        # llamar al modelo de lenguaje
        res = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools= TOOLS,
            max_tokens=600,
        )

        # obtener la respuesta del modelo
        msg = res.choices[0].message
        
        # Verificar si solo es un mensaje o es una herramienta
        if not getattr(msg, "tool_calls", None):
            return msg.content or "No hay respuesta del modelo."
        
        # Existe un llamado a las herramientas
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or '',
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in msg.tool_calls
                ]
            }
        )

        # Vamos a iterar de acuerdo al numero de llamadas a funciones o herramientas
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"{Color.DIM}→ usando herramienta '{name}'...{Color.RESET}")

            function = AVAILABLE_FUNCTIONS.get(name)
            if function is not None:
                result = function(**args)
            else:
                result = {"error": f"Herramienta '{name}' no encontrada"}

            # agregar el resultado de la herramienta a los mensajes
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": json.dumps(result, ensure_ascii=False),
            })

while True:

    try:
        user_input = input(f"{Color.BOLD}{Color.CYAN}Tú:{Color.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break

    if not user_input:
        continue
    if user_input.lower() == "salir" or user_input.lower() == "exit":
        break

    # Procesado de la respuesta
    try:
        assistant_text = process_response(client, memory.messages(), user_input)
    except Exception as e:
        print_error(f"Ocurrió un error al consultar el modelo: {e}")
        continue

    # imprimir la respuesta del modelo
    print_respuesta(assistant_text)

    # actualizar la memoria con la respuesta del modelo
    memory.add("user", user_input)
    memory.add("assistant", assistant_text)