# -*- coding: utf-8 -*-

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc


# =========================
# 1. CARGAR LA BASE DE DATOS
# =========================

df = pd.read_csv("salesmonthly.csv")

df["datum"] = pd.to_datetime(df["datum"], format="%d/%m/%y")
df["Año"] = df["datum"].dt.year
df["Mes"] = df["datum"].dt.month

categorias = ["M01AB", "M01AE", "N02BA", "N02BE", "N05B", "N05C", "R03", "R06"]
años = sorted(df["Año"].unique())


# =========================
# 2. CREAR LA APP
# =========================

external_stylesheets = [dbc.themes.CERULEAN]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Tablero de ventas farmacéuticas"


# =========================
# 3. DISEÑO DEL TABLERO
# =========================

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H1(
                "Tablero de Ventas Farmacéuticas",
                className="text-center text-primary mt-4"
            ),
            html.P(
                "Análisis mensual de ventas por categorías de medicamentos entre 2014 y 2019",
                className="text-center"
            )
        ])
    ]),

    html.Hr(),

    dbc.Row([

        dbc.Col([
            html.Label("Categoría para gráfico de líneas"),
            dcc.Dropdown(
                id="categoria-linea",
                options=[{"label": c, "value": c} for c in categorias],
                value="M01AB",
                clearable=False
            )
        ], width=3),

        dbc.Col([
            html.Label("Rango de fechas"),
            dcc.DatePickerRange(
                id="rango-fechas",
                min_date_allowed=df["datum"].min(),
                max_date_allowed=df["datum"].max(),
                start_date=df["datum"].min(),
                end_date=df["datum"].max(),
                display_format="YYYY-MM-DD"
            )
        ], width=3),

        dbc.Col([
            html.Label("Año para barras y torta"),
            dcc.Dropdown(
                id="año-seleccionado",
                options=[{"label": str(a), "value": a} for a in años],
                value=años[-1],
                clearable=False
            )
        ], width=3),

        dbc.Col([
            html.Label("Categoría para histograma"),
            dcc.RadioItems(
                id="categoria-histograma",
                options=[{"label": c, "value": c} for c in categorias],
                value="M01AB",
                inline=True
            )
        ], width=3),

    ], className="mb-4"),

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("1. Tendencia mensual con selector de rango"),
                dbc.CardBody([
                    dcc.Graph(id="grafico-linea")
                ])
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("2. Ventas totales por categoría"),
                dbc.CardBody([
                    html.Button(
                        "Cambiar fondo",
                        id="boton-fondo",
                        n_clicks=0,
                        className="btn btn-primary mb-2"
                    ),
                    dcc.Graph(id="grafico-barras")
                ])
            ])
        ], width=6),

    ], className="mb-4"),

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("3. Participación porcentual por categoría"),
                dbc.CardBody([
                    dcc.Graph(id="grafico-torta")
                ])
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("4. Distribución mensual de una categoría"),
                dbc.CardBody([
                    dcc.Graph(id="grafico-histograma")
                ])
            ])
        ], width=6),

    ]),

], fluid=True)


# =========================
# 4. CALLBACKS
# =========================

@app.callback(
    Output("grafico-linea", "figure"),
    Input("categoria-linea", "value"),
    Input("rango-fechas", "start_date"),
    Input("rango-fechas", "end_date")
)
def actualizar_linea(categoria, fecha_inicio, fecha_fin):

    datos_filtrados = df[
        (df["datum"] >= fecha_inicio) &
        (df["datum"] <= fecha_fin)
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=datos_filtrados["datum"],
        y=datos_filtrados[categoria],
        mode="lines+markers",
        name=categoria
    ))

    fig.update_layout(
        title=f"Ventas mensuales de {categoria}",
        xaxis_title="Fecha",
        yaxis_title="Ventas",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="Mes", step="month", stepmode="backward"),
                    dict(count=6, label="Semestre", step="month", stepmode="backward"),
                    dict(count=1, label="Año", step="year", stepmode="backward"),
                    dict(step="all", label="Todo")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig


@app.callback(
    Output("grafico-barras", "figure"),
    Input("año-seleccionado", "value"),
    Input("boton-fondo", "n_clicks")
)
def actualizar_barras(año, clicks):

    datos_año = df[df["Año"] == año]

    ventas = datos_año[categorias].sum().reset_index()
    ventas.columns = ["Categoria", "Ventas"]

    fig = px.bar(
        ventas,
        x="Categoria",
        y="Ventas",
        text="Ventas",
        title=f"Ventas totales por categoría en {año}"
    )

    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")

    if clicks % 2 == 0:
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    else:
        fig.update_layout(
            plot_bgcolor="#EAF2F8",
            paper_bgcolor="#EAF2F8"
        )

    fig.update_layout(
        xaxis_title="Categoría",
        yaxis_title="Ventas"
    )

    return fig


@app.callback(
    Output("grafico-torta", "figure"),
    Input("año-seleccionado", "value")
)
def actualizar_torta(año):

    datos_año = df[df["Año"] == año]

    ventas = datos_año[categorias].sum().reset_index()
    ventas.columns = ["Categoria", "Ventas"]

    fig = px.pie(
        ventas,
        values="Ventas",
        names="Categoria",
        title=f"Participación porcentual de ventas en {año}",
        hole=0.35
    )

    return fig


@app.callback(
    Output("grafico-histograma", "figure"),
    Input("categoria-histograma", "value")
)
def actualizar_histograma(categoria):

    fig = px.histogram(
        df,
        x=categoria,
        nbins=20,
        title=f"Distribución de ventas mensuales de {categoria}"
    )

    fig.update_layout(
        xaxis_title="Ventas mensuales",
        yaxis_title="Frecuencia"
    )

    return fig


# =========================
# 5. EJECUTAR LA APP
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
