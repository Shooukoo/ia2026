# Conclusiones

Corpus: `politicas_empresa.txt` (40 artículos). Golden set: 20 preguntas con respuesta + 2 sin respuesta; 5 preguntas extra de validación. Todo corrió en CPU. Tabla completa en [resultados.md](resultados.md).

> Con 20 preguntas, **1 pregunta = 0.05 de Hit@3**. Diferencias de una pregunta se tratan como ruido.

## Tabla resumida (búsqueda vectorial)

| Chunking | all-MiniLM-L6-v2 | paraphrase-multilingual-L12 | bge-m3 |
|---|---|---|---|
| Artículo | 0.45 / 0.39 | 0.90 / 0.84 | 0.90 / 0.83 |
| Fijo (400) | 0.55 / 0.48 | 0.80 / 0.69 | 0.95 / 0.80 |
| Fijo + traslape (400/80) | 0.55 / 0.43 | 0.85 / 0.75 | 0.95 / 0.89 |
| Ingesta (CPU, 40 chunks) | ~1 s | ~1 s | 5–6.5 s |
| Costo en dinero | $0 | $0 | $0 |

(Celdas: Hit@3 / MRR.)

## Qué se encontró

1. **El modelo es el factor que más pesa.** all-MiniLM-L6-v2 (pensado para inglés) acierta apenas la mitad (9–11/20); los otros dos llegan a 16–19/20. Es la diferencia más grande de todo el experimento y es la única que no es ruido.
2. **multilingual-L12 vs bge-m3: casi empate.** Con chunking por artículo ambos hacen 18/20. bge-m3 se separa un poco con chunks de tamaño fijo (19 vs 16–17 de 20), pero son 2–3 preguntas: indicativo, no concluyente. Cuesta ~5× más tiempo de ingesta y vectores de 1024 dimensiones (2.7× más almacenamiento que 384).
3. **El chunking casi no cambió los resultados con bge-m3** (18, 19, 19 de 20; MRR 0.83, 0.80, 0.89), coherente con lo que reporta el artículo. Con el modelo multilingüe pequeño el chunking por artículo sí ayudó (0.90 vs 0.80–0.85), plausible porque cada chunk trae su tema completo.
4. **Tamaño fijo sin traslape parte evidencias**: "compensación mensual de 400 pesos" queda cortada entre dos chunks. Es un fallo de recuperación real, no de la métrica; el traslape lo evita.
5. **La búsqueda híbrida no ayudó con los buenos modelos.** Con multilingual y bge-m3 igualó o empeoró (p. ej. bge-m3 por artículo: 18→16/20, MRR 0.83→0.72). Solo mejoró un poco a all-MiniLM (+1–2 preguntas), que es el modelo débil. Ojo: mi implementación usa OR entre todas las palabras de la pregunta + RRF, que mete ruido léxico; una versión mejor ajustada (pesos, filtrar términos genéricos) podría cambiar esto. No se afinó para no sobreajustar al golden.
6. **Umbral de similitud:** solo bge-m3 separa respondibles de no respondibles: mínima con respuesta 0.542 vs máxima sin respuesta 0.502, así que un umbral ≈ 0.52 funciona. Con los modelos MiniLM las zonas se traslapan (0.368 < 0.466 en multilingual) y ningún umbral sirve. Ojo: solo hay 2 preguntas sin respuesta, el margen (0.04) es estrecho.
7. **Validación con preguntas extra** (config ganadora): 4/5. Consistente con el golden, pero 5 preguntas no prueban nada fino.

## Recomendación

**Chunking por artículo + BAAI/bge-m3 + búsqueda vectorial + umbral ≈ 0.52.**

- bge-m3 es el único con rechazo confiable de preguntas sin respuesta y el mejor o igual de mejor en Hit@3 en todos los chunkings.
- Por artículo, aunque `fijo_traslape` tuvo el MRR más alto (0.89 vs 0.83): la diferencia es de pocas posiciones, y el chunk por artículo es más interpretable, se puede citar ("Artículo 14") y no depende de ajustar tamaños. Si se prefiere maximizar MRR, `fijo_traslape` es igual de válido.
- La búsqueda híbrida no se justifica con estos datos.
- Alternativa barata: multilingual-L12 con chunking por artículo (18/20, ~6× más rápido de ingestar), si no importa rechazar preguntas fuera de tema.
- **Descartar all-MiniLM-L6-v2** para este corpus en español.

## Limitaciones

- Corpus de 40 artículos, de un solo documento ficticio; los resultados dependen del corpus.
- 20 preguntas escritas por la misma persona/herramienta; las 7 del enunciado más 13 nuevas. No hay intervalos de confianza.
- Contextual retrieval, late chunking y segmentadores con LLM no se midieron; los dos últimos y el primero añaden costo de LLM por chunk. Con 18–19/20 ya acertados, el margen de mejora (1–2 preguntas) difícilmente justificaría ese costo aquí; sería distinto en un corpus largo y ambiguo.
- Tiempos medidos en CPU con 40 chunks; solo sirven como comparación relativa.

## Aprendizajes

- Cambiar de modelo obliga a re-vectorizar todo, y la dimensión va atada al modelo (por eso una columna `vector(n)` por modelo).
- El modelo pequeño inglés fue el eslabón débil con español; el multilingüe pequeño casi alcanza al grande.
- Medir evitó dos suposiciones: que "más sofisticado" (híbrida, bge-m3 con chunking elaborado) siempre mejora.

## Anomalía pendiente: línea base original

La fila "línea base" de `resultados.md` (1/20) **no es representativa**. Los vectores guardados en `politicas_chunks` no corresponden a su propio texto: su similitud coseno con el embedding recién calculado del mismo contenido es ~0 con all-MiniLM-L6-v2 y con paraphrase-multilingual (la búsqueda de "aguinaldo" devuelve similitudes de 0.19 y artículos equivocados). Probablemente la tabla se ingestó con otro modelo/versión. La configuración equivalente medida limpiamente es **artículo + multilingual-L12 + vectorial = 18/20**. Para corregir la línea base basta volver a correr `ingesta.py`.
