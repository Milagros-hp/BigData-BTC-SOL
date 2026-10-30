# Preparación S12 · Evaluación de la Unidad II

Guía de la evaluación: [S12](https://262bigdata.github.io/lambda26/sesiones/S12_Evaluacion_Unidad_2/). Aquí está cada tema de la evaluación teórico-práctica (S6–S11) respondido con **nuestro** pipeline, las preguntas de referencia, la autoevaluación con la rúbrica y las decisiones propias que nos distinguen del ejemplo del docente.

## 1. Teoría S6–S11 con ejemplos de CryptoPulse

### S6 · Eventos empresariales con Kafka

| Concepto | En CryptoPulse |
|---|---|
| **Broker** | Un broker Kafka 4.3.1 en modo KRaft (sin ZooKeeper), contenedor `cryptopulse-kafka` |
| **Topic** | `market.trades.btcusdt` y `market.trades.solusdt` (operaciones); `market.klines.*` (velas) |
| **Partición** | 3 por tópico; el orden se garantiza dentro de cada partición |
| **Key** | El símbolo (`BTCUSDT`): todos los eventos de un activo caen en la misma partición y conservan su orden |
| **Offset** | Posición de cada mensaje; Spark guarda el último offset procesado en su checkpoint |
| **Consumer group** | Spark Structured Streaming no confirma offsets en un consumer group: los guarda en su checkpoint, por eso puede reprocesar exactamente desde donde iba |
| **Contrato versionable** | `schema_version: 1` en cada evento; `schemas/market-trade-v1.schema.json` y `market-kline-v1.schema.json`. Un cambio incompatible sería `v2` en un tópico nuevo |

### S7 · Eventos IoT/sensores

| Concepto | En CryptoPulse |
|---|---|
| **Frecuencia y volumen** | La vela (nuestra telemetría) llega a un ritmo fijo: 2 mensajes por minuto, tamaño constante. La operación (evento de negocio) llega en ráfagas: ~800 por minuto en promedio y picos de 3 547 |
| **Particionado por dispositivo** | Nuestro «dispositivo» es el activo: la key `BTCUSDT`/`SOLUSDT` se verifica en Kafka UI, columna *Key* |
| **Validación de esquema y rango físico** | `contract.py` rechaza: OHLC incoherente (mínimo mayor que apertura o cierre), volúmenes negativos, intervalo distinto de 59 999 ms, velas futuras o no cerradas |
| **¿Por qué un dispositivo real usa MQTT y no Kafka?** | Un sensor tiene poca memoria, batería y conexión intermitente; MQTT es liviano y tolera cortes. Un **puente** recibe por MQTT y publica en Kafka. En nuestro caso, `producer.py` cumple el papel de puente: recibe del WebSocket de Binance y publica en Kafka con contrato y reintentos |

### S8 · Streaming con ventanas, watermark y semántica

| Concepto | En CryptoPulse |
|---|---|
| **Ventana fija** | 5 minutos, sin solaparse |
| **Ventana deslizante** | 5 minutos que avanzan de a 1 minuto |
| **Watermark** | 2 min en velas y 1 min en operaciones: lo que llega más tarde se descarta y se cuenta en `descartadas_por_watermark` |
| **Checkpoint** | Uno por consulta en `_runtime/checkpoints/{archive,fixed,sliding,trades}` |
| **Al menos una vez + deduplicación** | Spark puede reprocesar un lote tras un fallo; `dropDuplicatesWithinWatermark(event_id)` y las claves únicas de PostgreSQL hacen que el resultado no tenga duplicados |
| **Efecto en latencia y throughput** | El watermark agrega hasta 2 min de espera antes de cerrar una ventana definitiva; el micro-lote de 15 s y `maxOffsetsPerTrigger` limitan cuánto se procesa por lote |

**Verificación en logs** (criterio 3): cada minuto Spark escribe una línea con lote, filas, watermark, filas descartadas y ruta del checkpoint de cada consulta:

```powershell
docker logs --tail 40 cryptopulse-streaming | Select-String progreso
```

### S9 · Observabilidad y costos

| Métrica | Tipo | Dónde |
|---|---|---|
| `cryptopulse_producer_connected`, `cryptopulse_product_ready` | Disponibilidad | Panel *WebSocket* y *Estado integral* |
| Edad de la última vela y del heartbeat de Spark | Latencia | Panel *Spark · edad de señal de vida*, tabla *Frescura* |
| `cryptopulse_input_rows_per_second`, offsets de Kafka | Throughput | Panel *Kafka · avance acumulado por tópico* |
| `cryptopulse_kafka_checkpoint_lag` | Lag del consumidor | Panel *Kafka · eventos pendientes*; alerta `CryptoPulseKafkaLag` |
| `cryptopulse_batch_duration_seconds` | Backpressure | Panel *Spark · duración de micro-lotes* |

Prometheus lee (pull) el exportador propio en `exporter:8000/metrics` y el `kafka-exporter`; Grafana consulta Prometheus y PostgreSQL. Costos y escalado: [Producto U2, costos](u2-producto.md#costos).

### S10 · Series de tiempo e inferencia

- **Referencia de persistencia primero:** en volatilidad la referencia es «la volatilidad actual se repite». Si el modelo no le gana, no aporta: eso nos pasó con la divergencia con signo y por eso la reformulamos.
- **División cronológica, nunca aleatoria:** entrenamiento 2022–2024, validación 2025, prueba 2026, con 30 min de embargo.
- **Inferencia sin estado:** el modelo se carga una vez; en cada cierre de minuto se leen las últimas 61 velas desde PostgreSQL y se calcula todo de nuevo. No se mantiene historial en memoria: si Spark se reinicia, la próxima lectura basta.

### S11 · BI/ML: KPIs y predicción

- **KPI de negocio:** precio, flujo neto comprador − vendedor, probabilidad de caída, separación BTC–SOL. **Métrica de infraestructura:** lag de Kafka, duración del lote. **Métrica de aplicación:** pronósticos vigentes 7/7, velas de contexto 61/61.
- **Pushgateway:** no lo usamos. Nuestro streaming nunca termina, así que exponemos `/metrics` y Prometheus lo lee, que es la forma recomendada. Pushgateway sirve para jobs que terminan; usarlo en uno que no termina es un atajo porque si el job muere, la última métrica queda «congelada» y Prometheus no lo nota.
- **Error de predicción en vivo:** tabla *En vivo · error real de los pronósticos ya madurados*.
- **Panel batch y streaming lado a lado:** *Batch · prueba histórica reservada* (estático, 2026) junto a *En vivo · error real* (se actualiza cada minuto).

## 2. Preguntas de referencia

**¿Diferencia entre el contrato de un evento empresarial y uno de sensor?**
La vela (sensor) es periódica, de tamaño fijo y se valida por rango físico (OHLC coherente). La operación (negocio) es individual, en ráfagas, con identidad propia (`trade_id`) y lado comprador/vendedor. Por eso van en tópicos distintos: distinto volumen, retención y consumidores.

**Si un evento llega tarde, ¿qué hace el watermark? ¿Y sin él?**
Dentro del watermark entra en su ventana según la hora del evento; fuera de él se descarta y se cuenta. Sin watermark, Spark tendría que guardar el estado de todas las ventanas para siempre: la memoria crecería sin límite y nunca podría declarar una ventana como definitiva.

**¿Qué métrica alertaría primero un backpressure?**
La duración del micro-lote: si supera los 15 s del intervalo, el siguiente lote empieza atrasado. Enseguida le sigue el lag de Kafka (`cryptopulse_kafka_checkpoint_lag`), que tiene alerta a partir de 100 mensajes durante 2 min.

**¿Por qué estimar el costo del streaming no es igual que el del batch?**
El batch corre un rato y se apaga: se paga por ejecución. El streaming corre las 730 horas del mes y su costo crece con el volumen continuo y la retención de Kafka (las operaciones ocuparon unos 6 GB proyectados a 7 días con el volumen del 30 de octubre).

**¿Qué gana el tablero al mostrar la predicción junto a los KPIs?**
El analista ve en la misma pantalla qué está pasando (KPI) y qué se espera (predicción), y luego si el pronóstico acertó. Por separado tendría que cruzarlos a mano.

**¿Por qué comparar primero con la persistencia y qué significa no ganarle?**
Porque en series de tiempo «mañana será como hoy» suele ser difícil de superar. Si el modelo no le gana, no aporta valor y se despliega la referencia; nos pasó con la divergencia con signo.

**¿KPI de negocio frente a métrica de infraestructura? ¿Por qué Pushgateway es un atajo?**
Ver S11 arriba.

## 3. Autoevaluación con la rúbrica U2

| Criterio | Peso | Evidencia en vivo | Nivel esperado |
|---|---:|---|---|
| 1. Eventos empresariales con Kafka | 12 % | Kafka UI `market.trades.*`, contrato v1, panel de flujo neto | A |
| 2. Eventos IoT/sensores | 10 % | Kafka UI `market.klines.*`, 61/61 velas, 0 faltantes | A (telemetría real de mercado; explicar la analogía con un sensor) |
| 3. Streaming con Spark | 14 % | 4 consultas; log `progreso` con watermark y checkpoint; tabla *Ventanas finalizadas* | A |
| 4. Observabilidad | 12 % | Sección *Operación*, Prometheus `/targets` y `/alerts`, caso de error | A |
| 5. Costos y escalado | 8 % | Volumen medido, costo de 65 USD/mes y umbrales para escalar | A |
| 6. Salidas BI/ML | 12 % | Tablero único: estado, señales, KPIs y predicciones | A |
| 7. Inferencia validada | 12 % | Prueba 2026 contra referencias y error en vivo, lado a lado | A |
| 8. Sustentación | 20 % | Depende de cada integrante: dimensión propia, evolución desde U1 y una pregunta de la Tabla 1 | Practicar |

## 4. Decisiones propias, distintas al ejemplo del docente

1. **Datos reales, no simulados:** velas y operaciones reales de Binance en lugar de sensores simulados.
2. **Evento empresarial con valor de negocio:** cada operación ejecutada se convierte en el flujo comprador/vendedor por minuto.
3. **Cambiar la pregunta cuando el modelo no aporta:** la divergencia con signo no superó la referencia; la reformulamos como tamaño y documentamos ambas versiones.
4. **Probabilidades calibradas y umbral elegido en datos separados**, en vez de usar 0,5 por defecto.
5. **Error medido en vivo:** cada pronóstico se compara con la realidad cuando madura su horizonte.
6. **Exportador propio con `/metrics`** en lugar de Pushgateway.
7. **Autorreparación:** el streaming detecta checkpoints corruptos y se recupera sin duplicar datos.
