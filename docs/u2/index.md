---
hide:
  - navigation
  - toc
---

<div class="cp-hero" markdown>
<span class="cp-eyebrow">Big Data · UPeU 2026-2 · Grupo 3 · Producto de Unidad 2</span>

# CryptoPulse en tiempo real

Del histórico de la Unidad 1 a un pipeline vivo: cada operación y cada minuto de BTC y SOL entran por Kafka, pasan por Spark y terminan como riesgo pronosticado en un solo tablero.

<p class="cp-question">¿Cómo puede un analista de riesgo anticipar, con 5 a 30 minutos de antelación, volatilidad alta, caídas fuertes, actividad anómala y desacople entre BTC y SOL?</p>
</div>

<div class="cp-stats" markdown>
<div class="cp-stat"><b>2</b><span>flujos reales en Kafka: operaciones y velas</span></div>
<div class="cp-stat"><b>79 744</b><span>operaciones en ventanas durante la primera hora</span></div>
<div class="cp-stat"><b>7/7</b><span>pronósticos vigentes cada minuto</span></div>
<div class="cp-stat"><b>11</b><span>alertas operativas en Prometheus</span></div>
<div class="cp-stat"><b>4,6 s</b><span>duración media del lote, con intervalo de 15 s</span></div>
<div class="cp-stat"><b>65 USD</b><span>por mes, estimación con tarifas ilustrativas</span></div>
</div>

## De la Unidad 1 a la Unidad 2

| | Unidad 1 | Unidad 2 |
|---|---|---|
| **Datos** | 4 993 757 velas históricas validadas | Operaciones y velas en vivo desde Binance |
| **Proceso** | Batch con PySpark y Parquet | Spark Structured Streaming con ventanas, watermark y checkpoints |
| **Modelos** | Entrenados y evaluados con historia | Aplicados cada minuto y evaluados cuando madura el horizonte |
| **Salida** | Notebooks por integrante | Tablero Grafana en vivo, con operación y costos |

## El equipo y su aporte

<div class="cp-team">
<a class="cp-member cp-franck" href="franck/"><strong>Franck Coaquira</strong><em>Volatilidad a 15 min</em><span class="cp-chip">S10</span><span class="cp-chip">S11</span><span class="cp-chip">S12</span><small>Modelo Random Forest en vivo</small></a>
<a class="cp-member cp-julmer" href="julmer/"><strong>Julmer Quispe</strong><em>Caída fuerte a 30 min</em><span class="cp-chip">S6</span><span class="cp-chip">S7</span><span class="cp-chip">S8</span><span class="cp-chip">S10</span><span class="cp-chip">S12</span><small>Kafka, contratos y Spark</small></a>
<a class="cp-member cp-abdul" href="abdul/"><strong>Abdul Quispe</strong><em>Actividad anómala a 5 min</em><span class="cp-chip">S9</span><span class="cp-chip">S10</span><span class="cp-chip">S12</span><small>Prometheus, alertas y costos</small></a>
<a class="cp-member cp-luz" href="luz/"><strong>Luz Milagros Huanca</strong><em>Separación BTC–SOL a 15 min</em><span class="cp-chip">S10</span><span class="cp-chip">S11</span><span class="cp-chip">S12</span><small>Tablero BI, scripts y CI</small></a>
</div>

## El camino: sesión 6 a sesión 12

<div class="cp-timeline" markdown>
<div class="cp-step cp-julmer"><b>S6</b><span>Eventos empresariales: operaciones ejecutadas en <code>market.trades.*</code></span><small>Julmer</small></div>
<div class="cp-step cp-julmer"><b>S7</b><span>Telemetría de mercado: velas de 1 minuto en <code>market.klines.*</code></span><small>Julmer</small></div>
<div class="cp-step cp-julmer"><b>S8</b><span>Spark Streaming: 4 consultas, ventanas, watermark y checkpoints</span><small>Julmer</small></div>
<div class="cp-step cp-abdul"><b>S9</b><span>Observabilidad, alertas, costos y criterios de escalado</span><small>Abdul</small></div>
<div class="cp-step cp-franck"><b>S10</b><span>Inferencia en streaming: un modelo por integrante</span><small>Los cuatro</small></div>
<div class="cp-step cp-luz"><b>S11</b><span>Tablero BI: KPIs y predicción en la misma vista</span><small>Luz Milagros</small></div>
<div class="cp-step cp-luz"><b>S12</b><span>Integración, pruebas de recuperación y sustentación</span><small>Luz Milagros y equipo</small></div>
</div>

[Ver cada sesión con su evidencia](sesiones.md){ .md-button .md-button--primary } [Guion de la demo](demo.md){ .md-button }

## Arquitectura

```mermaid
flowchart LR
    B[Binance WebSocket y REST] --> PT[trades.py] --> KT[(Kafka market.trades)]
    B --> PK[producer.py] --> KK[(Kafka market.klines)]
    KT --> SF[Spark: flujo por minuto]
    KK --> SW[Spark: ventanas fija y deslizante]
    KK --> SA[Spark: archivo e inferencia]
    SF --> DB[(PostgreSQL)]
    SW --> DB
    SA --> DB
    DB --> G[Grafana]
    EX[exporter y kafka-exporter] --> PR[Prometheus] --> G
```

## El producto en vivo

<figure markdown>
![Tablero CryptoPulse en estado LISTO](../assets/u2/tablero.png)
<figcaption>Tablero único en estado LISTO, 30 de octubre de 2026. Captura automática del producto en ejecución.</figcaption>
</figure>

## Lo que probamos, no solo lo que construimos

| Prueba | Resultado |
|---|---|
| Evento duplicado | Se cuenta una sola vez, en velas y en operaciones |
| Evento tardío | Se descarta por watermark |
| Reinicio de Spark | Continúa desde su checkpoint |
| Caída del productor de velas | El estado pasa a degradado y se recupera sin huecos |
| Caída del productor de operaciones | El estado pasa a degradado; recupera por REST y la verificación no encuentra minutos faltantes en BTC |

<div class="cp-honest" markdown>
**Lectura honesta de los modelos.** En la prueba histórica reservada (enero a septiembre de 2026), los cuatro superan a su referencia. En la primera hora en vivo solo volatilidad la supera con claridad; caída queda empatada, y actividad y separación quedan por debajo. Una hora de un solo día no alcanza para concluir, por eso el tablero sigue midiéndolo.
</div>
