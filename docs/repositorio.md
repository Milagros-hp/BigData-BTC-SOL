# Repositorio y estándares

## Topics académicos

Configurados en GitHub (*About → Topics*):

```text
campus-juliaca
semestre-2026-2
linea-cdia
tipo-ps
bigdata
seccion-<sección>
grupo-3-cryptopulse
```

## Estructura

```text
BigData-BTC-SOL/
├── platform.yml              # Plataforma completa: Kafka, Spark streaming, PostgreSQL, Grafana, Prometheus
├── config/                   # Rango de datos y supuestos de costos
├── database/                 # Esquema y migraciones PostgreSQL
├── docs/                     # Este sitio MkDocs
├── observability/            # Prometheus, reglas de alerta y tablero Grafana provisionado
├── pyspark/
│   ├── compose.yml           # JupyterLab + Spark para notebooks
│   └── sesiones/
│       ├── s01-arquitectura/ # Notebook S01
│       ├── s02-fundamentos/  # Notebook S02 y descarga de históricos
│       ├── u1-dimensiones/   # Un notebook U1 por integrante
│       └── cryptopulse/      # Código del pipeline (calidad, features, entrenamiento, streaming, inferencia)
├── runtime/                  # Imagen de ejecución (PySpark + Kafka + PostgreSQL)
├── schemas/                  # Contrato JSON de los eventos Kafka
├── scripts/                  # Iniciar, entrenar, verificar, detener, pruebas
└── .github/workflows/        # CI y publicación de la documentación
```

No se versionan los datos descargados, el Parquet, los modelos ni los checkpoints: se regeneran con `scripts/entrenar_producto.ps1` (ver [Instalación](instalacion.md)).

## Reproducibilidad

- Un solo comando levanta el sistema: `scripts/iniciar_producto.ps1`.
- Un solo comando lo verifica: `scripts/verificar_producto.ps1`.
- Las versiones de todas las imágenes y librerías están fijadas.
- La CI ejecuta las pruebas en cada push.
