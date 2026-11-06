from dotenv import load_dotenv
from groq import Groq
import json
import os

from memoria_simple import SimpleMemory
from tools import Tools

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
    "check_availability": tools_instance.check_availability,
    "list_events": tools_instance.list_events,
    "create_event": tools_instance.create_event,
    "update_event": tools_instance.update_event,
    "delete_event": tools_instance.delete_event,
}

# cargar herramientas
TOOLS = [
    {
        "type": "function",
        "function": {
        "name": "check_availability",
        "description": "Consulta la disponibilidad del calendario del usuario para un intervalo determinado. Usa esta herramienta cuando el usuario pregunte si tiene disponibilidad en una fecha u horario. Los parametros time_ini y time_end DEBEN estar en formato RFC3339 e incluir el offset de zona horaria. EJEMPLO: 2026-09-09T10:00:00-06:00",
        "parameters": {
            "type": "object",
            "properties": {
                "time_ini": {
                    "type": "string",
                    "description": "La fecha de inicio para revisar la disponibilidad en formato RFC3339"
                },
                "time_end": {
                    "type": "string",
                    "description": "La fecha de fin para revisar la disponibilidad en formato RFC3339"
                }
            },
        "required": [
            "time_ini",
            "time_end"
        ]
        }
    }
    },
    {
        "type": "function",
        "function": {
        "name": "list_events",
        "description": "Lista los eventos del calendario del usuario dentro de un intervalo determinado. Usa esta herramienta cuando el usuario pida ver, consultar o listar sus eventos o citas. Los parametros time_ini y time_end DEBEN estar en formato RFC3339 e incluir el offset de zona horaria. EJEMPLO: 2026-09-09T10:00:00-06:00",
        "parameters": {
            "type": "object",
            "properties": {
                "time_ini": {
                    "type": "string",
                    "description": "La fecha de inicio para listar los eventos en formato RFC3339. Si no se especifica, se listan a partir de ahora."
                },
                "time_end": {
                    "type": "string",
                    "description": "La fecha de fin para listar los eventos en formato RFC3339."
                },
                "max_results": {
                    "type": "integer",
                    "description": "El numero maximo de eventos a devolver."
                }
            },
        "required": []
        }
    }
    },
    {
        "type": "function",
        "function": {
        "name": "create_event",
        "description": "Crea un evento en el calendario del usuario, verificando primero que el horario esté disponible. Usa esta herramienta cuando el usuario pida agendar, crear o programar un evento o cita. Los parametros time_ini y time_end DEBEN estar en formato RFC3339 e incluir el offset de zona horaria. EJEMPLO: 2026-09-09T10:00:00-06:00",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "El titulo o resumen del evento."
                },
                "time_ini": {
                    "type": "string",
                    "description": "La fecha y hora de inicio del evento en formato RFC3339."
                },
                "time_end": {
                    "type": "string",
                    "description": "La fecha y hora de fin del evento en formato RFC3339."
                }
            },
        "required": [
            "summary",
            "time_ini",
            "time_end"
        ]
        }
    }
    },
    {
        "type": "function",
        "function": {
        "name": "update_event",
        "description": "Actualiza uno o mas campos de un evento existente en el calendario del usuario. Usa esta herramienta cuando el usuario pida modificar, reagendar, cambiar el horario o el titulo de un evento o cita. El event_id se obtiene previamente de la herramienta list_events o create_event. Solo se actualizan los campos proporcionados. Los parametros time_ini y time_end DEBEN estar en formato RFC3339 e incluir el offset de zona horaria. EJEMPLO: 2026-09-09T10:00:00-06:00",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "El identificador del evento a actualizar."
                },
                "summary": {
                    "type": "string",
                    "description": "El nuevo titulo o resumen del evento."
                },
                "time_ini": {
                    "type": "string",
                    "description": "La nueva fecha y hora de inicio del evento en formato RFC3339."
                },
                "time_end": {
                    "type": "string",
                    "description": "La nueva fecha y hora de fin del evento en formato RFC3339."
                }
            },
        "required": [
            "event_id"
        ]
        }
    }
    },
    {
        "type": "function",
        "function": {
        "name": "delete_event",
        "description": "Elimina un evento del calendario del usuario a partir de su identificador. Usa esta herramienta cuando el usuario pida cancelar, borrar o eliminar un evento o cita. El event_id se obtiene previamente de la herramienta list_events o create_event.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "El identificador del evento a eliminar."
                }
            },
        "required": [
            "event_id"
        ]
        }
    }
    },
]

# verificar conexión
print("Agente de IA")

def process_response(client: Groq, memory_messages: list[dict], user_input: str):
    # obtenemos la memoria de mensajes
    messages = memory_messages

    # crear mensajes
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Ciclo para la iteracion del modelo
    while True:
        # llamar al modelo de lenguaje
        res = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            tools= TOOLS,
            max_tokens=300,
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

    user_input = input("Escribe tu pregunta: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "salir" or user_input.lower() == "exit":
        break

    # Procesado de la respuesta
    assistant_text = process_response(client, memory.messages(), user_input)

    # imprimir la respuesta del modelo
    print("Respuesta del modelo:", assistant_text)

    # actualizar la memoria con la respuesta del modelo
    memory.add("user", user_input)
    memory.add("assistant", assistant_text)