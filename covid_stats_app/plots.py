# plots.py
import plotly.express as px
import pandas as pd
import plotly.io as pio
from pathlib import Path

def timeseries_plot(df, date_col='date', y='new_cases', entity_col='country', countries=None, y_label=None, title=None):
    df = df.copy()
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    if countries and entity_col in df.columns:
        df = df[df[entity_col].isin(countries)]
    if entity_col and entity_col in df.columns:
        fig = px.line(df, x=date_col, y=y, color=entity_col, markers=True, title=title or "")
        fig.update_layout(legend_title=entity_col)
    else:
        fig = px.line(df, x=date_col, y=y, markers=True, title=title or "")
    fig.update_layout(xaxis_title="Fecha", yaxis_title=y_label or y, transition={'duration':300, 'easing':'cubic-in-out'})
    return fig

def animated_choropleth(df, date_col='date', value_col='value', code_col='country_code', title=None, color_scale='Reds'):
    """
    df: preagregado por (date_col, code_col, value_col). value_col debe existir.
    Esta versión fija range_color para toda la animación para que el mapa cambie de color correctamente.
    Incluye controles play/pause y define duración de frame.
    """
    if df is None or df.empty:
        raise ValueError("No hay datos para la animación.")
    tmp = df.copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors='coerce')
    tmp = tmp.dropna(subset=[date_col, code_col, value_col])
    if tmp.empty:
        raise ValueError("No hay registros válidos con fecha, código de país y valor.")
    tmp[code_col] = tmp[code_col].astype(str).str.upper()
    tmp['date_str'] = tmp[date_col].dt.strftime('%Y-%m-%d')
    tmp = tmp.sort_values(date_col)
    agg = tmp.groupby(['date_str', code_col], as_index=False)[value_col].sum()
    # calcular rango global para colors
    vmin = agg[value_col].min() if not agg[value_col].empty else 0
    vmax = agg[value_col].max() if not agg[value_col].empty else 1

    title = title or f"Animación — {value_col}"
    fig = px.choropleth(
        agg,
        locations=code_col,
        color=value_col,
        hover_name=code_col,
        animation_frame='date_str',
        projection='natural earth',
        title=title,
        locationmode='ISO-3',
        range_color=(vmin, vmax),
        color_continuous_scale=color_scale
    )
    fig.update_layout(transition={'duration':300, 'easing':'cubic-in-out'}, coloraxis_colorbar=dict(title="Casos"))
    fig.update_traces(marker_line_width=0.1)

    # Añadir control play/pause y customizar velocidad de frames
    if fig.frames:
        fig.layout.updatemenus = [
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}]
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 10},
                "showactive": True,
                "x": 0.1,
                "y": 0.05
            }
        ]
    return fig

def histogram_plot(df, col, x_label=None, y_label=None, title=None, nbins=30):
    df = df.copy()
    if col not in df.columns:
        raise ValueError(f"La columna {col} no existe en el DataFrame.")
    s = pd.to_numeric(df[col], errors='coerce').dropna()
    title = title or f"Histograma — {x_label or col}"
    df_plot = pd.DataFrame({x_label or col: s})
    fig = px.histogram(df_plot, x=x_label or col, nbins=nbins, title=title)
    fig.update_layout(xaxis_title=x_label or col, yaxis_title=y_label or "Frecuencia", bargap=0.05)
    return fig

def bar_plot(df, x, y, x_label=None, y_label=None, title=None):
    df = df.copy()
    title = title or f"{y_label or y} por {x_label or x}"
    fig = px.bar(df, x=x, y=y, title=title)
    fig.update_layout(xaxis_title=x_label or x, yaxis_title=y_label or y)
    return fig

def save_fig_html(fig, out_path, include_plotlyjs='cdn'):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = pio.to_html(fig, include_plotlyjs=include_plotlyjs)
    out_path.write_text(html, encoding='utf-8')
    return out_path
