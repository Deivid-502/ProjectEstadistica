#!/usr/bin/env sh
set -e

PORT=${PORT:-8501}
echo "Iniciando Streamlit en 0.0.0.0:${PORT}"
streamlit run covid_stats_app/app.py --server.port ${PORT} --server.address 0.0.0.0
