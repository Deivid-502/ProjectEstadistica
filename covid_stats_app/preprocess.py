# preprocess.py
"""
Genera datos procesados y una animación HTML del mapa choropleth.
Uso:
  python -m covid_stats_app.preprocess --metric new_cases
Genera:
  converted_covid_data/processed/notifications_agg_<metric>.csv
  converted_covid_data/processed/choropleth_notifications_<metric>.html
"""
import argparse
from pathlib import Path
from covid_stats_app import data_loader as dl
from covid_stats_app import plots
import pandas as pd

def preprocess_notifications(metric='new_cases', use_cumulative=True):
    base = dl.get_base_dir()
    p = base / dl.EXPECTED_FILES["notifications"]
    if not p.exists():
        print("No existe CSV de notificaciones en:", p)
        return
    df = dl.load_notifications()
    if metric not in df.columns:
        print(f"La columna {metric} no existe en el CSV. Columnas disponibles: {list(df.columns)}")
        return
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'country_code'])
    df['country_code'] = df['country_code'].astype(str).str.upper()
    df[metric] = pd.to_numeric(df[metric], errors='coerce').fillna(0)
    agg = df.groupby(['date', 'country_code'], as_index=False)[metric].sum().sort_values(['country_code','date'])
    # generar acumulado si se desea (útil para visualización del spread)
    if use_cumulative:
        agg['cum'] = agg.groupby('country_code')[metric].cumsum()
    out_dir = base.parent / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_out = out_dir / f"notifications_agg_{metric}.csv"
    agg.to_csv(csv_out, index=False)
    print("CSV agregado guardado en:", csv_out)

    # Generar figura animada (usamos la columna 'cum' si use_cumulative True)
    try:
        if use_cumulative:
            # renombrar la columna que contiene el valor a 'value' para compatibilidad con plots
            df_for_fig = agg.rename(columns={'cum': 'value'})
        else:
            df_for_fig = agg.rename(columns={metric: 'value'})
        fig = plots.animated_choropleth(df_for_fig, date_col='date', value_col='value', code_col='country_code', title=f"Animación — {metric}")
        html_out = out_dir / f"choropleth_notifications_{metric}.html"
        plots.save_fig_html(fig, html_out)
        print("HTML de animación guardado en:", html_out)
    except Exception as e:
        print("No se pudo generar la figura de animación:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric", default="new_cases", help="Columna métrica a procesar (por defecto new_cases)")
    parser.add_argument("--no-cum", action="store_true", help="No generar acumulado; animar valores diarios en su lugar")
    args = parser.parse_args()
    preprocess_notifications(metric=args.metric, use_cumulative=not args.no_cum)
