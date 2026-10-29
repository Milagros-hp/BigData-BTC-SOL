# Notebooks U1 por integrante

Cada integrante tiene su propio notebook en `pyspark/sesiones/u1-dimensiones/`, con su dimensión, su variable objetivo y su modelo. Todos siguen la estructura de la rúbrica U1:

| Sección | Criterio de la rúbrica |
|---|---|
| 1. Extracción con `StructType` y `explain(True)` antes de la acción | 2. Uso correcto de Spark |
| 2. Nulos y duplicados (`row_number`, `dropDuplicates`, `na.drop`) con decisión documentada | 3. Calidad y formatos analíticos |
| 3. Parquet particionado: `PartitionFilters` en el plan y conteo reconciliado con el crudo | 3. Datos particionados y verificados |
| 4. Procesamiento con RDD (`map`, `reduceByKey`) | 2. Procesamiento distribuido |
| 5. Análisis descriptivo y diagnóstico con gráficos (2022–2026) | Dimensión descriptiva/diagnóstica |
| 6. Tres configuraciones de modelo y una referencia, al menos tres métricas, ganador guardado y recargado | 5. Componente ML distribuido |
| 7. Registro `verificacion_u1.json` | 4 y 6. Reproducible, con evidencia |

Partición temporal en los cuatro: **entrenamiento 2022–2024**, **validación 2025** (elige al ganador), **prueba enero–septiembre 2026** (se usa una sola vez), con 30 minutos de embargo entre tramos.

## Resultados

### 01 · Volatilidad — Franck Albertson Coaquira Justo

Regresión de la volatilidad realizada a 15 min. Referencia: persistencia (la volatilidad actual).

| Modelo | RMSE val. | MAE val. | R² val. |
|---|---|---|---|
| Referencia | 0,160 | 0,089 | 0,538 |
| Ridge | 0,142 | 0,086 | 0,635 |
| Lasso | 0,141 | 0,081 | 0,643 |
| **Random Forest** | **0,140** | **0,079** | **0,648** |

Prueba 2026: RMSE **0,129** frente a 0,151 de la referencia (−15 %). Es el mismo algoritmo que el producto despliega en vivo.

### 02 · Caídas — Julmer Quispe Apaza

Clasificación: rendimiento a 30 min ≤ P5 histórico (≈ 5 % de los casos). Referencia: prevalencia histórica por activo.

| Modelo | AUC-ROC | AUC-PR | Brier | Precisión | Recall | F1 |
|---|---|---|---|---|---|---|
| Referencia | 0,507 | 0,035 | 0,0335 | 0 | 0 | 0 |
| **Logística L2** | **0,795** | **0,125** | **0,0323** | 0,143 | 0,374 | 0,207 |
| Logística elastic-net | 0,754 | 0,108 | 0,0329 | 0,141 | 0,246 | 0,180 |
| Random Forest | 0,705 | 0,106 | 0,0329 | 0,113 | 0,394 | 0,175 |

Prueba 2026: AUC-PR **0,103** frente a 0,033 de la referencia (tres veces más). El producto usa esta misma regresión logística, calibrada.

### 03 · Actividad anómala — Abdul Quispe Condori

Clasificación: volumen u operaciones de los próximos 5 min sobre su P95 por activo y hora UTC.

| Modelo | AUC-ROC | AUC-PR | Brier | Precisión | Recall | F1 |
|---|---|---|---|---|---|---|
| Referencia | 0,706 | 0,341 | 0,188 | 0 | 0 | 0 |
| **Logística L2** | **0,930** | **0,820** | 0,112 | 0,701 | 0,753 | 0,726 |
| Logística elastic-net | 0,828 | 0,613 | 0,161 | 0,482 | 0,652 | 0,554 |
| Random Forest | 0,913 | 0,791 | 0,109 | 0,697 | 0,781 | 0,737 |

Prueba 2026: AUC-PR **0,660** frente a 0,072 de la referencia. Es la dimensión más predecible: la actividad alta tiende a continuar. El producto usa esta misma regresión logística, calibrada.

### 04 · Divergencia BTC–SOL — Luz Milagros Huanca Pacco

Regresión del tamaño de la separación |SOL − BTC| a 15 min. Referencia: promedio histórico de entrenamiento.

| Modelo | RMSE val. | MAE val. | R² val. |
|---|---|---|---|
| Referencia | 0,244 | 0,168 | −0,036 |
| Ridge | 0,219 | 0,147 | 0,165 |
| **Lasso** | **0,217** | **0,142** | **0,177** |
| Random Forest | 0,218 | 0,141 | 0,171 |

Prueba 2026: RMSE **0,149** frente a 0,198 de la referencia (−25 %). Los tres modelos quedan muy parejos. El producto en vivo despliega Ridge, que fue el ganador del pipeline de entrenamiento (donde Lasso no estaba entre los candidatos); la diferencia entre ambos es menor al 1 %.

## Cómo ejecutarlos

Requieren el batch ya preparado (`scripts/entrenar_producto.ps1`).

```powershell
docker compose -f .\pyspark\compose.yml up -d
Get-Content .\scripts\ejecutar_notebooks_u1.py -Raw | docker exec -i cryptopulse-pyspark python -
```

O bien en JupyterLab (<http://localhost:4488/lab?token=sintoken>), carpeta `u1-dimensiones`. Cada notebook usa unos 3 GB de memoria: si Docker tiene poca, pausa antes el streaming con `docker compose -f platform.yml stop streaming`.
