import dash
import dcc as dcc
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
from functions.functions import get_analytics_s3
import plotly.graph_objects as go

dash.register_page(__name__, path="/analytics", name='ANALYTICS')

df = get_analytics_s3()

print(df.columns)
# https://www.youtube.com/watch?v=bDXypNBH1uw

dropdown1 = dcc.Dropdown(
    id="ticker_tipo2",
    options=[{"label": family, "value": family} for family in df["Tipo2"].unique()],
    # value="USA FLAT",
    placeholder="Seleccionar tipo de servicio",
    clearable=True,
    style={'background-color': 'grey'}
)

dropdown2 = dcc.Dropdown(
    id="ticker_motivo",
    options=[{"label": family, "value": family} for family in df["Nombre Motivo"].unique()],
    value="USA FLAT",
    placeholder="Seleccionar motivo",
    clearable=True,
    style={'background-color': 'grey'}
)

dropdown3 = dcc.Dropdown(
    id="ticker_mes",
    options=[{"label": family, "value": family} for family in df["mes_año"].unique()],
    value="2023-09",
    placeholder="Seleccionar mes",
    clearable=True,
    style={'background-color': 'grey'}
)
first_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("ANALYTICS", className="card-title"),
            html.P(" "),
            html.P("Seleccione el motivo o servicio para obtener los insights"),
            dropdown1,
            html.P(" "),
            dropdown2,
            html.P(" "),
            dropdown3,
            dbc.Button('Predict', id="btn_saldos", href='http://127.0.0.1:8088/control', external_link=True,
                       color="primary", style={'margin-top': '20px'}),
            dbc.Button('Forecast', id="btn_forecast", color="primary", href='http://127.0.0.1:8085/forecast',
                       style={'margin-top': '20px', 'margin-left': '8px'}),
        ]
    )
)

##card contents
# https://icons.getbootstrap.com/
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
                    dcc.Graph(id='total_kilos',
                              config={'displayModeBar': False},
                             ),
                ] ,style={"width": "15rem"}
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
                    dcc.Graph(id='total_guias',
                              config={'displayModeBar': False},
                              ),
                ], style={"width": "15rem"}
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
                    html.H5("Total Clientes", className="card-title"),
                    dcc.Graph(id='total_clientes',
                              config={'displayModeBar': False},
                              ),
                ], style={"width": "15rem"}
            )
        ),
    ]
    # ,className="mt-4 shadow",
)

cards = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content_kilos, color="primary", inverse=True, )),
                dbc.Col(dbc.Card(card_content_guias, color="warning", inverse=True)),
                dbc.Col(dbc.Card(card_content_clientes, color="info", inverse=True)),
            ],
            className="mb-4",
        )])

card_prueba = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Aca va el piechart", className="card-title"),
            html.H6("Card subtitle", className="card-subtitle"),
            html.P(
                "Some quick example text to build on the card title and make "
                "up the bulk of the card's content.",
                className="card-text",
            ),
            dbc.CardLink("Card link", href="#"),
            dbc.CardLink("External link", href="https://google.com"),
        ]
    ),
    style={"width": "18rem"},
)

segunda_fila= html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='pie_chart')),
                dbc.Col(dcc.Graph(id="line_graph")),
            ]
        )])



layout = html.Div([
    dbc.Row([
        dbc.Col([first_card], width=3, style={'marginLeft': '30px',
                                              'margin-right': '0px',
                                              'marginTop': '3px',
                                              'background-color': 'black'}),
        dbc.Col([cards, segunda_fila], width=8, style={  'marginLeft': '0px',
                                                         'margin-right': '0px',
                                                                'marginTop': '3px',
                                                                # 'margin': '30px',
                                                                'background-color': 'black'})]),


    ])
### callback pie chart
@callback(
    Output("pie_chart", "figure"),
    [Input('ticker_motivo', 'value'),
     Input('ticker_mes', 'value')])
def display_pie_chart(value, date):

    dff = df[df['Nombre Motivo'] == value]
    dff = dff[dff['mes_año'] == date]
    colors= ['#77b300','#fd7e14', '#6f42c1', '#2a9fd6']
    fig = px.pie(dff,
                 values='kilos facturables',
                 names='Categoria',
                 hole=.4,
                 width=307.799, height=400,
                 )

    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.02,
            xanchor="right",
            x=1
        ),
        legend_title_text='Categoria',
    )
    return fig



###callback line graph
@callback(
    Output("line_graph", "figure"),
    Input("ticker_motivo", "value"))
def display_time_series(value):

    dff = df[df['Nombre Motivo'] == value]

    dff = dff.groupby('mes_año')['kilos facturables'].sum().reset_index()

    dff.rename(columns={'mes_año': 'Mes'}, inplace=True)

    fig = px.line(dff, x='Mes', y='kilos facturables', markers=True, width=657, height=400)
    fig.update_traces(line_color='#2a9fd6')  ####77b300  ####6610f2 ####2a9fd6
    fig.update_layout(xaxis_title='Período',
                      yaxis_title='kilos',
                      title=f'Evolución kilos facturables {value}'
                      )
    return fig




###callback cards

# total kilos
@callback(
    Output('total_kilos', 'figure'),
    [Input('ticker_motivo', 'value'),
     Input('ticker_mes', 'value')]
)
def update_kilos(value, date):
    dff = df[df['Nombre Motivo'] == value]

    df_filtro = dff[dff['mes_año'] == date]

    total_kilos = df_filtro['kilos facturables'].sum()

    num_mes = list(date)[-2:]
    pal = num_mes[0] + num_mes[1]
    num = int(pal)
    mes_anterior = num - 1
    date_anterior = f'2023-{str(mes_anterior)}'
    if len(date_anterior) == 6:
        date_anterior = f'2023-0{str(mes_anterior)}'
    else:
        date_anterior = f'2023-{str(mes_anterior)}'

    df_filtro_mes_anterior = dff[dff['mes_año'] == date_anterior]

    total_kilos_mes_anterior = df_filtro_mes_anterior['kilos facturables'].sum()

    return {
        'data': [go.Indicator(
            mode="number+delta",
            value=total_kilos,
            number={'suffix': " kg","font":{"size":24}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_kilos_mes_anterior,
                   'relative':False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='white'),
            paper_bgcolor='#282828'
        )

    }

# total guias
@callback(
    Output('total_guias', 'figure'),
    [Input('ticker_motivo', 'value'),
     Input('ticker_mes', 'value')]
)
def update_guias(value, date):
    dff = df[df['Nombre Motivo'] == value]

    df_filtro = dff[dff['mes_año'] == date]

    total_guias = df_filtro['Guias_Numero'].unique().sum()

    num_mes = list(date)[-2:]
    pal = num_mes[0] + num_mes[1]
    num = int(pal)
    mes_anterior = num - 1
    date_anterior = f'2023-{str(mes_anterior)}'
    if len(date_anterior) == 6:
        date_anterior = f'2023-0{str(mes_anterior)}'
    else:
        date_anterior = f'2023-{str(mes_anterior)}'

    df_filtro_mes_anterior = dff[dff['mes_año'] == date_anterior]

    total_guias_mes_anterior = df_filtro_mes_anterior['Guias_Numero'].unique().sum()

    return {
        'data': [go.Indicator(
            mode="number+delta",
            value=total_guias,
            number={'suffix': " guias","font":{"size":24}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_guias_mes_anterior,
                   'relative':False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='white'),
            paper_bgcolor='#282828'
        )

    }

# total clientes
@callback(
    Output('total_clientes', 'figure'),
    [Input('ticker_motivo', 'value'),
     Input('ticker_mes', 'value')]
)
def update_guias(value, date):
    dff = df[df['Nombre Motivo'] == value]

    df_filtro = dff[dff['mes_año'] == date]

    total_clientes = len(df_filtro['Clientes_Codigo'].unique())

    num_mes = list(date)[-2:]
    pal = num_mes[0] + num_mes[1]
    num = int(pal)
    mes_anterior = num - 1
    date_anterior = f'2023-{str(mes_anterior)}'
    if len(date_anterior) == 6:
        date_anterior = f'2023-0{str(mes_anterior)}'
    else:
        date_anterior = f'2023-{str(mes_anterior)}'

    df_filtro_mes_anterior = dff[dff['mes_año'] == date_anterior]

    total_clientes_mes_anterior = len(df_filtro_mes_anterior['Clientes_Codigo'].unique())

    return {
        'data': [go.Indicator(
            mode="number+delta",
            value=total_clientes,
            number={'suffix': " clientes","font":{"size":24}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_clientes_mes_anterior,
                   'relative':False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='white'),
            paper_bgcolor='#282828'
        )

    }
