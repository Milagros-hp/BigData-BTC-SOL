# Evidencias de ejecución

La rúbrica pide capturas con **el reloj de Windows y el usuario visibles**, con fechas coherentes con los commits. Cada integrante guarda aquí las suyas con el nombre `<integrante>-<numero>-<que-muestra>.png`.

| Captura | Qué debe verse | Quién |
|---|---|---|
| Notebook U1 ejecutado | Su notebook en JupyterLab, tabla de métricas y gráfico, con el reloj | Cada integrante |
| Panel U2 en vivo | Su panel en Grafana con pronóstico y real, con el reloj | Cada integrante |
| Estado LISTO | Panel *Estado integral* en 7/7 | Una por equipo |
| Verificación | Terminal con `verificar_producto.ps1` en PASS | Una por equipo |
| Kafka UI | Tópicos `market.klines.*` y `market.trades.*` con mensajes | Julmer |
| Prometheus | Reglas de alerta cargadas | Abdul |
| GitHub Actions | CI en verde | Luz Milagros |
| Caso de error | Estado DEGRADADO durante `prueba_recuperacion.ps1` y vuelta a LISTO | Una por equipo |
