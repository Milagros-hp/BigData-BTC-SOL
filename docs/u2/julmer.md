<div class="cp-profile cp-julmer" markdown>
<h1>Julmer Quispe Apaza</h1>
<p><strong>¿Qué probabilidad hay de una caída fuerte en los próximos 30 minutos?</strong></p>
<p>Sesiones de la Unidad 2: S6, S7, S8, S10 y S12</p>
</div>

## Mi aporte

| Sesión | Qué hice | Evidencia |
|---|---|---|
| **S6** | Eventos empresariales: operaciones ejecutadas con contrato versionado | `trades.py`, `market-trade-v1.schema.json` |
| **S7** | Telemetría de mercado: velas por WebSocket con recuperación REST | `producer.py`, `market-kline-v1.schema.json` |
| **S8** | Cuatro consultas Spark con ventanas, watermark y checkpoints | `stream.py` |
| **S10** | Pronóstico de caída con regresión logística calibrada | Panel *Caída significativa* |
| **S12** | Sustentación de la ingesta, el streaming y mi dimensión | Esta página y la demo |

## Evidencia de ingesta

![Tópicos en Kafka UI](../assets/u2/kafka_topicos.png)
![Mensajes de operaciones](../assets/u2/kafka_mensajes.png)

## Evidencia de streaming

![Ventanas finalizadas](../assets/u2/ventanas.png)
![Último minuto cerrado de operaciones](../assets/u2/ultimo.png)

## Mi panel en vivo

![Panel de caída significativa](../assets/u2/caida.png)

## Validación

| Medición en prueba 2026 (n = 52 412) | Modelo | Referencia |
|---|---:|---:|
| PR-AUC | **0,103** | 0,033 |
| Brier | **0,0250** | 0,0262 |
| Recall en el umbral | 0,262 | 0 |
| Precisión en el umbral | 0,135 | 0 |

En la primera hora en vivo (n = 60) el error queda prácticamente igual al de la referencia.

## Cómo explicarlo

- **Indicador:** probabilidad calibrada de que el rendimiento a 30 minutos caiga bajo el percentil 5 del entrenamiento de ese activo.
- **Sin fuga de información:** las variables solo usan velas cerradas y hay un embargo de 30 minutos entre particiones.
- **Garantía de entrega:** al menos una vez, con resultados idempotentes por claves únicas; no es una transacción exactamente una vez.
- **Límite real:** de cada 100 alertas, unas 14 aciertan. Sirve para priorizar una revisión, no como decisión automática.
