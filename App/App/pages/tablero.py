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
import dash_table
import dash_bootstrap_components as dbc
from functions.functions import get_analytics_s3
import plotly.graph_objects as go

dash.register_page(__name__, path="/analytics", name='ANALYTICS')

df = get_analytics_s3()

print(df.columns)
# https://www.youtube.com/watch?v=bDXypNBH1uw

ultimo_mes = list(df.mes_año.unique())[-1]
dff= df[df['mes_año']== ultimo_mes]

dropdown1 = dcc.Dropdown(
    id="ticker_motivo",
    options=[{"label": family, "value": family} for family in dff["Nombre Motivo"].unique()],
    value="USA FLAT",
    placeholder="Seleccionar motivo",
    clearable=True,
    style={'background-color': 'grey'}
)

dropdown2 = dcc.Dropdown(
    id="ticker_mes",
    options=[{"label": family, "value": family} for family in df["mes_año"].unique()],
    value="2023-09",
    placeholder="Seleccionar mes",
    clearable=True,
    style={'background-color': 'grey'}
)
first_card = html.Div(
    dbc.Card(
        dbc.CardBody(
            [
                html.H5("ANALYTICS", className="card-title"),
                html.P("Utilizar los filtros para ver los insights"),
                html.P(" "),
                dropdown1,
                html.P(" "),
                dropdown2,
                dbc.Button('Forecast', id="btn_forecast", color="primary", href='http://127.0.0.1:8085/forecast',
                           style={'margin-top': '20px', 'margin-left': '8px'}),
            ]
        )
    ), className='mb-1',
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
                ], style={"width": "15rem"}
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

segunda_fila = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='pie_chart')),
                dbc.Col(dcc.Graph(id="line_graph")),
            ]
        )])

cards_tipo_servicios = html.Div(
    [  ###impo Courier
        dbc.CardGroup(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Impo Courier",
                                ],
                                className="card-text",
                            ),
                        ]
                    ),
                    className="mb-1", color="info", inverse=True
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Graph(id='courier_impo',
                                      ),
                        ],
                    ), className="mb-1"
                ),
            ], style={"margin_left": "5px"},

        )
        ,
        dbc.CardGroup(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Expo Courier",
                                ],
                                className="card-text",
                            ),
                        ]
                    ),
                    className="mb-1", color="warning", inverse=True
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Graph(id='courier_expo',
                                      ),
                        ],
                    ), className="mb-1"
                ),
            ], style={"margin_left": "5px"},

        )
        ,
        dbc.CardGroup(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Exporta Simple",
                                ],
                                className="card-text",
                            ),
                        ]
                    ),
                    className="mb-1", color="danger", inverse=True
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Graph(id='exporta_simple',
                                      ),
                        ],
                    ), className="mb-1"
                ),
            ], style={"margin_left": "5px"},

        )
        ,
        dbc.CardGroup(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Cargas",
                                ],
                                className="card-text",
                            ),
                        ]
                    ),
                    className="mb-1", color="success", inverse=True
                ),
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Graph(id='cargas',
                                      ),
                        ],
                    ), className="mb-1"
                ),
            ], style={"margin_left": "5px"},

        )
        ,
    ]
)


###table
def generate_table_data():
    meses_filtrados = df['mes_año'].unique()[-5:]
    df_filtrado = df[df['mes_año'].isin(meses_filtrados)]

    # 2. Pivotar el DataFrame para obtener una columna por cada mes
    df_pivot = df_filtrado.pivot_table(index=['Cliente', 'Nombre Motivo'],
                                       columns='mes_año',
                                       values='kilos facturables',
                                       aggfunc='sum',
                                       fill_value=0)

    df_pivot['Total'] = df_pivot.sum(axis=1)
    df_pivot = df_pivot.reset_index()  # Restablecer los índices
    df_pivot = df_pivot.sort_values(by='Total', ascending=False)
    # Agregar "kg" al final de cada valor en la tabla
    df_pivot.iloc[:, 2:] = df_pivot.iloc[:, 2:].applymap(lambda x: f"{x} kg")


    return df_pivot


df_table = generate_table_data()

table = dash_table.DataTable(
    df_table.to_dict("records"),
    [{"name": i, "id": i} for i in df_table.columns],
    filter_action="native",
    sort_action="native",
    sort_mode= "multi",
    filter_options={"placeholder_text": "Filter column..."},
    page_size=15,
    style_as_list_view=True,
    style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['Cliente', 'Nombre Motivo']
    ],
    style_header={
        'backgroundColor': '#2a9fd6',
        'fontWeight': 'bold',
        'color': 'white',
        'fontSize':15
    },
    style_data={
        'color': '#adafae',
        'backgroundColor': '#282828'  # 555'
    },
    style_cell={'fontSize':14,
                'font-family':'Roboto',
                'padding-right': '10px',
                'padding-left': '10px'}

)

###Download button
download_excel_button = html.Div([
                                dbc.Button('Descargar Excel', id="btn_xlsx", color="primary",
                                           style={'margin-top': '8px',
                                                  'margin-left': '1220px',
                                                  'margin-bottom': '8px'}),
                                dcc.Download(id="download-dataframe-xlsx"),
])

##page layout
layout = html.Div([
    dbc.Row([
        dbc.Col([first_card, cards_tipo_servicios], width=3, style={'marginLeft': '60px',
                                                                    'margin-right': '0px',
                                                                    'marginTop': '3px',
                                                                    'background-color': 'black',
                                                                    'margin_bottom': '20px'}),
        dbc.Col([cards, segunda_fila], width=8, style={'marginLeft': '0px',
                                                       'margin-right': '0px',
                                                       'marginTop': '3px',
                                                       'background-color': 'black'})]),

    dbc.Row(dbc.Col([download_excel_button,table], width=11, style={'marginLeft': '60px',
                                                                    'margin-right': '0px',
                                                                    'marginTop': '3px',
                                                                    'background-color': 'black'}))
])

##CALLBACKS!!!

###callback download excel
@callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df_table.to_excel, "Raiconet Data.xlsx", sheet_name="Clientes", index=False)

### callback pie chart
@callback(
    Output("pie_chart", "figure"),
    [Input('ticker_motivo', 'value'),
     Input('ticker_mes', 'value')])
def display_pie_chart(value, date):
    dff = df[df['Nombre Motivo'] == value]
    dff = dff[dff['mes_año'] == date]
    colors = ['#77b300', '#fd7e14', '#6f42c1', '#2a9fd6']
    fig = px.pie(dff,
                 values='kilos facturables',
                 names='Categoria',
                 hole=.4,
                 width=307.799, height=400,
                 color_discrete_sequence=['#2a9fd6', '#77b300', '#fd7e14', '#6f42c1'])

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
    fig.update_traces(textfont_size=15, textinfo='percent+label', textfont_color='white')
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

###courier impo

@callback(
    Output('courier_impo', 'figure'),
    Input('ticker_mes', 'value')
)
def update_kilos(date):
    dff = df[df['Tipo2'] == 'Courier Impo']

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
            number={'suffix': " kg", "font": {"size": 18}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_kilos_mes_anterior,
                   'relative': False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='grey'),
            paper_bgcolor='#282828'
        )

    }


###courier expo

@callback(
    Output('courier_expo', 'figure'),
    Input('ticker_mes', 'value')
)
def update_kilos(date):
    dff = df[df['Tipo2'] == 'Courier Expo']

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
            number={'suffix': " kg", "font": {"size": 18}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_kilos_mes_anterior,
                   'relative': False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='grey'),
            paper_bgcolor='#282828'
        )

    }


###exporta simple

@callback(
    Output('exporta_simple', 'figure'),
    Input('ticker_mes', 'value')
)
def update_kilos(date):
    dff = df[df['Tipo2'] == 'Exporta Simple']

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
            number={'suffix': " kg", "font": {"size": 18}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_kilos_mes_anterior,
                   'relative': False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='grey'),
            paper_bgcolor='#282828'
        )

    }


###cargas
@callback(
    Output('cargas', 'figure'),
    Input('ticker_mes', 'value')
)
def update_kilos(date):
    dff = df[df['Tipo2'] == 'Carga']

    df_filtro = dff[dff['mes_año'] == date]

    total_kilos = df_filtro['Guias_Numero'].sum()

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
            number={'suffix': " guias", "font": {"size": 18}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_kilos_mes_anterior,
                   'relative': False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='grey'),
            paper_bgcolor='#282828'
        )

    }


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
            number={'suffix': " kg", "font": {"size": 24}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_kilos_mes_anterior,
                   'relative': False, },
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

    total_guias = df_filtro['Guias_Numero'].sum()

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
            number={'suffix': " guias", "font": {"size": 24}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_guias_mes_anterior,
                   'relative': False, },
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
            number={'suffix': " clientes", "font": {"size": 24}, "valueformat": ",.0f"},
            delta={'position': "right", 'reference': total_clientes_mes_anterior,
                   'relative': False, },
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='white'),
            paper_bgcolor='#282828'
        )

    }
