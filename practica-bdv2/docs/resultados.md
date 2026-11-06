# Resultados del banco de pruebas

Golden set: 20 preguntas con respuesta (Hit@3, MRR). Una diferencia de 1 pregunta = 0.05 de Hit@3: **es ruido**.

| Chunking | Modelo | Búsqueda | Hit@3 | MRR | Ingesta (s) | Costo |
|---|---|---|---|---|---|---|
| articulo (línea base) | paraphrase-multilingual-MiniLM-L12-v2 | vectorial | 1/20 (0.05) | 0.017 | — | $0 (local) |
| articulo | sentence-transformers/all-MiniLM-L6-v2 | vectorial | 9/20 (0.45) | 0.392 | 1.04 | $0 (local) |
| articulo | sentence-transformers/all-MiniLM-L6-v2 | híbrida | 10/20 (0.50) | 0.450 | 1.04 | $0 (local) |
| articulo | paraphrase-multilingual-MiniLM-L12-v2 | vectorial | 18/20 (0.90) | 0.842 | 0.81 | $0 (local) |
| articulo | paraphrase-multilingual-MiniLM-L12-v2 | híbrida | 17/20 (0.85) | 0.742 | 0.81 | $0 (local) |
| articulo | BAAI/bge-m3 | vectorial | 18/20 (0.90) | 0.825 | 5.36 | $0 (local) |
| articulo | BAAI/bge-m3 | híbrida | 16/20 (0.80) | 0.717 | 5.36 | $0 (local) |
| fijo | sentence-transformers/all-MiniLM-L6-v2 | vectorial | 11/20 (0.55) | 0.475 | 0.89 | $0 (local) |
| fijo | sentence-transformers/all-MiniLM-L6-v2 | híbrida | 12/20 (0.60) | 0.542 | 0.89 | $0 (local) |
| fijo | paraphrase-multilingual-MiniLM-L12-v2 | vectorial | 16/20 (0.80) | 0.692 | 1.18 | $0 (local) |
| fijo | paraphrase-multilingual-MiniLM-L12-v2 | híbrida | 16/20 (0.80) | 0.633 | 1.18 | $0 (local) |
| fijo | BAAI/bge-m3 | vectorial | 19/20 (0.95) | 0.800 | 4.85 | $0 (local) |
| fijo | BAAI/bge-m3 | híbrida | 17/20 (0.85) | 0.683 | 4.85 | $0 (local) |
| fijo_traslape | sentence-transformers/all-MiniLM-L6-v2 | vectorial | 11/20 (0.55) | 0.425 | 1.11 | $0 (local) |
| fijo_traslape | sentence-transformers/all-MiniLM-L6-v2 | híbrida | 12/20 (0.60) | 0.575 | 1.11 | $0 (local) |
| fijo_traslape | paraphrase-multilingual-MiniLM-L12-v2 | vectorial | 17/20 (0.85) | 0.750 | 0.94 | $0 (local) |
| fijo_traslape | paraphrase-multilingual-MiniLM-L12-v2 | híbrida | 17/20 (0.85) | 0.633 | 0.94 | $0 (local) |
| fijo_traslape | BAAI/bge-m3 | vectorial | 19/20 (0.95) | 0.892 | 6.56 | $0 (local) |
| fijo_traslape | BAAI/bge-m3 | híbrida | 16/20 (0.80) | 0.717 | 6.56 | $0 (local) |

Costo: todos los modelos corren localmente, así que el costo en dinero es $0; el costo real es tiempo de cómputo y memoria. Contextual retrieval no se midió: añadiría una llamada a un LLM por chunk en cada ingesta.

## Mejor configuración (por MRR): fijo_traslape + BAAI/bge-m3 + vectorial

Validación con 5 preguntas de intercambio (no usadas para ajustar): Hit@3 = 4/5, MRR = 0.667. Con tan pocas preguntas es solo orientativo.

## Umbral de similitud (chunking por artículo, búsqueda vectorial)

| Modelo | Similitud top-1 media (con respuesta) | Mínima (con respuesta) | Máxima (sin respuesta) |
|---|---|---|---|
| sentence-transformers/all-MiniLM-L6-v2 | 0.531 | 0.424 | 0.481 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.569 | 0.368 | 0.466 |
| BAAI/bge-m3 | 0.643 | 0.542 | 0.502 |

Un umbral solo separa bien si la máxima de las preguntas sin respuesta queda por debajo de la mínima de las que sí tienen respuesta.
