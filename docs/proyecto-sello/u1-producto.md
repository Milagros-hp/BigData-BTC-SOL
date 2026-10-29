# Producto de Unidad 1 · CryptoPulse

Plantilla del docente: [Producto U1](https://262bigdata.github.io/lambda26/proyecto-sello/u1-producto/). Aquí se adapta a nuestro instrumento: velas de 1 minuto de BTCUSDT y SOLUSDT de Binance.

## Producto

**Pipeline batch de ETL distribuido con salidas analíticas en Parquet listas para BI/ML.**

114 archivos mensuales oficiales (enero 2022 – septiembre 2026, SHA256 verificado) → PySpark con esquema explícito → controles de calidad, cuarentena y registro de huecos → Parquet particionado por `symbol/year/month` → variables temporales → cuatro modelos MLlib, uno por integrante, con validación temporal.

| Integrante | Dimensión U1 | Notebook |
|---|---|---|
| Franck Albertson Coaquira Justo | Volatilidad | `pyspark/sesiones/u1-dimensiones/01_volatilidad.ipynb` |
| Julmer Quispe Apaza | Caídas significativas | `pyspark/sesiones/u1-dimensiones/02_caidas.ipynb` |
| Abdul Quispe Condori | Actividad anómala | `pyspark/sesiones/u1-dimensiones/03_actividad_anomala.ipynb` |
| Luz Milagros Huanca Pacco | Divergencia BTC–SOL | `pyspark/sesiones/u1-dimensiones/04_divergencia.ipynb` |

## 1. Arquitectura Big Data seleccionada

**Lambda.** La capa batch necesita el histórico completo en bloque para describir el pasado y entrenar; la capa de velocidad necesita reaccionar a cada vela en segundos con esos mismos modelos. Kappa obligaría a reprocesar 4,99 millones de velas a través de Kafka para cada reentrenamiento, sin ventaja para este caso.

Diagrama y justificación completos: [Informe técnico, sección 2](../INFORME_PROYECTO_CRYPTOPULSE.md#2-arquitectura-implementada).

## 2. Transformaciones distribuidas con PySpark

| Requisito | Evidencia |
|---|---|
| Extracción con esquema explícito | Sección 1 de cada notebook U1 (`StructType` con `DecimalType(28,8)`); `cryptopulse/quality.py` |
| `withColumn()` / `filter()` | Conversión de microsegundos a milisegundos, `rango_pct`, `hora_utc`, filtro de velas sin operaciones |
| `groupBy().agg()` | Resumen por hora UTC (sección 1) y agregaciones mensuales (sección 5) |
| Plan de ejecución y evaluación perezosa | `explain(True)` antes de la acción; la acción `toPandas()` ejecuta el plan |
| Procesamiento RDD | Sección 4: `map` + `reduceByKey` para la distribución del rango intravela |

## 3. Calidad de datos y particionamiento analítico

| Control | Qué verifica | Evidencia en CryptoPulse |
|---|---|---|
| Esquema explícito | Tipos correctos desde la lectura | `StructType` en `quality.py` y en cada notebook |
| Duplicados | Filas repetidas identificadas antes de eliminarlas | `Window` + `row_number()` por minuto; `dropDuplicates(["open_ms"])`. Resultado: 0 duplicados |
| Nulos | Detección y decisión explícita | Conteo por columna; `na.drop` en obligatorias. **Decisión:** no se imputan precios; las filas inválidas van a cuarentena |
| Particionamiento | Parquet por columnas de bajo cardinal usadas en filtros | `s03-calidad/artifacts/clean_parquet/symbol=…/year=…/month=…` |
| Verificación de ida y vuelta | Conteo reconciliado y `PartitionFilters` en el plan | Sección 3 de cada notebook: `assert` de `PartitionFilters` y de igualdad de conteos (44 640 = 44 640 en BTC marzo 2025) |

Resultado global de S03: **4 993 759 filas → 4 993 757 válidas**, 2 en cuarentena y 3 huecos (163 minutos) registrados sin inventar velas.

## 4. Componente ML distribuido

| Componente | Evidencia |
|---|---|
| Vector de predictores | `VectorAssembler` con 14 variables (rendimientos, volatilidades, volumen, rango, hora codificada) |
| Entrenado y evaluado sin fuga | Entrenamiento 2022–2024, validación 2025, prueba 2026, con 30 min de embargo |
| Comparación de configuraciones | Tres por integrante: Ridge, Lasso y Random Forest (regresión), o logística L2, elastic-net y Random Forest (clasificación), más una referencia |
| Modelo guardado | `write().overwrite().save()` del **ganador en validación** y recarga con `PipelineModel.load` |

| Integrante | Métricas | Ganador | Prueba 2026 frente a la referencia |
|---|---|---|---|
| Franck | RMSE, MAE, R² | Random Forest | RMSE 0,129 frente a 0,151 |
| Julmer | AUC-ROC, AUC-PR, Brier, precisión, recall, F1 | Logística L2 | AUC-PR 0,103 frente a 0,033 |
| Abdul | AUC-ROC, AUC-PR, Brier, precisión, recall, F1 | Logística L2 | AUC-PR 0,660 frente a 0,072 |
| Luz Milagros | RMSE, MAE, R² | Lasso | RMSE 0,149 frente a 0,198 |

Detalle por integrante: [Notebooks U1](../notebooks-u1.md).

## 5. Rúbrica y evidencia

| Criterio | Peso | Evidencia principal |
|---|---:|---|
| 1. Arquitectura seleccionada y justificada | 12% | Sección 1 de esta página; brief, sección 2 |
| 2. Uso correcto de Spark/PySpark | 16% | Secciones 1, 4 y 5 de cada notebook, con `explain(True)` |
| 3. Datos particionados en formatos analíticos | 16% | Sección 3 de cada notebook (`PartitionFilters` y conteo reconciliado) |
| 4. Pipeline batch reproducible | 12% | `scripts/entrenar_producto.ps1` y `scripts/ejecutar_notebooks_u1.py` corren sin intervención |
| 5. Primer componente ML distribuido | 16% | Sección 6 de cada notebook: 3 configuraciones, 3 o más métricas y ganador guardado |
| 6. Evidencias y documentación | 8% | `verificacion_u1.json` por notebook, [evidencias](../evidencias/README.md) con reloj y este sitio |
| 7. Sustentación | 20% | Cada integrante defiende su notebook ([Equipo](../equipo.md)) |

## Subaspectos de la sustentación U1

| Subaspecto | Cómo lo cubrimos |
|---|---|
| 1. Aporte individual | Un notebook y un modelo propios por integrante |
| 2. Comunicación y orden | Orden fijo de los notebooks: extracción → calidad → partición → RDD → descriptivo → modelo |
| 3. Presentación personal y actitud | Responsabilidad de cada integrante |
| 4. Repositorio y estándares | Topics, commits por integrante, notebooks reproducibles |
| 5. MkDocs | Esta página y [Notebooks U1](../notebooks-u1.md) |
| 6. Pitch/demo ejecutiva | Diapositiva por integrante: pregunta, gráfico principal y modelo ganador |
