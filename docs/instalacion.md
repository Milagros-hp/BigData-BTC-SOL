# Instalación y ejecución

Pasos para levantar CryptoPulse desde cero en otra computadora, sin ayuda del equipo. Todos los comandos se ejecutan en **PowerShell**, desde la carpeta raíz del repositorio.

## Requisitos

| Requisito | Detalle |
|---|---|
| Windows 10/11 con Docker Desktop | Motor Linux activo (`docker version` debe mostrar *Server*) |
| Git | Para clonar el repositorio |
| Memoria | 8 GB libres para Docker (Spark streaming usa 3 GB) |
| Disco | ~3 GB para históricos y Parquet, más ~6 GB de imágenes |
| Internet | Descarga de históricos y datos en vivo de Binance; no se necesita clave API |

Puertos usados (solo `localhost`): Grafana `43000`, estado `48000`, Kafka UI `48085`, Prometheus `49090`, Kafka `49092`, Jupyter `4488`.

!!! warning "Otros proyectos del curso"
    `lambda26` usa los mismos puertos. Si está encendido, el arranque se detiene y muestra el comando para pausarlo:
    `docker stop (docker ps --filter "name=lambda26-" -q)`

## 1. Clonar

```powershell
git clone https://github.com/Milagros-hp/BigData-BTC-SOL.git
Set-Location BigData-BTC-SOL
Copy-Item .env.example .env
```

## 2. Preparar el batch (solo la primera vez)

Descarga los 114 archivos mensuales, verifica SHA256, aplica calidad (S03), escribe el Parquet particionado y entrena los cuatro modelos (S04). Tarda entre 30 y 90 minutos según el equipo.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\entrenar_producto.ps1
```

Al final debe mostrar `Batch verificado`. Para reentrenar solo la divergencia:

```powershell
docker compose -f .\platform.yml run --rm --no-deps tools python -m cryptopulse.training --divergence
```

## 3. Iniciar la plataforma

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar_producto.ps1
```

El script:

1. Comprueba Docker y construye las imágenes que falten.
2. Detiene el arranque si otro proyecto ocupa los puertos.
3. Si Kafka arranca con un volumen nuevo, respalda los checkpoints viejos de Spark en `pyspark/sesiones/_runtime/backups/`.
4. Levanta los 10 servicios, aplica las migraciones y publica el registro de modelos.
5. Si la base de datos es nueva, publica los KPIs históricos (unos minutos).
6. Espera hasta que el producto esté **LISTO**: 61 velas consecutivas por activo y 7 pronósticos recientes. La primera vez tarda unos 5 minutos.

## 4. Verificar

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verificar_producto.ps1
```

Comprueba S03 a S12 y termina sin errores. Si cambiaste los modelos, primero repite las pruebas de integración:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\pruebas_integracion.ps1
```

## 5. Abrir las interfaces

| Interfaz | Dirección | Acceso |
|---|---|---|
| Tablero Grafana | <http://localhost:43000/d/cryptopulse-main> | `admin` / valor de `GRAFANA_PASSWORD` en `.env` |
| Estado JSON | <http://localhost:48000/api/status> | Libre |
| Kafka UI | <http://localhost:48085> | Libre |
| Prometheus | <http://localhost:49090> | Libre |
| JupyterLab | <http://localhost:4488/lab?token=sintoken> | Token `sintoken` |

## 6. Notebooks U1

```powershell
docker compose -f .\pyspark\compose.yml up -d
Get-Content .\scripts\ejecutar_notebooks_u1.py -Raw | docker exec -i cryptopulse-pyspark python -
```

Ejecuta los cuatro notebooks de `pyspark/sesiones/u1-dimensiones/` y guarda sus resultados. También se pueden abrir y correr celda por celda en JupyterLab.

## 7. Detener

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\detener_producto.ps1
docker compose -f .\pyspark\compose.yml stop
```

Se conservan volúmenes, modelos y checkpoints.

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `port is already allocated` o aviso de puertos ocupados | Otro proyecto (lambda26) usa los puertos | `docker stop` a los contenedores indicados |
| El streaming se reinicia en bucle con `Some data may have been lost` | Checkpoints de un Kafka anterior | El arranque ya los respalda solo; si ocurre manualmente, mover `pyspark/sesiones/_runtime/checkpoints` a `backups/` |
| La verificación falla en `batch_rows` | Base de datos nueva sin KPIs históricos | Volver a ejecutar `iniciar_producto.ps1` (los publica solo) |
| La verificación dice que las pruebas de integración son de otra versión | Se cambió un modelo | Ejecutar `pruebas_integracion.ps1` |
| Grafana pide contraseña | Volumen nuevo de Grafana | Usuario `admin`, contraseña de `GRAFANA_PASSWORD` en `.env` |
