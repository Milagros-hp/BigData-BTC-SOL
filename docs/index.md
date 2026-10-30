---
hide:
  - navigation
---

<div class="hero" markdown>
<span class="eyebrow">Big Data · UPeU 2026-2 · Grupo 3</span>

# CryptoPulse · Monitoreo de riesgo de BTC y SOL

¿Cómo puede un analista de riesgo anticipar, con 5 a 30 minutos de antelación, condiciones de riesgo en BTC y SOL: volatilidad alta, caídas fuertes, actividad anómala y desacople entre ambos activos?

<div class="hero-links" markdown>
<a class="cp-button" href="instalacion/">Levantar el sistema</a>
<a class="cp-button secondary" href="proyecto-sello/">Proyecto Sello</a>
<a class="cp-button secondary" href="https://github.com/Milagros-hp/BigData-BTC-SOL">Repositorio</a>
</div>
</div>

<div class="kpi-grid" markdown>
<div class="kpi"><span class="kpi-number">4 993 757</span><span class="kpi-label">velas históricas válidas (2022–2026)</span></div>
<div class="kpi"><span class="kpi-number">2 flujos</span><span class="kpi-label">en Kafka: velas y operaciones ejecutadas</span></div>
<div class="kpi"><span class="kpi-number">7 / min</span><span class="kpi-label">pronósticos en vivo, uno por serie</span></div>
<div class="kpi"><span class="kpi-number">4 de 4</span><span class="kpi-label">modelos que superan su referencia en 2026</span></div>
</div>

## Cuatro dimensiones, un solo tablero

<div class="dimension-grid" markdown>
<div class="dimension-card" markdown>
<span class="cp-tag">15 MIN · RANDOM FOREST</span>

### Volatilidad

¿Cuánto se va a mover el precio? Error 14 % menor que la referencia.

**Franck Albertson Coaquira Justo**
</div>
<div class="dimension-card" markdown>
<span class="cp-tag">30 MIN · LOGÍSTICA</span>

### Caídas fuertes

¿Qué probabilidad hay de una caída dentro del 5 % de peores históricas? AUC-PR 3 veces la referencia.

**Julmer Quispe Apaza**
</div>
<div class="dimension-card" markdown>
<span class="cp-tag">5 MIN · LOGÍSTICA</span>

### Actividad anómala

¿Se viene volumen inusual para esa hora del día? AUC-PR 9 veces la referencia.

**Abdul Quispe Condori**
</div>
<div class="dimension-card" markdown>
<span class="cp-tag">15 MIN · RIDGE</span>

### Divergencia BTC–SOL

¿Cuánto se van a separar SOL y BTC? Error 25 % menor que la referencia.

**Luz Milagros Huanca Pacco**
</div>
</div>

## Arquitectura Lambda

```mermaid
flowchart LR
    H[Binance histórico<br/>ZIP mensuales] --> Q[PySpark<br/>calidad] --> P[Parquet<br/>symbol/año/mes] --> M[MLlib<br/>4 modelos]
    W1[WebSocket<br/>velas] --> K[Kafka]
    W2[WebSocket<br/>operaciones] --> K
    K --> S[Spark Structured<br/>Streaming] --> DB[(PostgreSQL)]
    M --> I[Inferencia<br/>cada minuto] --> DB
    S --> I
    DB --> G[Grafana]
    S --> PR[Prometheus] --> G
```

<div class="info-grid" markdown>
<div class="info-card" markdown>
### Capa batch
4,99 millones de velas de Binance → calidad con PySpark → Parquet particionado → cuatro modelos Spark MLlib validados en el tiempo.
</div>
<div class="info-card" markdown>
### Capa de velocidad
Velas y operaciones en vivo → Kafka → Spark Structured Streaming con ventanas, watermark y checkpoints → inferencia en cada cierre de minuto.
</div>
</div>

<div class="cp-callout" markdown>
El sistema no ejecuta órdenes ni da recomendaciones de inversión: entrega **señales de vigilancia y alerta** para saber cuándo revisar el mercado.
</div>

## Por dónde empezar

<div class="info-grid" markdown>
<div class="info-card" markdown>
### [Instalación y ejecución](instalacion.md)
Levantar todo desde cero con un comando.
</div>
<div class="info-card" markdown>
### [Brief técnico-analítico](proyecto-sello/brief.md)
Pregunta central, dimensiones y fichas por integrante.
</div>
<div class="info-card" markdown>
### [Notebooks U1](notebooks-u1.md)
El análisis batch y el modelo de cada integrante.
</div>
<div class="info-card" markdown>
### [Uso del tablero](PRODUCTO_FINAL.md)
Cómo leer Grafana: estado, señales y pronósticos.
</div>
</div>
