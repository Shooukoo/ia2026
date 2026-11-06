# ia2026

Prácticas y evaluaciones de la materia de IA (2026).

| Carpeta | Contenido |
|---|---|
| `practica1/` | Agente con herramientas y memoria simple |
| `agente-clima/` | Agente de clima con memoria de largo plazo |
| `evaluacion-unidad1/` | Evaluación de la unidad 1 |
| `practica-bdv/`, `practica-bdv2/`, `practica-bdv3/` | Bases de datos vectoriales (búsqueda, chunking, benchmark) |
| `tienda-agricola/` | Agente de tienda agrícola |

## Configuración

Cada proyecto tiene su propio `venv` y `.env` (no versionados):

```sh
cd <proyecto>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env   # si existe; completar las claves
```

`credentials.json` y `token.json` (OAuth de Google) tampoco se suben.
