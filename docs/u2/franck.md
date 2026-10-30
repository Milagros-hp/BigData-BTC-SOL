<div class="cp-profile cp-franck" markdown>
<h1>Franck Albertson Coaquira Justo</h1>
<p><strong>¿Qué volatilidad tendrá cada activo en los próximos 15 minutos, según lo que está pasando ahora?</strong></p>
</div>

Página adaptada a mi dimensión, con la estructura de la [plantilla del docente](../proyecto-sello/u2-producto.md).

## Producto

Pronóstico en streaming de la volatilidad a 15 minutos de BTC y SOL, actualizado cada minuto e integrado al tablero BI.

### Evolución desde U1

| | Unidad 1 | Unidad 2 |
|---|---|---|
| **Pregunta** | ¿Cuánta volatilidad tuvieron BTC y SOL por mes y por hora del día (2022–2026)? | ¿Qué volatilidad tendrá cada activo en los próximos 15 minutos, según lo que está pasando ahora? |
| **Resultado** | Notebook batch que comparó referencia, Ridge, Lasso y Random Forest. Ganó Random Forest, con RMSE de validación 0,140. | El mismo algoritmo se aplica a las últimas 61 velas cerradas, cada minuto, y cada pronóstico se compara con la volatilidad que ocurrió 15 minutos después. |

## 1. Alcance de capacidades por sesión

En negrita, lo que sustento como propio.

| Sesión | Capacidad en mi dimensión | Evidencia |
|---|---|---|
| S6, S7 | Mi modelo consume las velas de Kafka | Infraestructura de Julmer |
| S8 | Mi inferencia corre en la consulta de archivo de Spark | `stream.py` |
| S9 | Mi serie tiene su propia alerta de pronóstico atrasado | `CryptoPulseStalePrediction` |
| **S10** | **Random Forest en vivo para BTC y SOL** | [`inference.py`](https://github.com/Milagros-hp/BigData-BTC-SOL/blob/main/pyspark/sesiones/cryptopulse/inference.py), panel de volatilidad |
| **S11** | **Panel con observado, pronóstico y realidad posterior** | *Volatilidad · observada y futura a 15 min* |
| **S12** | **Integración y publicación del pipeline; sustentación de mi dimensión** | Commits `bc288ce` y `c051ab9`, esta página |

## 2. Rúbrica de Evaluación

| Criterio | Peso | Mi evidencia |
|---|---:|---|
| 1. Ingesta de eventos empresariales | 12% | Trabajo de Julmer |
| 2. Ingesta de eventos IoT/sensores | 10% | Trabajo de Julmer; de aquí sale mi modelo |
| 3. Procesamiento streaming | 14% | Trabajo de Julmer; ahí corre mi inferencia |
| 4. Observabilidad | 12% | Trabajo de Abdul; incluye la alerta de mi serie |
| 5. Costos y escalado | 8% | Trabajo de Abdul |
| 6. Salidas BI/ML | 12% | Mi panel junto al estado y las señales de riesgo |
| 7. Series de tiempo validada | 12% | Random Forest validado en prueba 2026 y en vivo |
| 8. Sustentación | 20% | Esta página y el [guion](demo.md) |

Niveles A, B, C y D completos en la [Tabla 2](../proyecto-sello/u2-producto.md#2-rubrica-de-evaluacion).

### Mi panel en vivo

![Panel de volatilidad](../assets/u2/volatilidad.png)

Cómo leerlo: si el pronóstico sube frente a lo observado reciente, el analista debe esperar un movimiento más intenso en los próximos 15 minutos. La línea de *realidad futura* aparece 15 minutos después y permite comprobar el acierto.

### Validación en el tablero

![Prueba histórica reservada](../assets/u2/prueba.png)
![Evaluación en vivo](../assets/u2/vivo.png)

### Métricas

| Medición | Modelo | Referencia |
|---|---:|---:|
| RMSE, prueba 2026 (n = 52 412) | **0,129** | 0,151 |
| MAE, prueba 2026 | **0,079** | 0,085 |
| MAE en vivo, BTC (n = 76) | **0,060** | 0,089 |
| MAE en vivo, SOL (n = 75) | **0,084** | 0,108 |

Cifras en vivo del 30 de octubre de 2026, de 15:07 a 18:34 UTC. Son una muestra corta.

### Cómo explicarlo

- **Indicador:** 100 por la raíz de la suma de cuadrados de 15 rendimientos logarítmicos de 1 minuto, sin anualizar.
- **Variables:** rendimientos a 1, 5, 15 y 30 min; volatilidad reciente a 15 y 60 min; volumen y operaciones a 5 min; rango y cuerpo de la vela; hora del día y activo.
- **Sin fuga de información:** las variables solo usan velas ya cerradas; el futuro solo se usa como etiqueta y para evaluar.
- **Aporte a la pregunta central:** mide la intensidad del movimiento, sin decir su dirección; por eso se lee junto a la caída.
- **Límite real:** en el panel, el pronóstico se mueve en un rango más estrecho que la realidad, así que puede quedarse corto en los picos.

## 3. Trazabilidad

Los criterios 6 y 7 son la evidencia de CE044-N3 y CE043-N3. Mi modelo de U1 completa aquí CE043 al aplicarse en streaming y validarse con métricas. [Trazabilidad completa](../proyecto-sello/u2-producto.md#3-trazabilidad-y-procedencia-de-la-rubrica).
