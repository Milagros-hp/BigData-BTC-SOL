# Guía de cambios (29 de octubre de 2026)

Qué se corrigió y qué se agregó para alinear CryptoPulse con la guía del Proyecto Sello ([lambda26](https://github.com/262bigdata/lambda26)). Cada punto dice **dónde verlo** y **qué criterio de la rúbrica cubre**.

## Resumen en una tabla

| # | Cambio | Dónde verlo | Rúbrica |
|---|---|---|---|
| 1 | Repositorio Git en GitHub con historial de commits | <https://github.com/Milagros-hp/BigData-BTC-SOL/commits/main> | Subaspecto *Repositorio y estándares* (U1, U2, U3) |
| 2 | Arranque robusto en un equipo limpio | `scripts/iniciar_producto.ps1` | U3 · 2 DataOps, 4 Hardening, 5 Demo reproducible |
| 3 | Rutas relativas en la documentación | `README.md`, `docs/*.md` | U3 · 3 Documentación |
| 4 | Divergencia reformulada: ahora tiene un modelo real | `cryptopulse/training.py`, panel *Separación BTC–SOL* | U1 · 5 ML; U2 · 7 Series de tiempo |
| 5 | Cuatro notebooks U1, uno por integrante | `pyspark/sesiones/u1-dimensiones/` | U1 · criterios 2, 3, 4, 5 y 6 |
| 6 | Eventos empresariales por Kafka | `cryptopulse/trades.py`, sección final del tablero | U2 · 1 Ingesta de eventos empresariales |
| 7 | Brief del equipo con 8 dimensiones | `docs/proyecto-sello/brief.md` | Hito S2; subaspecto *Aporte individual* |
| 8 | Sitio MkDocs | `mkdocs.yml`, `docs/` | Subaspecto *MkDocs*; U3 · 3 |
| 9 | CI en GitHub Actions | `.github/workflows/` | U3 · 2 DataOps |
| 10 | Páginas de equipo, hardening, limitaciones y repositorio | `docs/equipo.md`, `docs/hardening.md`, `docs/limitaciones.md`, `docs/repositorio.md` | U3 · 3 y 4; subaspectos de sustentación |

## Detalle

### 1. Repositorio Git

Antes la carpeta no era un repositorio. Ahora está en GitHub con commits que explican cada cambio. No se suben datos pesados, modelos ni el `.env` con contraseñas (ver `.gitignore`).

**Pendiente del equipo:** agregar los *topics* en GitHub (engranaje junto a *About*): `campus-juliaca`, `semestre-2026-2`, `linea-cdia`, `tipo-ps`, `bigdata`, `seccion-<sección>`, `grupo-3-cryptopulse`.

### 2. Arranque robusto

Al correr el proyecto aparecieron tres fallos que impedían reproducirlo en otra computadora. `iniciar_producto.ps1` ahora:

- **Detecta puertos ocupados** por otro proyecto (por ejemplo lambda26) y muestra el comando para liberarlos, en lugar de fallar a medias.
- **Respalda los checkpoints de Spark** si Kafka empieza con un volumen nuevo. Antes el streaming se caía en bucle con *"Some data may have been lost"*.
- **Publica los KPIs históricos** si la base de datos está vacía. Antes la verificación fallaba con `batch_rows`.

### 3. Rutas relativas

La documentación decía `D:\bigdata\...` (72 veces), pero el proyecto vive en otra carpeta y otra persona lo clonará en otro lugar. Ahora las rutas son relativas al repositorio.

### 4. Divergencia BTC–SOL (Luz Milagros)

**Problema:** el modelo que predecía SOL − BTC **con signo** no le ganaba a "predecir 0", así que el producto mostraba una referencia en lugar de un modelo. La rúbrica exige un modelo en U1 y en U2.

**Solución:** se predice el **tamaño** de la separación, |SOL − BTC|. La dirección no es predecible, pero el tamaño sí, igual que la volatilidad.

| RMSE (más bajo es mejor) | Validación 2025 | Prueba 2026 |
|---|---|---|
| Referencia: promedio histórico | 0,244 | 0,198 |
| **Ridge (desplegado)** | **0,219** | **0,149** |

Comando nuevo: `python -m cryptopulse.training --divergence` (reentrena solo esta dimensión y conserva los demás modelos). El panel cambió a *Separación BTC–SOL · tamaño |SOL − BTC| a 15 min*.

### 5. Notebooks U1 por integrante

La guía dice que U1 se reporta **en un notebook propio de cada integrante**. Antes solo había notebooks de S01 y S02. Ahora hay cuatro, ya ejecutados y con gráficos:

| Notebook | Integrante | Ganador | Resultado en prueba 2026 |
|---|---|---|---|
| `01_volatilidad.ipynb` | Franck | Random Forest | RMSE 0,129 frente a 0,151 de la referencia |
| `02_caidas.ipynb` | Julmer | Logística L2 | AUC-PR 0,103 frente a 0,033 |
| `03_actividad_anomala.ipynb` | Abdul | Logística L2 | AUC-PR 0,660 frente a 0,072 |
| `04_divergencia.ipynb` | Luz Milagros | Lasso | RMSE 0,149 frente a 0,198 |

Todos tienen la misma estructura de 7 secciones, que corresponde a la rúbrica U1 (ver [Notebooks U1](notebooks-u1.md)). Se abren en JupyterLab, carpeta `u1-dimensiones`.

### 6. Eventos empresariales (criterio 1 de U2)

La rúbrica U2 pide **dos** ingestas: eventos empresariales e IoT/sensores. Antes había un solo flujo (velas). Ahora:

- **Telemetría (papel de sensor):** velas de 1 minuto → `market.klines.*` (ya existía).
- **Eventos empresariales (nuevo):** cada operación ejecutada en Binance (precio, cantidad, si la inició un comprador o un vendedor) → servicio `trades-producer` → tópicos `market.trades.*` → 4.ª consulta Spark (ventana de 1 min, watermark y deduplicación) → tabla `trade_flow` → nueva sección del tablero con el **flujo neto comprador − vendedor** y la **presión compradora**.

Contrato documentado en `schemas/market-trade-v1.schema.json`; pruebas en `cryptopulse/test_trades.py`.

### 7. Brief del equipo

`docs/proyecto-sello/brief.md` llena la plantilla de S2: pregunta central, arquitectura Lambda justificada, fuentes, la tabla de 8 filas (U1 y U2 de cada integrante) y una ficha con requisitos por dimensión.

**Pendiente del equipo:** completar la **sección** y revisar los **roles** de la tabla de integrantes (los asignó Claude; cámbienlos si no coinciden).

### 8. MkDocs

Sitio de documentación con la estructura de la plantilla de U3: Inicio, Instalación, Brief, U1, U2, U3, Equipo y Repositorio. Se publica solo en GitHub Pages en cada push.

### 9. CI

- `ci.yml`: en cada push corre las 45 pruebas unitarias, valida los JSON (tablero, contratos, configuración), los notebooks y los archivos Compose.
- `docs.yml`: publica la documentación.

### 10. Páginas de U3

- **Equipo:** quién hace qué, qué debe poder explicar cada uno y una tabla para registrar tareas.
- **Hardening:** checklist de 13 controles, pruebas, el **caso de error para la demo** (`prueba_recuperacion.ps1`) y los problemas corregidos.
- **Limitaciones y mejoras:** 7 limitaciones reales y mejoras priorizadas.

## Lo que falta y solo puede hacer el equipo

1. Topics del repositorio en GitHub.
2. Sección y roles en `docs/proyecto-sello/brief.md` y `docs/equipo.md`.
3. Activar GitHub Pages: *Settings → Pages → Branch: `gh-pages`*.
4. Que **cada integrante haga commits propios** (por ejemplo, revisar su notebook o su ficha del brief). La rúbrica revisa el aporte individual en el historial.
5. Llenar la tabla *Registro de tareas* en `docs/equipo.md`.
6. Diapositivas y video pitch de 3 minutos para S15.
7. Que cada integrante practique su parte con la sección *Qué debe poder explicar* de `docs/equipo.md`.

## Cómo comprobar que todo funciona

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar_producto.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verificar_producto.ps1
```

Último resultado: S03 a S12 **PASS**, producto **LISTO** con 7/7 pronósticos y 45 pruebas unitarias aprobadas.
