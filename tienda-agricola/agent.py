from langchain.agents import create_agent
from models3 import groq
from langgraph.checkpoint.memory import InMemorySaver
from tools import calcular_dosis

PROMPT = ("Eres el vendedor de una tienda agricola. Busca el catalogo antes de dar precios." "Nunca inventes productos. Antes de registrar un pedido, resume producto, cantidad, total y nombre del cliente" "Pide confirmacion explicita")

vendedor = create_agent(
    model=groq,
    tools=[calcular_dosis],
    system_prompt=PROMPT,
    checkpointer=InMemorySaver(),
)
