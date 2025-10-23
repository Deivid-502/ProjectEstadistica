#!/usr/bin/env sh
set -e

# Asegurar que el directorio raíz del repo esté en PYTHONPATH
export PYTHONPATH=$(pwd)

# Use PORT provisto por Railway.
echo "Iniciando Streamlit en 0.0.0.0:${PORT}"
streamlit run covid_stats_app/app.py --server.port ${PORT} --server.address 0.0.0.0
