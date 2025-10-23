#!/usr/bin/env sh
set -e

# Use PORT provisto por Railway. No usar valor por defecto que no coincida.
echo "Iniciando Streamlit en 0.0.0.0:${PORT}"
streamlit run covid_stats_app/app.py --server.port ${PORT} --server.address 0.0.0.0
