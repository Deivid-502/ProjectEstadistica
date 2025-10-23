import numpy as np
import pandas as pd
from scipy import stats
from collections import Counter

def safe_mean(series):
    s = pd.to_numeric(series, errors='coerce').dropna()
    return float(s.mean()) if len(s) > 0 else None

def safe_median(series):
    s = pd.to_numeric(series, errors='coerce').dropna()
    return float(s.median()) if len(s) > 0 else None

def safe_mode(series):
    s = series.dropna().astype(str)
    if len(s) == 0:
        return None
    counts = Counter(s)
    mode, freq = counts.most_common(1)[0]
    return {'mode': mode, 'count': int(freq)}

def safe_variance(series, ddof=0):
    s = pd.to_numeric(series, errors='coerce').dropna()
    return float(s.var(ddof=ddof)) if len(s) > 0 else None

def safe_covariance(series_x, series_y):
    x = pd.to_numeric(series_x, errors='coerce')
    y = pd.to_numeric(series_y, errors='coerce')
    df = pd.concat([x, y], axis=1).dropna()
    if df.shape[0] == 0:
        return None
    cov = np.cov(df.iloc[:, 0], df.iloc[:, 1], ddof=0)[0, 1]
    return float(cov)

def fit_distributions(series, continuous=True):
    s = pd.to_numeric(series, errors='coerce').dropna()
    res = []
    if len(s) < 5:
        return res
    if continuous:
        mu = float(s.mean())
        std = float(s.std(ddof=0))
        if std > 0:
            kstest = stats.kstest((s - mu) / std, 'norm')
            res.append({'dist': 'normal', 'params': {'mu': mu, 'std': std}, 'kstest_pvalue': float(kstest.pvalue)})
        else:
            res.append({'dist': 'normal', 'params': {'mu': mu, 'std': std}, 'kstest_pvalue': None})
        try:
            a, loc, scale = stats.gamma.fit(s, floc=0)
            kstest = stats.kstest(s, 'gamma', args=(a, loc, scale))
            res.append({'dist': 'gamma', 'params': {'a': float(a), 'loc': float(loc), 'scale': float(scale)}, 'kstest_pvalue': float(kstest.pvalue)})
        except Exception:
            pass
    else:
        lam = float(s.mean())
        res.append({'dist': 'poisson', 'params': {'lambda': lam}})
        try:
            mean = float(s.mean())
            var = float(s.var(ddof=0))
            if var > mean and mean > 0:
                p = mean / var
                r = mean * p / (1 - p) if p < 1 else None
                res.append({'dist': 'nbinom_mom', 'params': {'r': r, 'p': p}})
        except Exception:
            pass
    return res
