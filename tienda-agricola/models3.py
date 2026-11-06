import time
import config
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from pydantic import BaseModel

load_dotenv()

groq = ChatGroq(
    model="openai/gpt-oss-120b", temperature=0 # Con 0 no alucina y con 1 si alucina
)

gemini = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite", temperature=0
)

class Producto(BaseModel):
    nombre: str
    precio: float
    existencia: int

class Materia(BaseModel):
    nombre: str
    promedio: float

class Estudiante(BaseModel):
    nombre: str
    materias: list[Materia]
    promedio_general: float

def practica():
    texto = ("Juan Pérez Gómez cursa Matemáticas con promedio 8.5, Física con 9.0 "
            "e Historia con 7.5.")
    for nombre, llm in (("Groq", groq), ("Gemini", gemini)):
        print(5*"===" + nombre + 5*"===")
        extractor = llm.with_structured_output(Estudiante, method="json_schema")
        print(extractor.invoke([
            ("system", "Extrae el nombre del estudiante, sus materias con su promedio, y calcula el promedio general como la media de los promedios de las materias, redondeado a 2 decimales. No hagas preguntas."),
            ("user", texto)
        ]))

def main():
    print(5*"===" + "Groq" + 5*"===")
    extractor = groq.with_structured_output(Producto, method="json_schema")
    print(extractor.invoke([
        ("system", "Extrae el nombre del producto, precio, y la existencia. No realices calculos ni hagas preguntas."),
        ("user", "Fungicida cúprico de 1KG, cuentas 245.89, en almacen hay 100 ")
    ]))

    print(5*"===" + "Gemini" + 5*"===")
    extractor = gemini.with_structured_output(Producto, method="json_schema")
    print(extractor.invoke([
        ("system", "Extrae el nombre del producto, precio, y la existencia. No realices calculos ni hagas preguntas."),
        ("user", "Fungicida cúprico de 1KG, cuentas 245.89, en almacen hay 100 ")
    ]))

if __name__ == '__main__':
    practica()
