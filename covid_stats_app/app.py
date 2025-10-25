import os
import sys
from pathlib import Path
import logging
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime, timedelta, date

# asegurar repo root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covid_stats_app import data_loader as dl
from covid_stats_app import plots, stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("covid_app")

st.set_page_config(layout="wide", page_title="Panel COVID — Visualizaciones y Análisis")

# mapas amigables
NOTIF_METRICS = {
    "Nuevos casos": "new_cases",
    "Casos acumulados": "cum_cases",
    "Nuevas muertes": "new_deaths",
    "Muertes acumuladas": "cum_deaths",
}

HOSP_METRICS = {
    "Nuevas hospitalizaciones": "new_hospitalizations",
    "Hospitalizaciones acumuladas": "cum_hospitalizations",
    "UCI (estimado)": "icu",
}

DEATHS_METRICS = {
    "Muertes (conteo)": "deaths",
}

DATASET_MAP = {"Notificaciones": "notifications", "Hospitalizaciones": "hospitalizations", "Muertes por edad": "deaths_by_age"}
GENERIC_FOOTER = "Panel interactivo para exploración y análisis de series COVID — diseñado para uso exploratorio."

# cache invalidable por mtime de archivos
def _files_state():
    base = dl.get_base_dir()
    state = []
    for fname in dl.EXPECTED_FILES.values():
        p = base / fname
        try:
            m = p.stat().st_mtime if p.exists() else None
        except Exception:
            m = None
        state.append((str(p), m))
    return tuple(state)

@st.cache_data(ttl=3600, show_spinner=False)
def load_data_cached(state_key):
    notif = hosp = deaths = pd.DataFrame()
    errors = []
    try:
        notif = dl.load_notifications()
    except Exception as e:
        errors.append(f"Notificaciones: {e}")
    try:
        hosp = dl.load_hospitalizations()
    except Exception as e:
        errors.append(f"Hospitalizaciones: {e}")
    try:
        deaths = dl.load_deaths_by_age()
    except Exception as e:
        errors.append(f"Muertes por edad: {e}")
    return notif, hosp, deaths, errors

file_state = _files_state()
notif, hosp, deaths, load_errors = load_data_cached(file_state)

# uploader simple (si faltan CSV)
def uploader_panel():
    st.info("Si falta alguno de los CSV finales, súbelos aquí (se guardarán en converted_covid_data/final).")
    with st.form("uploader_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            up1 = st.file_uploader("notifications_timeseries.csv", type="csv", key="u1")
        with c2:
            up2 = st.file_uploader("hospitalizations_timeseries.csv", type="csv", key="u2")
        with c3:
            up3 = st.file_uploader("deaths_by_age_timeseries.csv", type="csv", key="u3")
        submit = st.form_submit_button("Guardar archivos")
        if submit:
            saved = []
            base = dl.get_base_dir()
            base.mkdir(parents=True, exist_ok=True)
            for up, name in [(up1, dl.EXPECTED_FILES["notifications"]), (up2, dl.EXPECTED_FILES["hospitalizations"]), (up3, dl.EXPECTED_FILES["deaths_by_age"])]:
                if up is not None:
                    dest = base / name
                    with open(dest, "wb") as f:
                        f.write(up.getbuffer())
                    saved.append(str(dest))
            if saved:
                st.success("Archivos guardados: " + ", ".join(saved))
                st.experimental_rerun()

if notif.empty or hosp.empty or deaths.empty:
    uploader_panel()

# sidebar
section = st.sidebar.selectbox("Sección", ["Resumen", "Notificaciones", "Hospitalizaciones", "Muertes por edad", "Análisis estadístico", "Exportar y ajustes"])

if notif.empty and hosp.empty and deaths.empty:
    st.warning("Aún no hay datos cargados. Sube los CSV en la sección superior para comenzar.")
    st.stop()

# ---------- RESUMEN (con filtro por país y rango de fechas) ----------
if section == "Resumen":
    st.title("Impacto de COVID-19 — Resumen")
    st.markdown("""
**Resumen ejecutivo**
Explora la evolución de COVID-19 (2020–2025) con indicadores y visualizaciones.
    """)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros — notificaciones", f"{len(notif):,}")
    c2.metric("Registros — hospitalizaciones", f"{len(hosp):,}")
    c3.metric("Registros — muertes por edad", f"{len(deaths):,}")

    st.markdown("### Filtrado por país y rango de fechas")
    countries = sorted(notif['country'].dropna().unique()) if 'country' in notif.columns else []
    col1, col2 = st.columns([2,1])
    with col1:
        sel_country = st.selectbox("Seleccionar país", ["-- Todos --"] + countries)
        # rango de fechas (default: últimos 30 días si hay fechas)
        if 'date' in notif.columns and not notif['date'].dropna().empty:
            min_date = notif['date'].min().date()
            max_date = notif['date'].max().date()
            default_end = max_date
            default_start = max_date - timedelta(days=30) if (max_date - min_date).days >= 30 else min_date
            # Uso seguro de st.date_input: el widget puede devolver una fecha o una tupla.
            date_range = st.date_input("Rango de fechas", value=(default_start, default_end), min_value=min_date, max_value=max_date)
            # Normalizar salida del widget para obtener start_date y end_date de forma segura
            if isinstance(date_range, (list, tuple)):
                try:
                    start_date = date_range[0]
                    end_date = date_range[1]
                except Exception:
                    start_date = date_range
                    end_date = None
            else:
                # Si el usuario selecciona solo una fecha (p.ej. el selector se cerró antes),
                # la guardamos como fecha de inicio y pedimos que seleccione la fecha final.
                start_date = date_range
                end_date = None
        else:
            start_date, end_date = None, None

    with col2:
        if st.button("Aplicar filtro"):
            # Validaciones para evitar que la app intente filtrar con fecha fin ausente o mal orden
            if start_date is None:
                st.warning("Seleccione una fecha de inicio antes de aplicar el filtro.")
            elif end_date is None:
                st.warning("Seleccione también la fecha de fin para aplicar el filtro (usa el calendario y elige ambos días).")
            elif start_date > end_date:
                st.warning("La fecha de inicio no puede ser posterior a la fecha de fin.")
            else:
                st.session_state['summary_filter'] = {'country': sel_country if sel_country != "-- Todos --" else None, 'start': start_date, 'end': end_date}
    # Mostrar KPI del filtro si aplicado (o instrucción)
    if 'summary_filter' in st.session_state:
        f = st.session_state['summary_filter']
        st.markdown("**Resultados del filtro:**")
        df = notif.copy()
        if f['country']:
            df = df[df['country'] == f['country']]
        if f['start'] and f['end']:
            df = df[(pd.to_datetime(df['date']).dt.date >= f['start']) & (pd.to_datetime(df['date']).dt.date <= f['end'])]
        if df.empty:
            st.info("No hay datos para el filtro aplicado.")
        else:
            last7_mean = stats.safe_mean(df.sort_values('date').tail(7)['new_cases']) if 'new_cases' in df.columns else None
            st.write(f"Periodos: {f['start']} — {f['end']}")
            st.metric("Media (últimos 7 días)", f"{last7_mean:,.1f}" if last7_mean is not None else "N/A")
            # Mostrar mini serie
            fig = plots.timeseries_plot(df, date_col='date', y='new_cases', entity_col=None, countries=None, y_label="Nuevos casos", title="Serie (filtro aplicado)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Seleccione país y rango y pulse 'Aplicar filtro' para ver indicadores por periodo.")
    st.markdown("---")
    st.write(GENERIC_FOOTER)

# ---------- NOTIFICACIONES ----------
elif section == "Notificaciones":
    st.title("Notificaciones — casos y muertes")
    countries = sorted(notif['country'].dropna().unique()) if 'country' in notif.columns else []
    sel_countries = st.multiselect("Selecciona países (vacío = todos)", countries, default=(countries[:3] if len(countries) > 0 else []))
    metric_label = st.selectbox("Métrica", list(NOTIF_METRICS.keys()))
    metric_col = NOTIF_METRICS[metric_label]

    st.subheader("Serie temporal")
    try:
        fig_ts = plots.timeseries_plot(notif, date_col='date', y=metric_col, entity_col='country', countries=sel_countries if sel_countries else None, y_label=metric_label, title=f"{metric_label} — Serie temporal")
        st.plotly_chart(fig_ts, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la serie temporal: {e}")

    st.subheader("Mapa animado")
    st.write("Abajo se muestra la animación por fecha. Si está en blanco, ejecuta el preprocesador para generar el HTML o verifica country_code.")

    processed_dir = dl.get_base_dir().parent / "processed"
    html_path = processed_dir / f"choropleth_notifications_{NOTIF_METRICS[metric_label]}.html"
    csv_agg_path = processed_dir / f"notifications_agg_{NOTIF_METRICS[metric_label]}.csv"

    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        components.html(html, height=700, scrolling=True)
    else:
        try:
            agg = dl.aggregate_for_choropleth(notif, date_col='date', value_col=metric_col, code_col='country_code')
            if agg is None or agg.empty:
                st.warning("No hay datos válidos para el mapa animado (country_code o fechas faltantes). Ejecuta el preprocesador para generar la animación HTML.")
            else:
                # crear acumulado por país para mostrar evolución
                tmp = agg.copy()
                tmp['date'] = pd.to_datetime(tmp['date'])
                tmp = tmp.sort_values(['country_code','date'])
                tmp['cum'] = tmp.groupby('country_code')[metric_col].cumsum()
                tmp2 = tmp.rename(columns={metric_col:'value'})
                fig_map = plots.animated_choropleth(tmp2, date_col='date', value_col='cum', code_col='country_code', title=f"{metric_label} — Animación acumulada")
                st.plotly_chart(fig_map, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo generar el mapa animado: {e}")

# ---------- HOSPITALIZACIONES ----------
elif section == "Hospitalizaciones":
    st.title("Hospitalizaciones")
    countries = sorted(hosp['country'].dropna().unique()) if 'country' in hosp.columns else []
    sel = st.selectbox("País", countries)
    metric_label = st.selectbox("Métrica", list(HOSP_METRICS.keys()))
    metric_col = HOSP_METRICS[metric_label]
    try:
        fig = plots.timeseries_plot(hosp, date_col='date', y=metric_col, entity_col='country', countries=[sel] if sel else None, y_label=metric_label, title=f"{metric_label} — {sel}")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo generar la gráfica: {e}")

# ---------- MUERTES POR EDAD ----------
elif section == "Muertes por edad":
    st.title("Muertes por edad")
    view = st.selectbox("Vista", ["Totales por grupo etario", "Serie temporal por grupo etario"])
    age_groups = []
    if 'age_group' in deaths.columns:
        def _age_sort_key(g):
            try:
                s = str(g).strip()
                if '+' in s:
                    return (1000, int(s.replace('+','').split('+')[0]))
                if '-' in s:
                    a = int(s.split('-')[0])
                    return (a, 0)
                return (10**6, 0)
            except Exception:
                return (10**6, 0)
        age_groups = sorted(deaths['age_group'].dropna().unique(), key=_age_sort_key)

    if view == "Totales por grupo etario":
        if not age_groups:
            st.warning("No se encontraron grupos etarios en el dataset.")
        else:
            df_tot = deaths.groupby('age_group', as_index=False)['deaths'].sum()
            df_tot['order'] = df_tot['age_group'].apply(lambda x: age_groups.index(x) if x in age_groups else 10**6)
            df_tot = df_tot.sort_values('order')
            fig = plots.bar_plot(df_tot, x='age_group', y='deaths', x_label="Grupo etario", y_label="Total de muertes", title="Muertes acumuladas por grupo etario")
            st.plotly_chart(fig, use_container_width=True)
    else:
        sel_age = st.selectbox("Seleccionar grupo etario", age_groups)
        if sel_age:
            df_sel = deaths[deaths['age_group'] == sel_age].copy()
            if df_sel.empty:
                st.info("No hay datos para el grupo seleccionado.")
            else:
                df_sel['month'] = pd.to_datetime(df_sel['date'], errors='coerce').dt.to_period('M').dt.to_timestamp()
                monthly = df_sel.groupby('month', as_index=False)['deaths'].sum()
                fig = plots.timeseries_plot(monthly, date_col='month', y='deaths', entity_col=None, countries=None, y_label="Muertes", title=f"Muertes por mes — {sel_age}")
                st.plotly_chart(fig, use_container_width=True)

# ---------- ANALISIS ESTADISTICO ----------
elif section == "Análisis estadístico":
    st.title("Análisis estadístico")
    ds_label = st.selectbox("Dataset para análisis", list(DATASET_MAP.keys()))
    ds_key = DATASET_MAP[ds_label]
    if ds_key == "notifications":
        df = notif
        metrics_map = NOTIF_METRICS
    elif ds_key == "hospitalizations":
        df = hosp
        metrics_map = HOSP_METRICS
    else:
        df = deaths
        metrics_map = DEATHS_METRICS

    numeric_options = [k for k, v in metrics_map.items() if v in df.columns]
    if not numeric_options:
        st.warning("No se encontraron columnas numéricas esperadas en el dataset seleccionado.")
    else:
        col_label = st.selectbox("Columna numérica", numeric_options)
        col_key = metrics_map[col_label]
        cont = st.checkbox("Tratar como continua (normal/gamma)", value=True)
        other_options = [lab for lab in numeric_options if lab != col_label]
        other_label = st.selectbox("Covarianza con (otra columna)", other_options + ["-- ninguna --"])

        if st.button("Calcular estadísticas"):
            mean_v = stats.safe_mean(df[col_key])
            median_v = stats.safe_median(df[col_key])
            mode_v = stats.safe_mode(df[col_key])
            var_v = stats.safe_variance(df[col_key])
            cov_v = None
            if other_label and other_label != "-- ninguna --":
                other_key = metrics_map[other_label]
                cov_v = stats.safe_covariance(df[col_key], df[other_key])
            fits = stats.fit_distributions(df[col_key], continuous=cont)
            st.session_state['last_stats'] = {
                'mean': mean_v, 'median': median_v, 'mode': mode_v, 'var': var_v, 'cov': cov_v, 'fits': fits,
                'col_label': col_label, 'other_label': other_label if other_label else None, 'cont': cont
            }

        if 'last_stats' in st.session_state:
            res = st.session_state['last_stats']
            st.subheader(f"Resultados — {res.get('col_label')}")
            a, b, c, d = st.columns(4)
            a.metric("Media", f"{res['mean']:,.2f}" if res['mean'] is not None else "N/A")
            b.metric("Mediana", f"{res['median']:,.2f}" if res['median'] is not None else "N/A")
            if res['mode'] is not None:
                # compatible: safe_mode returns número; safe_mode_with_count devuelve dict
                if isinstance(res['mode'], dict):
                    c.metric("Moda", f"{res['mode']['mode']} ({res['mode']['count']})")
                else:
                    c.metric("Moda", f"{res['mode']}")
            else:
                c.metric("Moda", "N/A")
            d.metric("Varianza", f"{res['var']:,.2f}" if res['var'] is not None else "N/A")
            if res.get('cov') is not None:
                st.write("Covarianza:", f"{res['cov']:,.2f}")
            else:
                if res.get('other_label'):
                    st.write("Covarianza: N/A (datos insuficientes)")
            if 'acum' in col_key or 'cum' in col_key or 'acumul' in col_label.lower():
                st.warning("Atención: la columna seleccionada parece ser acumulada. Use columnas de flujo para análisis por periodo.")
            fits = res.get('fits', [])
            if not fits:
                st.info("No se detectaron ajustes o la muestra es pequeña.")
            else:
                st.subheader("Ajustes detectados")
                rows = []
                for f in fits:
                    dist = f.get('dist', '')
                    params = f.get('params', {})
                    ksp = f.get('kstest_pvalue', None)
                    rows.append({
                        "Distribución": dist,
                        "Parámetros": ", ".join([f"{kk}={vv:.4g}" for kk, vv in params.items()]) if params else "",
                        "K-S p-value": f"{(ksp):.4g}" if ksp is not None else ""
                    })
                st.table(pd.DataFrame(rows))

# ---------- EXPORTAR ----------
elif section == "Exportar y ajustes":
    st.title("Exportar y ajustes")
    st.write("Opciones para convertir o descargar los archivos finales.")
    if st.button("Crear archivos Parquet (si hay CSV)"):
        created = []
        for name in dl.EXPECTED_FILES.values():
            p = dl.get_base_dir() / name
            if p.exists():
                dfp = pd.read_csv(p)
                out = p.with_suffix('.parquet')
                dfp.to_parquet(out, engine='pyarrow', index=False)
                created.append(str(out))
        if created:
            st.success("Parquet creados: " + ", ".join(created))
        else:
            st.info("No se encontraron CSV para convertir.")
    if st.button("Descargar CSV finales (zip)"):
        import shutil, tempfile
        tmp = tempfile.mkdtemp()
        copied = []
        for name in dl.EXPECTED_FILES.values():
            p = dl.get_base_dir() / name
            if p.exists():
                shutil.copy(str(p), tmp)
                copied.append(name)
        if not copied:
            st.info("No hay CSV para incluir en el ZIP.")
        else:
            zip_base = "/tmp/covid_final_csvs"
            shutil.make_archive(zip_base, 'zip', tmp)
            zip_path = zip_base + ".zip"
            with open(zip_path, 'rb') as f:
                st.download_button("Descargar ZIP", f, file_name="covid_final_csvs.zip")

if section != "Resumen":
    st.markdown("---")
    st.write(GENERIC_FOOTER)
