# Proyecto Sello · CryptoPulse

Esta sección sigue la [Guía del Proyecto Sello](https://262bigdata.github.io/lambda26/proyecto-sello/) del curso y la aplica a nuestro proyecto. Cada página toma la plantilla del docente y muestra, criterio por criterio, **dónde está la evidencia en CryptoPulse**.

## Competencia del proyecto

Construir y defender una solución Big Data distribuida end-to-end: arquitectura Lambda, ETL batch con Spark, almacenamiento analítico en Parquet, ingesta y streaming con Kafka, observabilidad, DataOps, analítica/ML distribuida y sustentación.

| Código | Competencia | Dónde la evidencia CryptoPulse |
|---|---|---|
| CE042 | Construye dataset | Pipeline batch de 4,99 millones de velas → Parquet particionado ([Producto U1](u1-producto.md)) |
| CE043 | Genera modelos | Cuatro modelos MLlib en batch (U1) y su inferencia en vivo cada minuto (U2) |
| CE044 | Analiza y define estrategias | Tablero Grafana con KPIs del flujo y predicciones en la misma vista ([Producto U2](u2-producto.md)) |

```text
Binance (histórico + vivo) -> PySpark batch -> Parquet -> Kafka -> Spark Structured Streaming
-> Prometheus/Grafana -> MLlib e inferencia -> DataOps (scripts, CI) -> Sustentación
```

## Hitos y productos

| Hito | Sesión | Producto | Página |
|---|---|---|---|
| Brief técnico-analítico | S2 | Pregunta central, arquitectura, fuentes y 8 dimensiones (U1 y U2 por integrante) | [Brief](brief.md) |
| Producto U1 | S5 | Pipeline batch con datos validados en Parquet y un modelo por integrante | [Producto U1](u1-producto.md) |
| Producto U2 | S12 | Pipeline en tiempo real con ingesta, streaming, observabilidad, costos e inferencia | [Producto U2](u2-producto.md) |
| Producto final (U3) | S15 | Sistema integrado, endurecido, documentado y demostrable | [Producto U3](u3-producto.md) |

## Repositorio y topics

- Repositorio: <https://github.com/Milagros-hp/BigData-BTC-SOL>
- Topics: `campus-juliaca`, `semestre-2026-2`, `linea-cdia`, `tipo-ps`, `bigdata`, `seccion-<sección>`, `grupo-3-cryptopulse`
