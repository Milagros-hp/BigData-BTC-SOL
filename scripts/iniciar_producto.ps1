param([switch]$Reconstruir,[int]$EsperarSegundos=240)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$composeFile=Join-Path $projectRoot 'platform.yml'
$registry=Join-Path $projectRoot 'pyspark\sesiones\s04-modelos\artifacts\model_registry.json'
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Abre Docker Desktop y espera a que el motor Linux este listo.' }
if (-not (Test-Path -LiteralPath $registry)) { throw 'Primero ejecuta scripts\entrenar_producto.ps1 para generar los modelos.' }
$envFile=Join-Path $projectRoot '.env'
if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath (Join-Path $projectRoot '.env.example') -Destination $envFile
}
$localImages=@(docker image ls --format '{{.Repository}}:{{.Tag}}')
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron consultar las imagenes Docker.' }
if ($localImages -notcontains 'cryptopulse-pyspark-pyspark:latest') {
    docker compose -f (Join-Path $projectRoot 'pyspark\compose.yml') build
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo construir la imagen base PySpark.' }
}
if ($Reconstruir -or $localImages -notcontains 'cryptopulse-runtime:local') {
    docker compose --env-file $envFile -f $composeFile build tools
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo construir el runtime.' }
}
# Otros proyectos del curso (por ejemplo lambda26) publican los mismos puertos.
$ports=@(43000,48000,48085,49090,49092)
$busy=@(docker ps --format '{{.Names}} {{.Ports}}' | Where-Object { $_ -notmatch '^cryptopulse-' } | Where-Object {
    $line=$_; @($ports | Where-Object { $line -match (':' + $_ + '->') }).Count -gt 0
} | ForEach-Object { ($_ -split ' ')[0] })
if ($busy.Count -gt 0) {
    throw ("Estos contenedores usan los puertos de CryptoPulse: " + ($busy -join ', ') + ". Detenlos con: docker stop " + ($busy -join ' '))
}

# Si Kafka arranca con un volumen nuevo, los checkpoints guardan offsets que ya no existen y
# el streaming se detiene en bucle. Se respaldan en lugar de borrarse.
$checkpoints=Join-Path $projectRoot 'pyspark\sesiones\_runtime\checkpoints'
docker volume inspect cryptopulse_kafka_data *> $null
$kafkaVolumeExists=($LASTEXITCODE -eq 0)
if (-not $kafkaVolumeExists -and (Test-Path -LiteralPath $checkpoints) -and @(Get-ChildItem -LiteralPath $checkpoints).Count -gt 0) {
    $backups=Join-Path $projectRoot 'pyspark\sesiones\_runtime\backups'
    New-Item -ItemType Directory -Force -Path $backups | Out-Null
    $target=Join-Path $backups ('checkpoints-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    Move-Item -LiteralPath $checkpoints -Destination $target
    Write-Host "Kafka nuevo: checkpoints anteriores respaldados en $target"
}

docker compose --env-file $envFile -f $composeFile up -d --no-build
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar el producto.' }

# Las migraciones se aplican tambien sobre volumenes existentes, sin borrar datos.
Get-ChildItem -LiteralPath (Join-Path $projectRoot 'database\migrations') -Filter '*.sql' | Sort-Object Name | ForEach-Object {
    Get-Content -LiteralPath $_.FullName -Raw | docker compose --env-file $envFile -f $composeFile exec -T postgres psql -U cryptopulse -d cryptopulse -v ON_ERROR_STOP=1
    if ($LASTEXITCODE -ne 0) { throw "Fallo la migracion $($_.Name)." }
}
docker compose --env-file $envFile -f $composeFile run --rm --no-deps tools python -m cryptopulse.publish_batch --metadata-only
if ($LASTEXITCODE -ne 0) { throw 'No se pudo publicar el registro de modelos.' }
# En una base de datos nueva los KPIs historicos aun no existen; se cargan una sola vez.
$batchRows=docker compose --env-file $envFile -f $composeFile exec -T postgres psql -U cryptopulse -d cryptopulse -tAc 'SELECT count(*) FROM batch_kpis'
if ($LASTEXITCODE -ne 0) { throw 'No se pudo consultar batch_kpis.' }
if ([int]"$batchRows".Trim() -eq 0) {
    Write-Host 'Base de datos nueva: publicando KPIs historicos (tarda unos minutos).'
    docker compose --env-file $envFile -f $composeFile run --rm --no-deps tools python -m cryptopulse.publish_batch
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron publicar los KPIs historicos.' }
}
docker compose --env-file $envFile -f $composeFile ps
Write-Host 'Grafana: http://localhost:43000/d/cryptopulse-main'
Write-Host 'Kafka UI: http://localhost:48085'
Write-Host 'Estado JSON: http://localhost:48000/api/status'
$deadline=(Get-Date).AddSeconds($EsperarSegundos)
$ready=$false
while ((Get-Date) -lt $deadline) {
    try {
        $health=Invoke-RestMethod -Uri 'http://localhost:48000/api/status' -TimeoutSec 5
        if ($health.health.ready) { $ready=$true; break }
    } catch { }
    Start-Sleep -Seconds 5
}
if (-not $ready) { throw 'Los servicios arrancaron, pero el producto no esta listo. Consulta http://localhost:48000/api/status para ver los motivos; no se borro ningun dato.' }
Write-Host 'Producto LISTO: datos consecutivos y siete pronosticos recientes.'
