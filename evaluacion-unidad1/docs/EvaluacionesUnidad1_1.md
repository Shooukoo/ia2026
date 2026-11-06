### IA AGENTICA | AGENTES INTELIGENTES EN PYTHON, USO DE MEMORIA Y HERRAMIENTAS 1


### Inteligencia Artificial – IA Agentica


PRÁCTICA: Agente Auditor de Tiempo

Objetivo: Evaluar la creación de herramientas de análisis sobre Calendar, usar SimpleMemory y orquestar 2 tools.

APIs:
- service.freebusy\(\).query\(\) -> para calcular horas ocupadas
- service.events\(\).list\(q="palabra clave"\) -> búsqueda inteligente por texto
- service.calendars\(\).get\(\) -> info del calendario principal

Enunciado para alumno:

Eres un asistente de productividad. El usuario no quiere que crees ni borres nada, solo que analices su agenda.

Debes crear 2 tools nuevas:
- analizar\_dia\(time\_ini, time\_end\): Llama a freebusy \+ events.list y retorna JSON analítico:

\{ "success": true, "total\_reuniones": 5, "horas\_ocupadas": 3.5, "primera\_reunion": "09:00 - Daily", "ultima\_reunion": "17:00 - Review", "huecos\_libres": \["11:00-11:30", "14:00-15:00"\]\}

Debes calcular en Python las horas ocupadas sumando busy y encontrar huecos.
- buscar\_por\_tema\(time\_ini, time\_end, tema\): Usa events\(\).list\(calendarId="primary", timeMin=..., timeMax=..., q=tema\) El parámetro q es búsqueda de texto libre de Google Calendar.

Retorna cuántas reuniones contienen ese tema y lista de títulos. Ej: tema="cliente" -> busca todas las reuniones con cliente en título o descripción.

Flujo obligatorio con memoria: Si el usuario dice: "¿Cuántas reuniones de cliente tuve ayer?" -> llamas a buscar\_por\_tema Si luego dice "¿Y cuánto tiempo libre tuve?" -> debes usar el mismo time\_ini/time\_end de memoria, sin preguntar fecha de nuevo.

SYSTEM\_PROMPT anti-alucinación: "NUNCA inventes número de reuniones. Siempre llama a analizar\_dia o buscar\_por\_tema. Si no hay datos, di 'No se encontraron eventos' no inventes."

Rúbrica \(10 pts\):
- 40 pts: analizar\_dia calcula bien horas ocupadas y huecos \(lógica Python\)
- 30 pts: buscar\_por\_tema usa parámetro q correctamente
- 20 pts: Uso de memoria para no volver a pedir fecha
- 10 pt: SYSTEM\_PROMPT anti-alucinación