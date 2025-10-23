#!/usr/bin/env sh
set -e

export PYTHONPATH=$(pwd):$PYTHONPATH

PORT=${PORT:-8080}
echo "Iniciando Streamlit en 0.0.0.0:${PORT}"
streamlit run covid_stats_app/app.py --server.port=${PORT} --server.address=0.0.0.0
