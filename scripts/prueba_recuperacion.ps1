param([int]$SegundosPausa=75)
$ErrorActionPreference='Stop'
if ($SegundosPausa -lt 70 -or $SegundosPausa -gt 120) { throw 'La pausa de prueba debe ser de 70 a 120 segundos.' }
$root=Split-Path -Parent $PSScriptRoot
$compose=Join-Path $root 'platform.yml'
$evidence=Join-Path $root 'pyspark\sesiones\_runtime\recovery_acceptance.json'
function Snapshot { return (Invoke-RestMethod -Uri 'http://localhost:48000/api/status' -TimeoutSec 10) }
$before=Snapshot
if (-not $before.health.ready) { throw 'El producto debe estar listo antes de probar su recuperacion.' }
$record=[ordered]@{status='RUNNING';before=$before.health;pause_seconds=$SegundosPausa}
Write-Host 'Pausando solo el productor para comprobar deteccion del fallo y recuperacion sin huecos.'
docker compose -f $compose stop producer
if ($LASTEXITCODE -ne 0) { throw 'No se pudo pausar el productor.' }
try {
    $remaining=$SegundosPausa
    while ($remaining -gt 0) { $step=[Math]::Min(30,$remaining); Start-Sleep -Seconds $step; $remaining-=$step }
    $during=Snapshot
    $record.during=$during.health
    if ($during.health.ready) { throw 'La salud permanecio verde tras detener el productor: fallo de deteccion.' }
    Write-Host 'Degradacion detectada correctamente; restaurando la ingesta.'
} finally {
    docker compose -f $compose up -d --no-deps producer
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo restaurar el productor.' }
}
$deadline=(Get-Date).AddMinutes(4)
$after=$null
do {
    Start-Sleep -Seconds 5
    $after=Snapshot
    if ($after.health.ready) { break }
} while ((Get-Date) -lt $deadline)
$record.after=$after.health
if (-not $after.health.ready) { $record.status='FAIL'; $record | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $evidence -Encoding UTF8; throw 'No se recupero el producto dentro del plazo.' }
if (@($after.health.symbols | Where-Object {$_.missing_minutes -ne 0}).Count -gt 0) { throw 'La recuperacion dejo un hueco.' }
Write-Host 'Velas: PASS. Pausando el productor de operaciones.'
docker compose -f $compose stop trades-producer
if ($LASTEXITCODE -ne 0) { throw 'No se pudo pausar el productor de operaciones.' }
$pausedAt=[DateTimeOffset]::UtcNow
try {
    Start-Sleep -Seconds $SegundosPausa
    $duringTrades=(Snapshot).health
    $record.during_trades=$duringTrades
    if ($duringTrades.ready -or @($duringTrades.reasons | Where-Object {$_.code -eq 'trades_producer_stale'}).Count -eq 0) { throw 'La salud no detecto la caida del productor de operaciones.' }
    Write-Host 'Degradacion por operaciones detectada; restaurando.'
} finally {
    docker compose -f $compose up -d --no-deps trades-producer
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo restaurar el productor de operaciones.' }
}
$deadline=(Get-Date).AddMinutes(5)
do { Start-Sleep -Seconds 10; $afterTrades=(Snapshot).health } while (-not $afterTrades.ready -and (Get-Date) -lt $deadline)
if (-not $afterTrades.ready) { throw 'No se recupero el flujo de operaciones dentro del plazo.' }
# Las ventanas de la pausa deben cerrarse con las operaciones recuperadas por REST.
Start-Sleep -Seconds 150
$from=$pausedAt.ToUnixTimeSeconds()
$sql="SELECT count(*) FROM generate_series(to_timestamp($from-($from%60)),to_timestamp($from-($from%60)+$SegundosPausa),interval '1 minute') m LEFT JOIN trade_flow t ON t.symbol='BTCUSDT' AND t.window_start=m WHERE t.symbol IS NULL"
$missing=docker compose -f $compose exec -T postgres psql -U cryptopulse -d cryptopulse -tAc $sql
if ($LASTEXITCODE -ne 0) { throw 'No se pudo consultar trade_flow.' }
if ([int]"$missing".Trim() -ne 0) { throw "Faltan $missing minutos de operaciones tras la recuperacion." }
$record.after_trades=$afterTrades
$record.status='PASS'
$record.verified_at=(Get-Date).ToString('o')
$record | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $evidence -Encoding UTF8
Write-Host 'PASS: velas y operaciones: fallo detectado, productores restaurados y sin huecos.'
