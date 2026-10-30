# Pruebas, hardening y DataOps

## Checklist de hardening

| # | Control | Estado | Cómo se verifica |
|---|---|---|---|
| 1 | Versiones fijadas de imágenes y librerías | Hecho | `platform.yml`, `pyspark/Dockerfile`, `runtime/Dockerfile` |
| 2 | Servicios solo en `localhost` | Hecho | Todos los puertos publicados con `127.0.0.1:` en `platform.yml` |
| 3 | Secretos fuera del repositorio | Hecho | `.env` en `.gitignore`; el repo solo trae `.env.example` con valores locales |
| 4 | Reinicio automático y healthchecks | Hecho | `restart: unless-stopped`; healthchecks de Kafka y PostgreSQL |
| 5 | Idempotencia ante reintentos | Hecho | Claves únicas en PostgreSQL; prueba `prediction_upsert_idempotent` |
| 6 | Datos tardíos y duplicados | Hecho | Watermark de 2 min y deduplicación por `event_id`; prueba de integración |
| 7 | Reinicio desde checkpoint | Hecho | Prueba `checkpoint_restart_recovered` |
| 8 | Sin fuga de información futura | Hecho | Prueba `future_mutation_does_not_change_past_features`; embargo de 30 min entre particiones |
| 9 | Recuperación ante caída de la ingesta | Hecho | `scripts/prueba_recuperacion.ps1` |
| 10 | Arranque en equipo limpio | Hecho | `iniciar_producto.ps1` detecta puertos ocupados, respalda checkpoints obsoletos y publica KPIs si la base está vacía |
| 11 | Alertas operativas | Hecho | 11 reglas en `observability/alerts.yml` (exportador caído, datos atrasados, streaming detenido, lag Kafka, WebSocket, predicción atrasada, hueco, producto degradado) |
| 12 | Integración continua | Hecho | `.github/workflows/ci.yml`: pruebas unitarias, validación de Compose y JSON en cada push |
| 13 | Documentación reproducible | Hecho | Este sitio MkDocs, publicado con `.github/workflows/docs.yml` |

## Pruebas automatizadas

| Tipo | Cantidad | Comando |
|---|---|---|
| Unitarias (ingesta, contratos de velas y operaciones, señales, salud, calibración, reparación de checkpoints) | 45 | `docker compose -f platform.yml run --rm --no-deps tools python -m unittest cryptopulse.test_trades cryptopulse.test_health cryptopulse.test_signals cryptopulse.test_stream_contract cryptopulse.test_training_calibration cryptopulse.test_ingestion` |
| Spark con modelos reales | 5 | `... python -m unittest cryptopulse.test_inference_spark` |
| Integración aislada (Kafka, watermark, checkpoint, replay) | 1 suite | `scripts/pruebas_integracion.ps1` |
| Verificación integral S03–S12 | 1 suite | `scripts/verificar_producto.ps1` |
| Recuperación ante fallo real | 1 | `scripts/prueba_recuperacion.ps1` |

## Caso de error para la demo

`prueba_recuperacion.ps1` detiene el productor entre 70 y 120 segundos y comprueba tres cosas:

1. El estado pasa de **LISTO** a **DEGRADADO**, es decir, el fallo se detecta.
2. Al reanudar, el productor recupera por REST las velas perdidas.
3. El producto vuelve a **LISTO** sin huecos ni duplicados.

Durante la demo se puede ver el cambio en el panel *Estado integral* de Grafana y en <http://localhost:48000/api/status>.

## Prácticas DataOps

- **Infraestructura como código:** toda la plataforma se define en `platform.yml` y `pyspark/compose.yml`.
- **Scripts idempotentes:** cada script de `scripts/` se puede repetir sin borrar datos (iniciar, entrenar, verificar, detener).
- **Modelos versionados:** cada entrenamiento crea una versión nueva en `model_registry.json` y guarda una copia de la anterior en `registries/`.
- **Tablero como código:** `scripts/generar_dashboard.py` genera el JSON de Grafana, que se provisiona automáticamente.
- **CI en GitHub Actions:** las pruebas corren en cada push.

## Problemas encontrados y corregidos

| Problema | Corrección |
|---|---|
| Con una base de datos nueva, la verificación fallaba porque faltaban los KPIs históricos | El arranque los publica automáticamente |
| Con un Kafka nuevo, el streaming se caía en bucle por checkpoints obsoletos | El arranque detecta el volumen nuevo y respalda los checkpoints |
| Choque de puertos con lambda26 | El arranque se detiene con un mensaje claro y el comando para resolverlo |
| Rutas fijas `D:\bigdata` en la documentación | Rutas relativas al repositorio |
| Un apagado brusco dejó checkpoints de Spark llenos de ceros y el streaming se reiniciaba en bucle (30 de octubre) | Al arrancar, `stream.py` detecta archivos corruptos, los respalda en `_runtime/backups/` y continúa con checkpoints nuevos |
| El modelo de divergencia no superaba a la referencia | Se reformuló como tamaño de la separación; ahora supera a la referencia en validación y prueba |
