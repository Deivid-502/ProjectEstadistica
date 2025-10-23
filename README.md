
---

# 📘 ProyectoFinalEstadistica — Análisis Estadístico del COVID-19

## 🧠 Contexto general

**Nombre del proyecto:** `ProyectoFinalEstadistica`
**Tema:** Análisis estadístico del COVID-19
**Lenguaje principal:** Python
**Framework de interfaz:** Streamlit
**Propósito:** Facilitar el estudio, análisis y visualización de datos sobre el impacto del COVID-19 a través de métricas estadísticas y gráficas interactivas.

---

## 🎯 Objetivo

Este proyecto busca analizar información real del COVID-19 desde un enfoque estadístico, permitiendo al usuario explorar, comparar y comprender los datos de manera dinámica.

El sistema permite:

* Calcular medidas estadísticas básicas (media, mediana, moda, varianza, covarianza).
* Explorar distribuciones continuas y discretas.
* Visualizar datos mediante gráficos animados e interactivos.
* Organizar la información por categorías (casos, hospitalizaciones, muertes).
* Presentar todo dentro de una interfaz moderna, clara y navegable.

---

## 🧩 Estructura del proyecto

```
ProyectoFinalEstadistica/
│
├── covid_stats_app/                 ← Código fuente principal
│   ├── app.py                       ← Interfaz gráfica (Streamlit)
│   ├── data_loader.py               ← Carga y validación de archivos CSV
│   ├── stats.py                     ← Cálculos estadísticos
│   ├── plots.py                     ← Generación de gráficos
│   └── requirements.txt             ← Dependencias del proyecto
│
├── converted_covid_data/
│   └── final/                       ← Archivos CSV finales procesados
│       ├── deaths_by_age_timeseries.csv
│       ├── hospitalizations_timeseries.csv
│       └── notifications_timeseries.csv
│
└── README.md                        ← Instrucciones generales
```

---

## ⚙️ Funcionamiento del sistema

### 1. Inicio

El usuario ejecuta:

```bash
python -m streamlit run covid_stats_app/app.py
```

Esto inicia la aplicación web local ([http://localhost:8501](http://localhost:8501)).

### 2. Carga de datos

El módulo `data_loader.py` busca los CSV en la carpeta `converted_covid_data/final/`.
Si no los encuentra, la app permite **subir los archivos manualmente** mediante un uploader integrado.

### 3. Interfaz principal

El archivo `app.py` presenta un menú con tres secciones:

* 🧾 **Notificación de nuevos casos y muertes**
* 🏥 **Hospitalizaciones semanales**
* ⚰️ **Muertes mensuales por edad**

Cada sección permite:

* Ver los datos de forma tabular.
* Calcular estadísticas específicas.
* Visualizar resultados mediante gráficos animados.
* Generar comparaciones y resúmenes globales.

### 4. Procesamiento estadístico

El módulo `stats.py` se encarga de los cálculos principales:

* **Medidas de tendencia central:** media, mediana, moda.
* **Medidas de dispersión:** varianza, desviación estándar, covarianza.
* **Análisis de distribución:** continua y discreta (usando `scipy.stats`).

### 5. Visualización

El módulo `plots.py` genera gráficos con **Plotly** y **Matplotlib**, entre ellos:

* Gráficos de barras, líneas, y dispersión.
* Histogramas interactivos.
* Animaciones que muestran la evolución de los datos en el tiempo.

---

## 🧩 Modularidad y roles

| Módulo           | Función                                  | Entrada              | Salida                   |
| ---------------- | ---------------------------------------- | -------------------- | ------------------------ |
| `data_loader.py` | Carga, validación y preparación de datos | Archivos CSV         | DataFrames limpios       |
| `stats.py`       | Cálculo de estadísticas                  | DataFrame            | Diccionario de métricas  |
| `plots.py`       | Creación de gráficos y animaciones       | DataFrame / métricas | Objetos visuales         |
| `app.py`         | Control de interfaz y flujo principal    | Datos + módulos      | Interfaz web interactiva |

---

## 🧮 Estadísticas disponibles

El sistema puede calcular y mostrar:

* **Media**: promedio de los valores.
* **Mediana**: valor central.
* **Moda**: valor más frecuente.
* **Varianza**: dispersión de los datos respecto a la media.
* **Covarianza**: relación entre dos variables.
* **Distribución continua/discreta**: análisis probabilístico según tipo de dato.

---

## 📊 Tipos de gráficos

* Gráficos de líneas (evolución temporal).
* Gráficos de barras (comparativos).
* Histogramas (distribuciones).
* Diagramas de dispersión (relaciones entre variables).
* Gráficos animados (para series de tiempo).

Todos pueden personalizarse mediante filtros, selección de columnas y parámetros desde la interfaz.

---

## 🧰 Dependencias principales

Archivo: `requirements.txt`

```
streamlit
pandas
numpy
matplotlib
plotly
scipy
```

---

## 🧭 Flujo lógico general

```
Datos CSV → Carga (data_loader.py)
          → Procesamiento (stats.py)
          → Visualización (plots.py)
          → Interfaz (app.py)
```

---

## 🧱 Diseño modular y mantenimiento

El proyecto está diseñado para ser **expandible** y **fácil de mantener**:

* Puedes añadir nuevos conjuntos de datos (más CSVs).
* Se pueden incorporar nuevos cálculos estadísticos en `stats.py`.
* Puedes crear nuevos gráficos personalizados en `plots.py`.
* La interfaz `app.py` permite añadir nuevas secciones o resúmenes fácilmente.

Cada módulo es independiente y comunica sus resultados mediante `pandas.DataFrame` o estructuras JSON simples.

---

## 🚀 Posibles mejoras futuras

* Conexión directa a APIs de datos abiertos (OMS, Our World in Data, etc.).
* Modelos predictivos o proyecciones (regresión lineal o machine learning).
* Exportación automática de resultados (PDF, Excel, PNG).
* Panel de control con filtros avanzados.
* Análisis comparativo entre países o regiones.

---

## 🧩 Cómo modificar o ampliar el proyecto

1. **Agregar una nueva fuente de datos:**

   * Coloca el nuevo CSV en `converted_covid_data/final/`.
   * Crea una nueva función en `data_loader.py` para cargarlo.
   * Añade un nuevo submenú en `app.py` para visualizarlo.

2. **Agregar nuevas estadísticas:**

   * Implementa la función en `stats.py`.
   * Llama a esa función desde el menú correspondiente en `app.py`.

3. **Crear un nuevo gráfico:**

   * Diseña el gráfico en `plots.py` (usa Plotly o Matplotlib).
   * Conéctalo con los datos desde `app.py`.

---

## 📚 Resumen conceptual

El **ProyectoFinalEstadistica** no es solo una herramienta técnica, sino también **una plataforma educativa y analítica**.
Permite estudiar cómo se comportaron las variables del COVID-19 a través del tiempo, cómo se distribuyen los casos, y qué tendencias pueden observarse en diferentes regiones o grupos etarios.

El diseño busca equilibrio entre:

* **Rigor estadístico.**
* **Claridad visual.**
* **Facilidad de uso.**

---

