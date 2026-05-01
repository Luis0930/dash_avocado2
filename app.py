import os
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

df = pd.read_csv("salesmonthly.csv")
df["datum"] = pd.to_datetime(df["datum"], format="%d/%m/%y")
df["Año"] = df["datum"].dt.year

categorias = ["M01AB","M01AE","N02BA","N02BE","N05B","N05C","R03","R06"]

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

app.layout = dbc.Container([
    html.H1("Tablero de Ventas Farmacéuticas"),
    dcc.Dropdown(id="cat", options=[{"label":c,"value":c} for c in categorias], value="M01AB"),
    dcc.Graph(id="graf")
])

@app.callback(Output("graf","figure"), Input("cat","value"))
def update(cat):
    return px.line(df, x="datum", y=cat)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
