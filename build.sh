#!/usr/bin/env sh
set -e

echo "=== Build script: instalar dependencias y preprocesar ==="

# Ajusta si Railway ya instala requirements; este paso es seguro incluso si ya se ejecutó.
python -m pip install -r requirements.txt

# Ejecutar preprocesador (puedes cambiar métricas con la var PREPROCESS_METRICS)
: "${PREPROCESS_METRICS:=new_cases}"
echo "Preprocesando métricas: ${PREPROCESS_METRICS}"
for m in $(echo $PREPROCESS_METRICS | tr ',' ' '); do
  python -m covid_stats_app.preprocess --metric "$m" || echo "Aviso: preprocesor falló para $m (continuando)"
done

echo "=== Build terminado ==="
