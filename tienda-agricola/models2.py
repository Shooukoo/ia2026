import time
import config
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()

groq = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0 # Con 0 no alucina y con 1 si alucina
)

gemini = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite", temperature=0
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