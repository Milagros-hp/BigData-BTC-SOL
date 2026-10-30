<div class="cp-profile cp-luz" markdown>
<h1>Luz Milagros Huanca Pacco</h1>
<p><strong>¿Qué tamaño de separación SOL–BTC se espera en los próximos 15 minutos?</strong></p>
<p>Sesiones de la Unidad 2: S10, S11 y S12</p>
</div>

## Mi aporte

| Sesión | Qué hice | Evidencia |
|---|---|---|
| **S10** | Pronóstico de separación con regresión Ridge | Panel *Separación BTC–SOL* |
| **S11** | Tablero BI único, con KPIs y predicción en la misma vista | `generar_dashboard.py`, `cryptopulse.json` |
| **S12** | Scripts de operación, CI, documentación e integración | `scripts/`, `.github/workflows/`, `mkdocs.yml` |

## Evidencia del tablero

![Tablero completo](../assets/u2/tablero.png)
![Centro de señales](../assets/u2/senales.png)

## Mi panel en vivo

![Panel de separación BTC–SOL](../assets/u2/separacion.png)

## Validación

| Medición en prueba 2026 (n = 26 207) | Modelo | Referencia |
|---|---:|---:|
| RMSE | **0,149** | 0,198 |
| MAE | **0,107** | 0,170 |

## Integración

| Script | Resultado del 30 de octubre |
|---|---|
| `pruebas_integracion.ps1` | PASS |
| `verificar_producto.ps1` | PASS |
| `prueba_recuperacion.ps1` | PASS |

## Cómo explicarlo

- **Indicador:** tamaño de la separación |SOL − BTC| en puntos porcentuales.
- **Decisión clave:** predecir la dirección con signo no mejoró la referencia cero, así que la dimensión se reformuló como tamaño de la separación.
- **Límite real:** en la primera hora en vivo (n = 45) el MAE fue 0,120 frente a 0,109 de la referencia. Una hora no invalida la prueba histórica, pero tampoco la confirma todavía.
