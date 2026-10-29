# Brief técnico-analítico

Ficha del equipo según la plantilla [`brief.md`](https://262bigdata.github.io/lambda26/proyecto-sello/brief/) del Proyecto Sello (hito de S2).

## 1. Datos del equipo

- **Nombre del equipo:** CryptoPulse
- **Grupo:** 3
- **Sección:** *(completar)*
- **Repositorio:** <https://github.com/Milagros-hp/BigData-BTC-SOL>
- **Topics del repositorio:** `campus-juliaca`, `semestre-2026-2`, `linea-cdia`, `tipo-ps`, `bigdata`, `seccion-<sección>`, `grupo-3-cryptopulse`

| Integrante | Rol o énfasis en el equipo |
|---|---|
| Franck Albertson Coaquira Justo | Batch y Spark: calidad de datos, Parquet y modelo de volatilidad |
| Julmer Quispe Apaza | Streaming y Kafka: productor, contrato de eventos y ventanas Spark |
| Abdul Quispe Condori | Observabilidad: Prometheus, alertas operativas y costos |
| Luz Milagros Huanca Pacco | BI/ML y DataOps: tablero Grafana, scripts de despliegue, CI y documentación |

El rol es un énfasis de coordinación. Cada integrante construye y sustenta de extremo a extremo sus dos dimensiones (U1 y U2).

## 2. Dominio del proyecto

- **Nombre del proyecto:** CryptoPulse, monitoreo de riesgo de BTC y SOL.
- **Problema:** quien opera o analiza criptomonedas necesita saber, minuto a minuto, si el mercado entra en una condición de riesgo (movimientos fuertes, caídas, actividad anormal o desacople entre activos). Mirar solo el precio no basta: hace falta comparar con el histórico y anticipar los próximos minutos.
- **Dominio:** finanzas, mercado spot de criptomonedas (Binance). Se registra precio, volumen y operaciones de cada minuto.
- **Pregunta central de negocio:** *¿Cómo puede un analista de riesgo anticipar, con 5 a 30 minutos de antelación, condiciones de riesgo en BTC y SOL: volatilidad alta, caídas fuertes, actividad anómala y desacople entre ambos activos?*
- **Usuarios:** analista de riesgo o trader que vigila el tablero; el propio sistema, que emite señales de vigilancia y alerta.
- **Arquitectura:** **Lambda**. La capa batch procesa 4,99 millones de velas históricas para describir el pasado y entrenar los modelos. La capa de velocidad procesa cada vela en vivo con Kafka y Spark Structured Streaming y aplica esos mismos modelos. Se elige Lambda porque el entrenamiento necesita el histórico completo en bloque, mientras que la vigilancia necesita reaccionar en segundos.
- **Fuente batch:** [Binance Public Data](https://data.binance.vision/), velas de 1 minuto BTCUSDT y SOLUSDT, enero 2022 – septiembre 2026: 114 archivos ZIP mensuales verificados con SHA256.
- **Fuentes en tiempo real (datos reales, no simulados):**
    - **Telemetría de mercado:** velas cerradas de 1 minuto (`btcusdt@kline_1m`, `solusdt@kline_1m`), con recuperación REST → tópicos `market.klines.*`. Cumplen el papel de los sensores: una lectura periódica del estado del mercado.
    - **Eventos empresariales:** cada operación ejecutada (`btcusdt@aggTrade`, `solusdt@aggTrade`): precio, cantidad y lado comprador/vendedor → tópicos `market.trades.*`, contrato `schemas/market-trade-v1.schema.json`. Spark los agrega por minuto (flujo neto y presión compradora).
- **Mismo origen en dos momentos:** el histórico batch es la acumulación de las mismas velas que llegan en vivo (patrón Lambda típico).
- **Continuidad:** proyecto nuevo del equipo.

## 3. Dimensiones de análisis

| Integrante | Tipo | Dimensión (como pregunta) | Indicador | Fuente batch | Fuente streaming |
|---|---|---|---|---|---|
| Franck | Predictiva (U1, batch) | ¿Cuánta volatilidad tuvieron BTC y SOL por mes y por hora del día (2022–2026), y qué volatilidad se puede esperar en los próximos 15 minutos? | Volatilidad realizada 15 min (%): media y P95 mensual; volatilidad estimada por regresión | Velas históricas 2022–2026 | Mismas velas en vivo, acumuladas |
| Franck | Predictiva (U2, streaming) | ¿Qué volatilidad tendrá cada activo en los próximos 15 minutos, según lo que está pasando ahora? | Volatilidad pronosticada a 15 min, actualizada cada minuto | Histórico, para entrenar | Velas cerradas en vivo |
| Julmer | Predictiva (U1, batch) | ¿Con qué frecuencia BTC y SOL tuvieron caídas fuertes a 30 minutos (dentro del 5 % de peores caídas de su historial) y en qué condiciones de mercado ocurren más? | % mensual de caídas ≤ P5 histórico; probabilidad estimada por clasificación | Velas históricas | Mismas velas en vivo, acumuladas |
| Julmer | Predictiva (U2, streaming) | ¿Qué probabilidad hay de que BTC o SOL tengan una caída fuerte (dentro del 5 % de peores caídas históricas) en los próximos 30 minutos? | Probabilidad calibrada de caída, actualizada cada minuto | Histórico, para entrenar | Velas cerradas en vivo |
| Abdul | Predictiva (U1, batch) | ¿Cuándo hubo volumen u operaciones inusualmente altos (mayores que el 95 % de lo normal a esa misma hora del día), por mes y por hora? | % mensual de ventanas sobre P95; probabilidad estimada por clasificación | Velas históricas | Mismas velas en vivo, acumuladas |
| Abdul | Predictiva (U2, streaming) | ¿Qué probabilidad hay de que en los próximos 5 minutos el volumen o las operaciones sean inusualmente altos para esa hora del día? | Probabilidad calibrada de actividad anómala, cada minuto | Histórico, para entrenar | Velas cerradas en vivo |
| Luz Milagros | Predictiva (U1, batch) | ¿Cuánto se separaron los rendimientos de SOL y BTC en ventanas de 15 minutos, y cuándo se desacoplan más? | Separación \|SOL − BTC\| a 15 min (p.p.): media y P95 mensual; separación estimada por regresión | Velas históricas de ambos activos | Mismas velas en vivo, acumuladas |
| Luz Milagros | Predictiva (U2, streaming) | ¿Qué tamaño de separación entre los rendimientos de SOL y BTC se espera en los próximos 15 minutos? | Separación pronosticada a 15 min, cada minuto | Histórico, para entrenar | Velas de ambos activos en vivo |

Las cuatro dimensiones U2 se muestran en **un solo tablero Grafana** (*CryptoPulse · BTC y SOL*), y juntas responden la pregunta central: intensidad del movimiento, dirección bajista, actividad inusual y separación entre activos.

### Ficha · Volatilidad (Franck Albertson Coaquira Justo)

- **U1:** notebook [`01_volatilidad.ipynb`](../notebooks-u1.md). Media y P95 mensual, perfil por hora UTC; regresión Ridge, Lasso y Random Forest contra la referencia de persistencia (`rv15` actual), con métricas RMSE, MAE y R².
- **U2:** Random Forest desplegado en Spark; pronóstico de volatilidad a 15 min por activo en cada cierre de minuto. Alerta si supera el P95 histórico.
- **Decisión:** ajustar el tamaño de una posición o el margen de stop.
- **Panel:** *Volatilidad · observada y futura a 15 min*.
- **Se combina con:** caídas (riesgo direccional) y divergencia.
- **Requisitos:**
    1. El sistema debe calcular la volatilidad realizada con 15 rendimientos logarítmicos consecutivos, sin huecos.
    2. El sistema debe comparar el modelo con la referencia de persistencia y desplegar la referencia si el modelo no la mejora.
    3. El sistema debe mostrar el pronóstico y, cuando madure, la volatilidad real alineada al mismo instante.

### Ficha · Caídas (Julmer Quispe Apaza)

- **U1:** notebook [`02_caidas.ipynb`](../notebooks-u1.md). Porcentaje mensual de caídas y su relación con la volatilidad previa (quintiles); regresión logística L2, logística elastic-net y Random Forest contra la prevalencia histórica, con métricas AUC-ROC, AUC-PR, Brier, precisión, recall y F1.
- **U2:** regresión logística calibrada (Platt) en Spark; probabilidad de caída a 30 min por activo. El umbral de alerta se elige en validación.
- **Decisión:** reducir exposición o vigilar de cerca cuando la probabilidad supera el umbral.
- **Panel:** *Caída significativa · probabilidad a 30 min*.
- **Se combina con:** volatilidad y actividad anómala.
- **Requisitos:**
    1. El sistema debe definir una caída por activo como un rendimiento a 30 min ≤ P5 del entrenamiento.
    2. El sistema debe calibrar las probabilidades con datos separados de los de selección del umbral.
    3. El sistema debe distinguir VIGILANCIA de ALERTA en el centro de señales.

### Ficha · Actividad anómala (Abdul Quispe Condori)

- **U1:** notebook [`03_actividad_anomala.ipynb`](../notebooks-u1.md). Porcentaje mensual de ventanas anómalas y perfil por hora UTC; los mismos tres clasificadores y métricas que en caídas.
- **U2:** regresión logística calibrada; probabilidad de que el volumen o las operaciones de los próximos 5 min superen su P95 por activo y hora UTC.
- **Decisión:** anticipar momentos de liquidez extrema (noticias, liquidaciones).
- **Panel:** *Actividad anómala · probabilidad a 5 min*.
- **Se combina con:** caídas y volatilidad.
- **Requisitos:**
    1. El sistema debe usar referencias de actividad por activo y hora UTC, no un único umbral global.
    2. El sistema debe mostrar el z-score de volumen observado junto a la probabilidad.
    3. El sistema debe registrar cada evaluación para medir su acierto cuando madure el horizonte.

### Ficha · Divergencia BTC–SOL (Luz Milagros Huanca Pacco)

- **U1:** notebook [`04_divergencia.ipynb`](../notebooks-u1.md). Separación \|SOL − BTC\| media y P95 mensual y su relación con la correlación de 60 min; Ridge, Lasso y Random Forest contra el promedio histórico, con métricas RMSE, MAE y R².
- **U2:** regresión Ridge desplegada en Spark; tamaño esperado de la separación a 15 min en cada cierre de minuto. Alerta si supera el P95 histórico.
- **Hallazgo:** predecir la **dirección** de la diferencia (SOL − BTC con signo) no mejoró la referencia cero. Predecir su **tamaño** sí la mejora: RMSE de prueba 2026 de 0,149 frente a 0,198 del promedio histórico.
- **Decisión:** revisar coberturas o rotación cuando se espera que los activos se desacoplen.
- **Panel:** *Separación BTC–SOL · tamaño \|SOL − BTC\| a 15 min*.
- **Se combina con:** volatilidad (los desacoples coinciden con volatilidad alta).
- **Requisitos:**
    1. El sistema debe calcular la separación solo cuando ambos activos tienen la vela del mismo minuto.
    2. El sistema debe mostrar la correlación de 60 min como contexto observado.
    3. El sistema debe evaluar el pronóstico contra la separación real a 15 min.

## Alcance

- **Sí cubre:** histórico batch completo, ingesta en vivo, streaming con ventanas y watermark, cuatro modelos validados en el tiempo, inferencia en vivo, tablero único, observabilidad, costos estimados, pruebas y scripts de despliegue.
- **No cubre:** ejecución de órdenes, recomendaciones personales de inversión, otros activos o exchanges, ni un clúster Spark multinodo de alta disponibilidad.

## 4. Aprobación

- Docente:
- Fecha:
