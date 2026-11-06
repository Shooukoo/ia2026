import time
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

groq = init_chat_model(
    "groq:openai/gpt-oss-120b", temperature=0 # Con 0 no alucina y con 1 si alucina
)

gemini = init_chat_model(
    "google_genai:gemini-3.1-flash-lite", temperature=0
)

def main():
    # Mandar a llamar a los modelos para que respondan
    pregunta = "Explica en 3 lineas que es un agente de IA"
    
    for nombre, modelo in [("Groq", groq), ("Gemini", gemini)]:
        t0 = time.time()
        respuesta = modelo.invoke(pregunta)
        print(f"{nombre}: {time.time() - t0}\n {respuesta}")
        print("Tokens:", respuesta.usage_metadata)

if __name__ == '__main__':
    main()