# Producto de Unidad 3 · Producto final · CryptoPulse

Plantilla del docente: [Producto U3](https://262bigdata.github.io/lambda26/proyecto-sello/u3-producto/).

## Producto

**Sistema Big Data distribuido end-to-end para procesamiento batch y streaming, analítica/ML, observabilidad y visualización BI para la toma de decisiones:** U1 y U2 integradas, endurecidas, documentadas y demostrables con un solo comando.

## 1. Componentes mínimos

| Componente exigido | Estado | Evidencia |
|---|---|---|
| Problema delimitado y arquitectura justificada | ✅ | [Brief](brief.md), [Producto U1 §1](u1-producto.md#1-arquitectura-big-data-seleccionada) |
| Pipeline batch con Spark y calidad | ✅ | `quality.py`, notebooks U1 |
| Salida analítica particionada en Parquet | ✅ | `clean_parquet/symbol/year/month` |
| Ingesta de eventos empresariales e IoT con Kafka | ✅ | `trades.py` (operaciones) y `producer.py` (velas) |
| Streaming con ventanas y watermarking | ✅ | `stream.py`, 4 consultas |
| Observabilidad, paneles y costos | ✅ | Prometheus, 8 alertas, [costos y escalado](u2-producto.md#costos) |
| Modelo ML, inferencia y salida BI | ✅ | 4 modelos, inferencia cada minuto y tablero único |
| Prácticas DataOps/DevOps | ✅ | Docker Compose, scripts idempotentes, modelos versionados, CI en GitHub Actions |
| Evidencias reproducibles | 🔄 | `verificar_producto.ps1`; capturas con reloj en [evidencias](../evidencias/README.md) (las toma cada integrante) |
| Documentación y demo end-to-end | ✅ | Este sitio y [Instalación](../instalacion.md) |

## 2. Rúbrica y evidencia

| Criterio | Peso | Evidencia |
|---|---:|---|
| 1. Integración end-to-end batch + streaming + BI/ML | 20% | Los modelos entrenados en batch se aplican en vivo a cada vela de Kafka y se ven en Grafana; `verificar_producto.ps1` comprueba S03–S12 juntos |
| 2. DataOps/DevOps | 15% | `platform.yml`, `scripts/`, versiones fijadas, `.github/workflows/ci.yml` (45 pruebas en cada push), `docs.yml` |
| 3. Documentación operativa | 15% | Este sitio MkDocs; [Instalación](../instalacion.md) paso a paso con problemas frecuentes |
| 4. Hardening y revisión técnica | 10% | [Checklist de 13 controles](../hardening.md) y problemas encontrados y corregidos |
| 5. Demo reproducible | 15% | Clonar → `entrenar_producto.ps1` → `iniciar_producto.ps1` → `verificar_producto.ps1` |
| 6. Sustentación técnica | 25% | Secuencia de la sección 3 de esta página; [Equipo](../equipo.md) |

## 3. Secuencia de presentación (S15)

| Orden | Momento | Quién | Apoyo |
|---:|---|---|---|
| 1 | Título y equipo | Luz Milagros | Portada |
| 2 | Video pitch (3 min) | Todos | Problema, solución y valor |
| 3 | Problema y alcance | Luz Milagros | Pregunta central y dimensiones ([Brief](brief.md)) |
| 4 | Arquitectura Lambda | Franck | Diagrama de [Inicio](../index.md) |
| 5 | Procesamiento batch | Franck | Notebook 01: calidad, Parquet y modelo |
| 6 | Ingesta y streaming | Julmer | Kafka UI con los dos flujos; `stream.py` |
| 7 | Observabilidad y costos | Abdul | Prometheus, alertas y escalado |
| 8 | Resultados BI/ML | Los cuatro | Cada uno su panel y su métrica frente a la referencia |
| 9 | Demo end-to-end | Luz Milagros | Arranque → LISTO → caso de error → recuperación |
| 10 | Aporte individual | Los cuatro | [Equipo](../equipo.md) y commits |
| 11 | Repositorio y estándares | Luz Milagros | GitHub, topics, CI en verde, este sitio |
| 12 | Limitaciones y mejoras | Abdul | [Limitaciones](../limitaciones.md) |

Los responsables son una propuesta; ajústenla según quién domina cada parte.

## 4. Documentación mínima (plantilla del docente, Tabla 4)

| Sección exigida | Página |
|---|---|
| Inicio | [Inicio](../index.md) |
| Instalación o ejecución | [Instalación y ejecución](../instalacion.md) |
| Uso del sistema | [Uso del tablero](../PRODUCTO_FINAL.md) |
| Arquitectura o estructura | [Informe técnico](../INFORME_PROYECTO_CRYPTOPULSE.md), [Repositorio](../repositorio.md) |
| Módulos o funcionalidades | [Producto U2 §1](u2-producto.md#1-alcance-de-capacidades-por-sesion) |
| Datos | [Producto U1](u1-producto.md), [Brief §2](brief.md#2-dominio-del-proyecto) |
| Pruebas y evidencias | [Hardening](../hardening.md), [Notebooks U1](../notebooks-u1.md), [Evidencias](../evidencias/README.md) |
| Equipo y aporte individual | [Equipo](../equipo.md) |
| Repositorio y estándares | [Repositorio](../repositorio.md) |
| Limitaciones y mejoras | [Limitaciones](../limitaciones.md) |
