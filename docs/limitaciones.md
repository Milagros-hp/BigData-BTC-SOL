# Limitaciones y mejoras

## Limitaciones reconocidas

1. **Un solo nodo.** Spark corre en modo `local` dentro de Docker. Hay paralelismo, pero no un clúster de varias máquinas ni alta disponibilidad.
2. **Un broker Kafka.** Sin replicación: si el broker se pierde con su volumen, se pierde la retención de 7 días (el histórico batch no se pierde).
3. **Poder predictivo modesto.** Los mercados son ruidosos. Los modelos superan a referencias simples, pero sus errores son grandes en eventos extremos; por eso se muestran como señales de vigilancia, no como certezas.
4. **La dirección no se predice.** En divergencia solo se estima el tamaño de la separación, no qué activo rendirá más, porque la dirección no superó la referencia cero.
5. **Costos ilustrativos.** El panel de costos usa tarifas editables de `config/cost-assumptions.json`; no es una cotización de un proveedor de nube.
6. **Dos activos.** Solo BTCUSDT y SOLUSDT del mercado spot de Binance.
7. **Reentrenamiento manual.** Los modelos se reentrenan con un script; no hay reentrenamiento automático programado ni detección de deriva.

## Mejoras priorizadas

| Prioridad | Mejora | Beneficio |
|---|---|---|
| Alta | Detección de deriva y reentrenamiento programado | Modelos al día con el régimen de mercado |
| Alta | Kafka con 3 brokers y replicación | Tolerancia a fallos de la capa de velocidad |
| Media | Spark en clúster (Standalone o Kubernetes) | Escalar a más activos |
| Media | Más activos (ETH, BNB) reutilizando el mismo pipeline | Más cobertura con poco esfuerzo |
| Baja | Notificaciones (correo o Telegram) desde las alertas | El usuario no necesita mirar el tablero |
