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

    html.H1("Tablero de Ventas Farmacéuticas", className="text-center"),

    dbc.Row([
        dbc.Col([
            html.Label("Categoría"),
            dcc.Dropdown(
                id="cat",
                options=[{"label": c, "value": c} for c in categorias],
                value="M01AB"
            )
        ], width=4),

        dbc.Col([
            html.Label("Rango de fechas"),
            dcc.DatePickerRange(
                id="fecha",
                min_date_allowed=df["datum"].min(),
                max_date_allowed=df["datum"].max(),
                start_date=df["datum"].min(),
                end_date=df["datum"].max()
            )
        ], width=8)
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(dcc.Graph(id="linea"), width=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id="barras"), width=6),
        dbc.Col(dcc.Graph(id="torta"), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id="histograma"), width=12)
    ])

], fluid=True)


@app.callback(
    Output("linea", "figure"),
    Output("barras", "figure"),
    Output("torta", "figure"),
    Output("histograma", "figure"),
    Input("cat", "value"),
    Input("fecha", "start_date"),
    Input("fecha", "end_date")
)
def actualizar(cat, start, end):

    # Filtrar por fechas
    dff = df[(df["datum"] >= start) & (df["datum"] <= end)]

    # 📈 Línea
    fig_linea = px.line(
        dff,
        x="datum",
        y=cat,
        title=f"Evolución de {cat}"
    )

    # 📊 Barras
    total = dff[categorias].sum().reset_index()
    total.columns = ["Categoria", "Ventas"]

    fig_barras = px.bar(
        total,
        x="Categoria",
        y="Ventas",
        title="Ventas por categoría"
    )

    # 🥧 Torta
    fig_torta = px.pie(
        total,
        names="Categoria",
        values="Ventas",
        title="Participación por categoría"
    )

    # 📊 Histograma
    fig_hist = px.histogram(
        dff,
        x=cat,
        nbins=20,
        title="Distribución de ventas"
    )

    return fig_linea, fig_barras, fig_torta, fig_hist


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
