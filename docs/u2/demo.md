# Guion de la exposición

Pitch breve y luego demo técnica, como pide la rúbrica. Las duraciones son una propuesta; ajústenlas al tiempo que asigne el docente.

## Antes de entrar

1. Encender el producto al menos 35 minutos antes, para que maduren los pronósticos a 30 minutos:

    ```powershell
    powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar_producto.ps1
    powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verificar_producto.ps1
    ```

2. Abrir [Grafana](http://localhost:43000/d/cryptopulse-main), [Kafka UI](http://localhost:48085), [Prometheus](http://localhost:49090/alerts) y esta documentación.

## Pitch

| Tiempo | Quién | Qué decir | Apoyo |
|---|---|---|---|
| 1 min | Luz Milagros | Problema, pregunta central y evolución desde U1 | [Portada](index.md) |
| 1 min | Julmer | Arquitectura y flujos | [Arquitectura](index.md#arquitectura) |
| 1 min | Abdul | Lo que probamos y la lectura honesta de los modelos | [Pruebas](index.md#lo-que-probamos-no-solo-lo-que-construimos) |

## Demo técnica

| Tiempo | Quién | Acción | Criterio |
|---|---|---|---|
| 3 min | Julmer | Kafka UI: abrir un mensaje de operación y uno de vela. Mostrar `stream.py` y las ventanas. Exponer su panel de caída | 1, 2, 3 y 7 |
| 3 min | Abdul | Prometheus: destinos y reglas. Correlacionar lotes y pendientes. Costos y su panel de actividad | 4, 5 y 7 |
| 2 min | Franck | Panel de volatilidad: pronóstico, realidad posterior y error | 6 y 7 |
| 2 min | Luz Milagros | Tablero completo, señales, panel de separación y CI | 6 y 7 |
| 2 min | Equipo | En otra terminal, ejecutar `prueba_recuperacion.ps1` y mostrar DEGRADADO y LISTO | 3 y 4 |

La prueba de recuperación completa tarda varios minutos. Conviene lanzarla al inicio de la demo y volver a ella al final.

## Preguntas probables del jurado

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué velas como IoT? | La guía admite telemetría. Es una lectura periódica de frecuencia fija, real y sin simulación. |
| ¿Qué pasa si cae un productor? | El estado pasa a degradado, se dispara una alerta, y al volver recupera lo faltante por REST. |
| ¿Es exactamente una vez? | No. Es al menos una vez, con resultados idempotentes y deduplicación por `event_id`. |
| ¿Sus modelos funcionan? | En la prueba 2026 los cuatro superan su referencia. En vivo solo llevamos poco tiempo, y volatilidad es la única que ya la supera con claridad. |
| ¿Es costo real? | No. Son tarifas ilustrativas y editables, aplicadas a recursos y volumen medidos. |
| ¿Escala? | Es un broker y Spark local. Los umbrales para escalar están documentados por señal medida. |
