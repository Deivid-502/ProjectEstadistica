import streamlit as st
from covid_stats_app import data_loader as dl
from covid_stats_app import plots, stats
import pandas as pd
from pathlib import Path

st.set_page_config(layout='wide', page_title='COVID Stats App')
st.title("COVID Statistics App")

@st.cache_data(ttl=3600)
def load_data_all():
    notif = hosp = deaths = pd.DataFrame()
    errors = []
    try:
        notif = dl.load_notifications()
    except Exception as e:
        errors.append(str(e))
    try:
        hosp = dl.load_hospitalizations()
    except Exception as e:
        errors.append(str(e))
    try:
        deaths = dl.load_deaths_by_age()
    except Exception as e:
        errors.append(str(e))
    return notif, hosp, deaths, errors

notif, hosp, deaths, load_errors = load_data_all()

# (el resto del código sigue igual)

if load_errors:
    st.error("No se pudieron cargar algunos datasets. A continuación puedes subir los CSV (se guardarán en converted_covid_data/final)")
    col1, col2, col3 = st.columns(3)
    with col1:
        up1 = st.file_uploader("notifications_timeseries.csv", type="csv")
    with col2:
        up2 = st.file_uploader("hospitalizations_timeseries.csv", type="csv")
    with col3:
        up3 = st.file_uploader("deaths_by_age_timeseries.csv", type="csv")
    if st.button("Guardar archivos subidos"):
        saved = []
        for up, name in [(up1,"notifications_timeseries.csv"), (up2,"hospitalizations_timeseries.csv"), (up3,"deaths_by_age_timeseries.csv")]:
            if up is not None:
                outdir = Path(__file__).resolve().parent.parent / "converted_covid_data" / "final"
                outdir.mkdir(parents=True, exist_ok=True)
                dest = outdir / name
                with open(dest, "wb") as f:
                    f.write(up.getbuffer())
                saved.append(str(dest))
        if saved:
            st.success("Archivos guardados en proyecto: " + ", ".join(saved))
            st.experimental_rerun()

menu = st.sidebar.selectbox("Menú", ["Resumen general", "Notificaciones", "Hospitalizaciones", "Muertes por edad", "Análisis estadístico", "Exportar / Ajustes"])

# Si no hay datos cargados, mostrar mensaje amigable
if notif.empty and hosp.empty and deaths.empty:
    st.info("Aún no hay datos cargados. Sube los CSV en la sección superior para comenzar.")
    st.stop()

# resto de la app (similar a la versión previa)
if menu == "Resumen general":
    st.header("Resumen general (KPIs)")
    cols = st.columns(4)
    with cols[0]:
        st.metric("Registros (notificaciones)", len(notif))
    with cols[1]:
        st.metric("Registros (hospitalizaciones)", len(hosp))
    with cols[2]:
        st.metric("Registros (muertes por edad)", len(deaths))
    with cols[3]:
        st.write("Filtrado:")
        country = st.selectbox("Seleccionar país (notificaciones)", sorted(notif['country'].dropna().unique()) if 'country' in notif.columns else [])
        if country:
            st.write("Últimos 7 días - nuevos casos (media):", stats.safe_mean(notif[notif['country']==country]['new_cases'].tail(7)))

elif menu == "Notificaciones":
    st.header("Notificaciones: casos y muertes")
    countries = sorted(notif['country'].dropna().unique()) if 'country' in notif.columns else []
    sel_countries = st.multiselect("Selecciona países (vacío = todos)", countries, default=(countries[:3] if len(countries)>0 else []))
    metric = st.selectbox("Métrica", ['new_cases','cum_cases','new_deaths','cum_deaths'])
    if st.button("Mostrar serie temporal"):
        fig = plots.timeseries_plot(notif, date_col='date', y=metric, entity_col='country', countries=sel_countries if sel_countries else None)
        st.plotly_chart(fig, use_container_width=True)
    if st.button("Mostrar mapa animado (global)"):
        try:
            fig = plots.animated_choropleth(notif, date_col='date', value_col=metric, code_col='country_code')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo generar el mapa: {e}")

elif menu == "Hospitalizaciones":
    st.header("Hospitalizaciones semanales")
    countries = sorted(hosp['country'].dropna().unique()) if 'country' in hosp.columns else []
    sel = st.selectbox("País", countries)
    metric = st.selectbox("Métrica", ['new_hospitalizations','cum_hospitalizations','icu'])
    if st.button("Mostrar serie hospitalizaciones"):
        fig = plots.timeseries_plot(hosp, date_col='date', y=metric, entity_col='country', countries=[sel] if sel else None)
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Muertes por edad":
    st.header("Muertes mensuales por edad")
    age_groups = sorted(deaths['age_group'].dropna().unique()) if 'age_group' in deaths.columns else []
    sel_age = st.selectbox("Grupo etario", age_groups)
    if st.button("Mostrar histograma de muertes (grupo seleccionado)"):
        if 'deaths' in deaths.columns:
            fig = plots.histogram_plot(deaths[deaths['age_group']==sel_age], 'deaths')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No se encontró columna 'deaths' en el dataset.")

elif menu == "Análisis estadístico":
    st.header("Análisis estadístico")
    dataset = st.selectbox("Dataset para análisis", ["Notificaciones","Hospitalizaciones","Muertes por edad"])
    if dataset == "Notificaciones":
        df = notif
        numeric_cols = ['new_cases','new_deaths','cum_cases','cum_deaths']
    elif dataset == "Hospitalizaciones":
        df = hosp
        numeric_cols = ['new_hospitalizations','cum_hospitalizations','icu']
    else:
        df = deaths
        numeric_cols = ['deaths']

    col = st.selectbox("Columna numérica", [c for c in numeric_cols if c in df.columns])
    if st.button("Calcular estadísticas"):
        st.write("Media:", stats.safe_mean(df[col]))
        st.write("Mediana:", stats.safe_median(df[col]))
        st.write("Moda:", stats.safe_mode(df[col]))
        st.write("Varianza:", stats.safe_variance(df[col]))
        other = st.selectbox("Covarianza con (otra columna)", [c for c in numeric_cols if c in df.columns and c!=col] + ["-- ninguna --"])
        if other and other != "-- ninguna --":
            st.write("Covarianza:", stats.safe_covariance(df[col], df[other]))
        cont = st.checkbox("Tratar como continua (normal/gamma)", value=False)
        fits = stats.fit_distributions(df[col], continuous=cont)
        st.write("Ajustes detectados:", fits)

elif menu == "Exportar / Ajustes":
    st.header("Exportar y ajustes")
    st.write("Puedes descargar los datasets finales o crear versiones Parquet para rendimiento.")
    if st.button("Crear Parquet de los finales"):
        for name in ["notifications_timeseries.csv","hospitalizations_timeseries.csv","deaths_by_age_timeseries.csv"]:
            path = Path(__file__).resolve().parent.parent / "converted_covid_data" / "final" / name
            if path.exists():
                df = pd.read_csv(path)
                out = path.with_suffix('.parquet')
                df.to_parquet(out, engine='pyarrow', index=False)
        st.success("Parquet creados (si existían los CSV).")
    if st.button("Descargar CSV finales (zip)"):
        import shutil, tempfile, os
        tmp = tempfile.mkdtemp()
        for name in ["notifications_timeseries.csv","hospitalizations_timeseries.csv","deaths_by_age_timeseries.csv"]:
            p = Path(__file__).resolve().parent.parent / "converted_covid_data" / "final" / name
            if p.exists():
                shutil.copy(str(p), tmp)
        zip_path = "/tmp/covid_final_csvs.zip"
        shutil.make_archive(zip_path.replace('.zip',''), 'zip', tmp)
        with open(zip_path, 'rb') as f:
            st.download_button("Descargar ZIP", f, file_name="covid_final_csvs.zip")
