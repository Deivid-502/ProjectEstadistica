# data_loader.py
from pathlib import Path
import os
import pandas as pd
import logging

logger = logging.getLogger("data_loader")
try:
    import pycountry
except Exception:
    pycountry = None
    logger.warning("pycountry no disponible. El mapeo de países a ISO3 no funcionará sin esta librería.")

DEFAULT_BASE = Path(__file__).resolve().parent.parent / "converted_covid_data" / "final"
BASE = Path(os.getenv("COVID_DATA_DIR", DEFAULT_BASE))

EXPECTED_FILES = {
    "notifications": "notifications_timeseries.csv",
    "hospitalizations": "hospitalizations_timeseries.csv",
    "deaths_by_age": "deaths_by_age_timeseries.csv"
}

MANUAL_COUNTRY_ALIASES = {
    "estados unidos": "United States",
    "eeuu": "United States",
    "méxico": "Mexico",
    "brasil": "Brazil",
    "reino unido": "United Kingdom",
    "corea del sur": "Korea, Republic of",
    "corea del norte": "Korea, Democratic People's Republic of",
    "españa": "Spain",
    "argentina": "Argentina",
    "chile": "Chile",
    "colombia": "Colombia",
}

def get_base_dir():
    return BASE

def _safe_read(path):
    return pd.read_csv(path, low_memory=False, encoding="utf-8")

def _normalize_country_name(name):
    if pd.isna(name):
        return None
    s = str(name).strip()
    key = s.lower()
    if key in MANUAL_COUNTRY_ALIASES:
        return MANUAL_COUNTRY_ALIASES[key]
    return s

def _name_to_iso3(name):
    if name is None:
        return None
    if pycountry is None:
        return None
    try:
        if len(name) == 3 and name.isalpha() and name.upper() == name:
            c = pycountry.countries.get(alpha_3=name)
            if c:
                return c.alpha_3
        c = pycountry.countries.lookup(str(name))
        return c.alpha_3
    except Exception:
        try:
            for c in pycountry.countries:
                if str(c.name).lower() == str(name).lower():
                    return c.alpha_3
        except Exception:
            pass
    return None

def _map_country_to_iso3(series_country):
    return series_country.apply(lambda n: _name_to_iso3(_normalize_country_name(n)))

def _try_find(filename):
    p = BASE / filename
    if p.exists():
        return p
    alt = Path(__file__).resolve().parent.parent / filename
    if alt.exists():
        return alt
    return None

def load_notifications():
    filename = EXPECTED_FILES["notifications"]
    p = _try_find(filename)
    if not p:
        raise FileNotFoundError(f"{BASE/filename} no encontrado. Coloca el CSV en {BASE}")
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

    # Normalizar country_code a mayúsculas (ISO3)
    if 'country_code' in df.columns:
        df['country_code'] = df['country_code'].astype(str).str.upper().replace({'NONE':'', 'NAN':''})
        df.loc[df['country_code'].str.strip() == '', 'country_code'] = pd.NA

    for c in ['new_cases', 'cum_cases', 'new_deaths', 'cum_deaths']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64')
        else:
            df[c] = pd.Series([pd.NA]*len(df), dtype='Int64')
    return df

def load_hospitalizations():
    filename = EXPECTED_FILES["hospitalizations"]
    p = _try_find(filename)
    if not p:
        raise FileNotFoundError(f"{BASE/filename} no encontrado. Coloca el CSV en {BASE}")
    df = _safe_read(p)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        df['date'] = pd.NaT
    for c in ['new_hospitalizations', 'cum_hospitalizations', 'icu']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64')
        else:
            df[c] = pd.Series([pd.NA]*len(df), dtype='Int64')
    return df

def load_deaths_by_age():
    filename = EXPECTED_FILES["deaths_by_age"]
    p = _try_find(filename)
    if not p:
        raise FileNotFoundError(f"{BASE/filename} no encontrado. Coloca el CSV en {BASE}")
    df = _safe_read(p)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        df['date'] = pd.NaT
    if 'deaths' in df.columns:
        df['deaths'] = pd.to_numeric(df['deaths'], errors='coerce').astype('Int64')
    return df

def aggregate_for_choropleth(df, date_col='date', value_col='new_cases', code_col='country_code'):
    if df is None or df.empty:
        return pd.DataFrame()
    if date_col not in df.columns or code_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors='coerce')
    tmp[value_col] = pd.to_numeric(tmp[value_col], errors='coerce').fillna(0)
    tmp[code_col] = tmp[code_col].astype(str).str.upper()
    tmp = tmp.dropna(subset=[date_col, code_col])
    if tmp.empty:
        return pd.DataFrame()
    agg = tmp.groupby([date_col, code_col], as_index=False)[value_col].sum()
    return agg
