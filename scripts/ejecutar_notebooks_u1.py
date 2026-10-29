"""Ejecutar dentro de cryptopulse-pyspark. Corre los notebooks U1 y guarda sus salidas en el mismo archivo."""
import json
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

carpeta = Path("/opt/u1-dimensiones")
seleccion = sys.argv[1:] or sorted(p.name for p in carpeta.glob("[0-9][0-9]_*.ipynb"))
for nombre in seleccion:
    ruta = carpeta / nombre
    print("Ejecutando", ruta, flush=True)
    notebook = nbformat.read(ruta, as_version=4)
    cliente = NotebookClient(notebook, timeout=1800, kernel_name="python3",
                             resources={"metadata": {"path": str(carpeta)}})
    try:
        cliente.execute()
    finally:
        nbformat.write(notebook, ruta)
    slug = ruta.stem.split("_", 1)[1]
    resultado = json.loads((carpeta / "artifacts" / slug / "verificacion_u1.json").read_text(encoding="utf-8"))
    if resultado["status"] != "PASS":
        raise RuntimeError(f"{nombre} no paso la verificacion")
    print(nombre, "PASS | ganador:", resultado["modelo_ganador"], flush=True)
