# data_loader.py
from pathlib import Path
import pandas as pd
import pycountry

# BASE: carpeta converted_covid_data/final que está en la raíz del proyecto
BASE = Path(__file__).resolve().parent.parent / "converted_covid_data" / "final"

EXPECTED_FILES = {
    "notifications": "notifications_timeseries.csv",
    "hospitalizations": "hospitalizations_timeseries.csv",
    "deaths_by_age": "deaths_by_age_timeseries.csv"
}

def _safe_read(path):
    return pd.read_csv(path, low_memory=False, encoding="utf-8")

def _map_country_to_iso3(series_country):
    def name_to_iso3(name):
        try:
            if pd.isna(name): return None
            c = pycountry.countries.lookup(str(name))
            return c.alpha_3
        except Exception:
            return None
    return series_country.apply(name_to_iso3)

def _try_find(filename):
    p = BASE / filename
    if p.exists():
        return p
    # try a few alternatives relative to project root
    alt = Path(__file__).resolve().parent.parent / filename
    if alt.exists():
        return alt
    return None

def load_notifications():
    filename = EXPECTED_FILES["notifications"]
    p = _try_find(filename)
    if not p:
        raise FileNotFoundError(f"{BASE/filename} not found. Put the CSV in the project's converted_covid_data/final/ folder.")
    df = _safe_read(p)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        df['date'] = pd.NaT
    if 'country_code' not in df.columns or df['country_code'].isna().all():
        if 'country' in df.columns:
            df['country_code'] = _map_country_to_iso3(df['country'])
        else:
            df['country_code'] = None
    for c in ['new_cases','cum_cases','new_deaths','cum_deaths']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64')
        else:
            df[c] = pd.Series([pd.NA]*len(df), dtype='Int64')
    return df

def load_hospitalizations():
    filename = EXPECTED_FILES["hospitalizations"]
    p = _try_find(filename)
    if not p:
        raise FileNotFoundError(f"{BASE/filename} not found. Put the CSV in the project's converted_covid_data/final/ folder.")
    df = _safe_read(p)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        df['date'] = pd.NaT
    for c in ['new_hospitalizations','cum_hospitalizations','icu']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64')
        else:
            df[c] = pd.Series([pd.NA]*len(df), dtype='Int64')
    return df

def load_deaths_by_age():
    filename = EXPECTED_FILES["deaths_by_age"]
    p = _try_find(filename)
    if not p:
        raise FileNotFoundError(f"{BASE/filename} not found. Put the CSV in the project's converted_covid_data/final/ folder.")
    df = _safe_read(p)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        df['date'] = pd.NaT
    if 'deaths' in df.columns:
        df['deaths'] = pd.to_numeric(df['deaths'], errors='coerce').astype('Int64')
    return df
