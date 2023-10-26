import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import pandas as pd
import datetime
from dash import dcc
from datetime import date
import dash_bootstrap_components as dbc
from functions.functions import get_analytics_s3, get_data_s3

dash.register_page(__name__, path="/analytics", name='ANALYTICS')

df = get_analytics_s3()

#https://www.youtube.com/watch?v=bDXypNBH1uw

dropdown1 = dcc.Dropdown(
    id="ticker",
    options=[{"label": family, "value": family} for family in df["Tipo"].unique()],
    #value="USA FLAT",
    clearable=False,
    style={'background-color': 'grey'}
)


dropdown3 = dcc.Dropdown(
    id="ticker",
    options=[{"label": family, "value": family} for family in df["mes_año"].unique()],
    #value="USA FLAT",
    clearable=False,
    style={'background-color': 'grey'}
)
first_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("ANALYTICS", className="card-title"),
            html.P(" "),
            html.P("Seleccione el motivo o servicio para obtener los insights"),
            dropdown1,
            dropdown3,
            dbc.Button('Predict', id="btn_saldos", href='http://127.0.0.1:8088/control', external_link=True,
                       color="primary", style={'margin-top': '20px'}),
            dbc.Button('Forecast', id="btn_forecast", color="primary", href='http://127.0.0.1:8085/forecast',
                       style={'margin-top': '20px', 'margin-left': '8px'}),
        ]
    )
)

##card contents
#https://icons.getbootstrap.com/
card_icon = {
   "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

card_content_kilos = dbc.CardGroup(
    [
        dbc.Card(
            html.Div(className="bi bi-box-seam", style=card_icon),
            className="bg-primary",
            style={"maxWidth": 75},
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Total Kilos", className="card-title"),
                    html.P("40000 kg", className="card-text",),
                ]
            )
        ),
    ]

)
card_content_guias = dbc.CardGroup(
    [
        dbc.Card(
            html.Div(className="bi bi-cursor-fill", style=card_icon),
            className="bg-warning",
            style={"maxWidth": 75},
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Total Guias", className="card-title"),
                    html.P("40000 ", className="card-text",),
                ]
            )
        ),
    ]

)

card_content_clientes = dbc.CardGroup(
    [
        dbc.Card(
            html.Div(className="bi bi-people-fill", style=card_icon),
            className="bg-info",
            style={"maxWidth": 75},
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("3000", className="card-title"),
                    html.P("Clientes", className="card-text",),
                ]
            )
        ),
    ]
    #,className="mt-4 shadow",
)


cards = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content_kilos, color="primary", inverse=True,)),
                dbc.Col(dbc.Card(card_content_guias,color="warning", inverse=True)),
                dbc.Col(dbc.Card(card_content_clientes,color="info",inverse=True)),
            ],
            className="mb-4",
        ) ])

### table
table = dbc.Table.from_dataframe(df)

layout = html.Div(
    dbc.Row([
        dbc.Col([first_card], width=3, style={'marginLeft': '30px',
                                              'margin-right': '0px',
                                              'marginTop': '3px',
                                              'background-color': 'black'}),
        dbc.Col([cards, table], width=8, style={  # 'marginLeft': '20px',
            'margin-right': '30px',
            'marginTop': '3px',
            # 'margin': '30px',
            'background-color': 'black'}),

    ])
)
