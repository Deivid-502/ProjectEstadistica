#!/usr/bin/env sh
set -e

PORT=${PORT:-8080}
echo "Iniciando Streamlit en 0.0.0.0:${PORT}"

# Ejecutar la app como módulo de Python para que reconozca el paquete
streamlit run -m covid_stats_app.app --server.port=${PORT} --server.address=0.0.0.0
