# Sistema de diseño

Una sola identidad visual para el tablero Grafana, este sitio, las presentaciones y el pitch. Los colores se definen una vez en `scripts/generar_dashboard.py`.

## Paleta

| Uso | Color | Regla |
|---|---|---|
| Marca, fondos | Azul noche `#12182B` / `#1B2440` | Banner, encabezados y fondo de paneles |
| **BTC** | Naranja `#F2A65A` | Toda serie de Bitcoin, en todos los paneles |
| **SOL** | Azul `#4C9BE8` | Toda serie de Solana, en todos los paneles |
| Par BTC–SOL | Violeta `#B48EF0` | Divergencia y correlación |
| NORMAL / OK | Verde `#3FB68B` | Estado sano o señal sin cruce |
| VIGILANCIA | Ámbar `#E0A030` | Cruce de una regla de vigilancia |
| ALERTA / FALLA | Rojo `#E5534B` | Cruce de alerta o componente caído |
| Sin datos | Gris `#7A8296` | Nunca se interpreta como «todo bien» |

## Reglas de lectura

- **Línea continua:** dato observado. **Línea punteada:** pronóstico. **Puntos:** realidad que llegó después, cuando madura el horizonte.
- Los colores de estado siempre van con su palabra (NORMAL, VIGILANCIA, ALERTA), no solo con el color.
- Cada panel de dimensión lleva el nombre de su integrante: *Volatilidad · Franck*, *Caída fuerte · Julmer*, *Actividad anómala · Abdul*, *Separación BTC–SOL · Luz Milagros*.

## Dos tableros enlazados

| Tablero | Para quién | Contenido |
|---|---|---|
| [CryptoPulse · BTC y SOL](http://localhost:43000/d/cryptopulse-main) (ejecutivo, página de inicio) | Analista y jurado | Estado, riesgo actual como % del umbral, línea de tiempo de señales, velas japonesas, las cuatro dimensiones, evidencia batch y en vivo, eventos empresariales, anotaciones de cambios de modelo y alertas |
| [CryptoPulse · Operación](http://localhost:43000/d/cryptopulse-ops) | Equipo técnico | Salud del pipeline etapa por etapa (Binance → Kafka → Spark → PostgreSQL → producto), alertas disparadas, mensajes por minuto por tópico, micro-lotes, lag, costos y productores de operaciones |

## Estilo global

Grafana OSS no permite temas propios. El banner de cada tablero es un panel de texto HTML (habilitado con `GF_PANELS_DISABLE_SANITIZE_HTML`) que además aplica una hoja de estilos mientras el tablero está abierto: fondo azul noche, paneles con esquinas redondeadas y títulos de fila en naranja. Si una versión futura de Grafana cambia sus clases internas, solo se pierde ese estilo; los colores de las series y estados están en la definición de cada panel y se conservan.

## Prometheus

Además de las 11 alertas operativas, `observability/alerts.yml` define 3 **reglas de grabación** que el tablero de operación consulta:

| Regla | Qué calcula |
|---|---|
| `cryptopulse:kafka_mensajes_por_minuto` | Mensajes por minuto en cada tópico `market.*` (tasa de 5 minutos) |
| `cryptopulse:lag_total` | Lag total de Spark frente a Kafka |
| `cryptopulse:lote_spark_max_5m` | Micro-lote más lento de los últimos 5 minutos, por consulta |
