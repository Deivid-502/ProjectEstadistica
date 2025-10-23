import plotly.express as px
import pandas as pd

def timeseries_plot(df, date_col='date', y='new_cases', entity_col='country', countries=None):
    df = df.copy()
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    if countries:
        df = df[df[entity_col].isin(countries)]
    df = df.dropna(subset=[date_col])
    fig = px.line(df, x=date_col, y=y, color=entity_col, markers=True, title=f"Time series: {y}")
    fig.update_layout(transition={'duration':300, 'easing':'cubic-in-out'})
    return fig

def animated_choropleth(df, date_col='date', value_col='new_cases', code_col='country_code'):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col, code_col, value_col])
    agg = df.groupby([date_col, code_col])[value_col].sum().reset_index()
    agg['date_str'] = agg[date_col].dt.strftime('%Y-%m-%d')
    fig = px.choropleth(agg, locations=code_col, color=value_col, hover_name=code_col,
                        animation_frame='date_str', projection='natural earth',
                        title=f"Global {value_col} over time")
    fig.update_layout(transition={'duration':300, 'easing':'cubic-in-out'})
    return fig

def histogram_plot(df, col):
    df = df.copy()
    s = df[col].dropna() if col in df.columns else df.iloc[:,0].dropna()
    fig = px.histogram(s, x=col, nbins=30, title=f'Histogram of {col}')
    return fig
