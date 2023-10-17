import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name='INICIO')  #/ because its the home page

button = html.Div(
    [
        dbc.Button(
            "EMPEZAR",
            href="/forecasting",
            #download="my_data.txt",
            external_link=False,
           # color='dark',
        ),
    ]
)

SQUARE = "assets/icon_sin_back.png"

layout = html.Div([
    dbc.Row([
        dbc.Col(dcc.Markdown('''
                        ##### TABLERO DE CONTROL
                        

                        # __RAICO__

                        # __ANALYTICS__

                        ###### Powered by TIX
                                '''),
                align='center',
                width=4,
                style={'fontSize': '50px',
                       'margin': '56px',
                       'marginRight': '100px',
                       'marginLeft': '180px',
                       'marginTop': '2px',
                       'color': 'white',
                       }),

        dbc.Col(html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=SQUARE, height="508px"))
                ],
                align="right",
                className="g-0",
            ),
            href="https://www.tixdatascience.com/",
            style={"textDecoration": "none",
                   # 'margin-left': '35px',
                   'margin': '40px'},
        ), width=2)]),
        dbc.Row(
            dbc.Col(html.Div(button), width=4, align= 'center',
                                        style={'margin': '180px',
                                               'marginTop': '-160px',
                                               'marginBottom':'250px'})
        )]

)

