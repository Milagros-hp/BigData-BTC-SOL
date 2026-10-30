# Equipo y aporte individual

Cada integrante es dueño de una dimensión completa: su notebook U1 (batch) y su pronóstico U2 (streaming en Grafana). Además, cada uno coordina un aspecto compartido del sistema.

| Integrante | Dimensión U1 + U2 | Énfasis compartido | Evidencias |
|---|---|---|---|
| Franck Albertson Coaquira Justo | Volatilidad | Batch: calidad S03, Parquet particionado | `u1-dimensiones/01_volatilidad.ipynb`, `cryptopulse/quality.py`, panel *Volatilidad* |
| Julmer Quispe Apaza | Caídas significativas | Streaming: productor, contrato Kafka, ventanas | `u1-dimensiones/02_caidas.ipynb`, `cryptopulse/producer.py`, `cryptopulse/stream.py`, panel *Caída* |
| Abdul Quispe Condori | Actividad anómala | Observabilidad: Prometheus, alertas, costos | `u1-dimensiones/03_actividad_anomala.ipynb`, `cryptopulse/exporter.py`, `observability/`, panel *Actividad* |
| Luz Milagros Huanca Pacco | Divergencia BTC–SOL | BI/ML y DataOps: Grafana, scripts, CI, MkDocs | `u1-dimensiones/04_divergencia.ipynb`, `scripts/`, `.github/workflows/`, panel *Separación BTC–SOL* |

## Qué debe poder explicar cada integrante

1. Su pregunta U1 y U2, y cómo aporta a la pregunta central.
2. Cómo se calcula su indicador y por qué no hay fuga de información futura.
3. Qué modelos comparó, con qué métricas, cuál ganó y contra qué referencia.
4. Dónde se ve su pronóstico en Grafana y cómo se evalúa cuando madura el horizonte.
5. Una limitación real de su dimensión.

## Registro de tareas

Los commits actuales están hechos desde una sola cuenta. Por eso este registro no atribuye autoría por commit. Cada integrante debe completar su fila con fechas reales y con commits desde su propia cuenta.

| Fecha | Integrante | Tarea | Commit o evidencia |
|---|---|---|---|
| | Franck | S10: volatilidad en vivo | Por completar |
| | Julmer | S6 a S8: Kafka y Spark; S10: caídas | Por completar |
| | Abdul | S9: observabilidad y costos; S10: actividad | Por completar |
| | Luz Milagros | S10: separación; S11: tablero; S12: DataOps | Por completar |
