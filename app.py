import os
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Leer datos
df = pd.read_csv("salesmonthly.csv")
df["datum"] = pd.to_datetime(df["datum"], format="%d/%m/%y")
df["Año"] = df["datum"].dt.year

categorias = ["M01AB","M01AE","N02BA","N02BE","N05B","N05C","R03","R06"]

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

app.layout = dbc.Container([

    html.H1("Tablero de Ventas Farmacéuticas"),

    # Dropdown
    dcc.Dropdown(
        id="cat",
        options=[{"label": c, "value": c} for c in categorias],
        value="M01AB"
    ),

    dcc.Graph(id="linea"),
    dcc.Graph(id="barras"),
    dcc.Graph(id="torta"),
    dcc.Graph(id="histograma")

])

@app.callback(
    Output("linea", "figure"),
    Output("barras", "figure"),
    Output("torta", "figure"),
    Output("histograma", "figure"),
    Input("cat", "value")
)
def actualizar(cat):

    # Línea
    fig_linea = px.line(df, x="datum", y=cat, title=f"Evolución de {cat}")

    # Barras (suma por año)
    df_year = df.groupby("Año")[categorias].sum().reset_index()
    fig_barras = px.bar(df_year, x="Año", y=cat, title="Ventas por año")

    # Torta (total por categoría)
    total = df[categorias].sum()
    fig_torta = px.pie(
        values=total.values,
        names=total.index,
        title="Participación por categoría"
    )

    # Histograma
    fig_hist = px.histogram(df, x=cat, nbins=20, title="Distribución")

    return fig_linea, fig_barras, fig_torta, fig_hist


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
