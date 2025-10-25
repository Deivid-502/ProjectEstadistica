# ProyectoFinalEstadistica — Análisis estadístico del COVID-19

> Panel interactivo para explorar y analizar datos de COVID-19. Pensado para uso educativo y analítico: claro, directo y fácil de adaptar.

---

## Resumen rápido

Este repositorio contiene una aplicación **Streamlit** para visualizar y analizar series temporales relacionadas con COVID-19: notificaciones (casos y muertes), hospitalizaciones y muertes por edad. La idea es tener un entorno reproducible para calcular métricas básicas, ajustar distribuciones y crear visualizaciones (incluyendo mapas animados).

> Nota importante: durante la última revisión sólo se mantuvo un cambio puntual en `app.py` relativo al selector de rango de fechas en la sección *Resumen* (manejo robusto de `st.date_input`). Todo lo demás del proyecto original se mantiene sin modificaciones.

---

## Características principales

* Interfaz web rápida con Streamlit.
* Cálculos estadísticos robustos: media, mediana, moda, varianza, covarianza, correlación, medias móviles y tasas per cápita.
* Detección y ajuste de distribuciones candidatas (normal, gamma, lognormal, Poisson, NegBin por momentos).
* Visualizaciones con Plotly: series temporales, histogramas, barras y mapas choropleth animados.
* Preprocesado opcional para generar archivos procesados y animaciones HTML para el mapa.

---

## Estructura del proyecto

```
ProyectoFinalEstadistica/
├── covid_stats_app/
│   ├── app.py               # Interfaz Streamlit
│   ├── data_loader.py       # Carga y validación de CSV
│   ├── stats.py             # Funciones estadísticas
│   ├── plots.py             # Gráficos y animaciones
│   └── preprocess.py        # Scripts para preparar datos/animaciones
├── converted_covid_data/
│   └── final/               # CSV finales esperados (ver formato abajo)
└── README.md                # Este fichero
```

---

## Requisitos / Instalación

Se sugiere usar un entorno virtual. Requisitos mínimos:

```bash
python >= 3.9
pip install -r covid_stats_app/requirements.txt
# o manualmente
pip install streamlit pandas numpy plotly scipy pycountry pyarrow
```

> `pycountry` es opcional pero mejora la conversión de códigos de país (ISO2 → ISO3) para el mapa.

---

## Formato de los CSV esperados

Los archivos CSV deben estar en `converted_covid_data/final/` y tener, como mínimo, las columnas siguientes según el archivo:

* `notifications_timeseries.csv`: `date`, `country`, `country_code`, `new_cases`, `new_deaths`, `cum_cases`, `cum_deaths`, ...
* `hospitalizations_timeseries.csv`: `date`, `country`, `country_code`, `new_hospitalizations`, `cum_hospitalizations`, `icu`, ...
* `deaths_by_age_timeseries.csv`: `date`, `age_group`, `deaths`, `country`, ...

**Formatos recomendados:**

* `date` en ISO (`YYYY-MM-DD`) o cualquier formato parseable por `pandas.to_datetime`.
* `country_code` preferiblemente en ISO-3 (ej. `USA`, `ESP`). Si tienes ISO-2 (ej. `US`, `ES`), la app intentará convertirlos si `pycountry` está instalado.

---

## Arrancar la aplicación

Ejecuta desde la raíz del proyecto:

```bash
python -m streamlit run covid_stats_app/app.py
```

La app abrirá en `http://localhost:8501`.

---

## Uso básico

1. Si los CSV están en `converted_covid_data/final/`, la app los cargará automáticamente.
2. Si faltan archivos, usa el uploader integrado en la parte superior de la app para subirlos.
3. Ve a la sección **Resumen** para un panel con KPIs y filtros (país + rango de fechas). *Nota: el selector de fechas ahora maneja correctamente los casos en que el usuario selecciona una sola fecha accidentalmente.*
4. En **Notificaciones** verás la serie temporal y el mapa animado (si existe el preprocesado); si no, la app puede intentar generar los CSV procesados cuando selecciones la métrica.
5. En **Análisis estadístico** puedes calcular medidas y ajustar distribuciones.

---

## Cambio clave aplicado (importante)

Se ha aplicado un **arreglo puntual** en `app.py` para mejorar la experiencia del selector de rango de fechas en la sección *Resumen*:

* Antes: cuando el usuario escogía la fecha de inicio en el calendario, el widget se cerraba y `st.date_input` podía devolver una sola fecha; la app lo interpretaba como falta de `end` y lanzaba un error al aplicar el filtro.
* Ahora: el código normaliza la salida del `date_input` y valida que existan **ambas** fechas antes de aplicar el filtro. Si falta la fecha final, la app muestra un aviso claro pidiendo que seleccione ambas fechas.

Este fue el único cambio que se mantuvo de la última ronda de modificaciones (el resto fue descartado según tu indicación).

---

## Buenas prácticas y recomendaciones

* Haz copia de seguridad de tus archivos antes de sobrescribirlos.
* Si trabajas con muchos países y rangos grandes, considera usar la opción de escala logarítmica para el mapa (si la agregas) para evitar que países con muchos casos saturen la paleta.
* Mantén tus CSV con `date` normalizado; facilita reproducibilidad y evita sorpresas en las agrupaciones.

---
