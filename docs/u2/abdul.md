<div class="cp-profile cp-abdul" markdown>
<h1>Abdul Quispe Condori</h1>
<p><strong>¿Qué probabilidad hay de volumen inusualmente alto en los próximos 5 minutos?</strong></p>
<p>Sesiones de la Unidad 2: S9, S10 y S12</p>
</div>

## Mi aporte

| Sesión | Qué hice | Evidencia |
|---|---|---|
| **S9** | Métricas, 11 alertas, costos y criterios de escalado | `exporter.py`, `observability/`, [costos](../proyecto-sello/u2-producto.md#costos) |
| **S10** | Pronóstico de actividad con regresión logística calibrada | Panel *Actividad anómala* |
| **S12** | Sustentación de la operación del sistema y de mi dimensión | Esta página y la demo |

## Evidencia de observabilidad

![Destinos de Prometheus](../assets/u2/prom_destinos.png)
![Reglas de alerta](../assets/u2/prom_reglas.png)
![Duración de los micro-lotes](../assets/u2/microlotes.png)
![Avance de Kafka por tópico](../assets/u2/kafka_avance.png)

Cómo se correlacionan: si la duración del lote supera los 15 s, deberían crecer los eventos pendientes en Kafka, y después la edad de la última ventana. Si solo crece la edad de señal del productor, el problema está en la ingesta y no en Spark.

## Costos

![Escenario de costo](../assets/u2/costo.png)

La estimación es de 65,15 USD al mes con tarifas ilustrativas. No es una factura ni una cotización.

## Mi panel en vivo

![Panel de actividad anómala](../assets/u2/actividad.png)

## Validación

| Medición en prueba 2026 (n = 52 412) | Modelo | Referencia |
|---|---:|---:|
| PR-AUC | **0,660** | 0,072 |
| Brier | **0,0391** | 0,0658 |
| Recall en el umbral | 0,636 | 0 |
| Precisión en el umbral | 0,569 | 0 |

## Cómo explicarlo

- **Indicador:** probabilidad de superar el percentil 95 de volumen u operaciones para ese activo y esa hora UTC.
- **Por qué por hora:** el volumen normal cambia a lo largo del día; un umbral único confundiría el horario activo con una anomalía.
- **Límite real:** en la primera hora en vivo (n = 109) el error fue mayor que el de la referencia. La muestra es corta, pero es lo primero que hay que seguir vigilando.
