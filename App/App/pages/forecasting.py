import dash
from dash import html, Input, Output, callback
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from dash import dcc
import dash_bootstrap_components as dbc
from functions.functions import get_forecast_s3, get_data_s3

pd.options.plotting.backend = "plotly"
from dash_bootstrap_templates import load_figure_template

load_figure_template(["darkly"])

dash.register_page(__name__, path='/forecast', name='FORECAST')

##https://fontawesome.bootstrapcheatsheets.com/

df = get_data_s3()
all_preds = get_forecast_s3()

dropdown = dcc.Dropdown(
    id="ticker",
    options=[{"label": family, "value": family} for family in df["family"].unique()],
    value="USA FLAT",
    clearable=False,
    style={'background-color': 'grey'}
)

first_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("FORECAST", className="card-title"),
            html.P(" "),
            html.P("Seleccione el motivo para obtener las predicciones de las próximas 10 semanas"),
            dcc.Download(id="download-dataframe-xlsx"),
            dropdown,
            dbc.Button('Analytics', id="btn_dashboard", color="primary",href='http://127.0.0.1:8085/analytics',
                       style={'margin-top': '20px', 'margin-left': '8px'}),
        ]
    )
)

# https://towardsdatascience.com/create-a-professional-dasbhoard-with-dash-and-css-bootstrap-e1829e238fc5

### 3 cards arriba de grafico
card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

card_content_esperados = dbc.CardGroup(
    [
        dbc.Card(
            html.Div(className="bi bi-box-seam", style=card_icon),
            className="bg-primary",
            style={"maxWidth": 75},
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Kilos Esperados", className="card-title"),
                    dcc.Graph(id='esperado',
                              config={'displayModeBar': False},
                              ),
                ], style={"width": "15rem"}
            )
        ),
    ]

)
card_content_mejor = dbc.CardGroup(
    [
        dbc.Card(
            html.Div(className="bi bi-hand-thumbs-up", style=card_icon),
            className="bg-warning",
            style={"maxWidth": 75},
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Mejor Escenario", className="card-title"),
                    dcc.Graph(id='mejor',
                             config={'displayModeBar': False},
                             ),
                ], style={"width": "15rem"}
            )
        ),
    ]

)

card_content_peor= dbc.CardGroup(
    [
        dbc.Card(
            html.Div(className="bi bi-hand-thumbs-down", style=card_icon),
            className="bg-info",
            style={"maxWidth": 75},
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Peor Escenario", className="card-title"),
                    dcc.Graph(id='peor',
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
                dbc.Col(dbc.Card(card_content_esperados, color="primary", inverse=True, )),
                dbc.Col(dbc.Card(card_content_mejor, color="warning", inverse=True)),
                dbc.Col(dbc.Card(card_content_peor, color="info", inverse=True)),
            ],
            className="mb-4",
        )])



layout = html.Div(
    dbc.Row([
        dbc.Col([first_card], width=3, style={'marginLeft': '50px',
                                              'margin-right': '0px',
                                              'marginTop': '3px',
                                              'background-color': 'black'}),
        dbc.Col([cards,
                dcc.Graph(id="time-series-chart")], width=8, style={'marginLeft': '20px',
                                                                     'margin-right': '30px',
                                                                     'marginTop': '3px',
                                                                     #'margin': '30px',
                                                                     'background-color': 'black'}),

    ]))


@callback(
    Output("time-series-chart", "figure"),
    Input("ticker", "value"))
def display_time_series(ticker):
    df_pivot = df.pivot(index='ds', columns='family', values='y')
    df_pivot = df_pivot.reset_index()
    df_pivot = df_pivot.fillna(0)

    fig = px.line(df_pivot, x='ds', y=ticker,
                  #title="Seleccionar el periodo",
                  template='plotly_dark',
                  #color_discrete_sequence=["#2a9fd6"]
                  )
    # bandas de percentiles
    p_ = all_preds.loc[all_preds['family'] == ticker]
    fig.add_trace(
        go.Scatter(x=p_['ds'], y=p_['p10'], mode='lines', line=dict(color='rgba(255, 165, 0, 0.2)'), name='p10'))
    fig.add_trace(
        go.Scatter(x=p_['ds'], y=p_['p90'], mode='lines', line=dict(color='rgba(255, 165, 0, 0.2)'), name='p90',
                   fill='tonexty', fillcolor='rgba(255, 165, 0, 0.2)'))
    fig.add_trace(go.Scatter(x=p_['ds'], y=p_['p25'], mode='lines', line=dict(color='orange'), name='p25'))
    fig.add_trace(
        go.Scatter(x=p_['ds'], y=p_['p75'], mode='lines', line=dict(color='orange'), name='p75', fill='tonexty',
                   fillcolor='rgba(255, 165, 0, 0.2)'))
    fig.add_trace(go.Scatter(x=p_['ds'], y=p_['pred'], mode='lines', line=dict(color='orange'), name='Forecast'))
    fig.update_yaxes(gridcolor='#3b3939')
    fig.update_xaxes(
        rangeslider_visible=False,
        gridcolor='#3b3939',
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig.update_layout(plot_bgcolor='#282828',
                      paper_bgcolor='#282828',
                      margin=dict(l=20, r=20, t=20, b=10),
                      xaxis_rangeselector_font_color='white',
                      xaxis_rangeselector_activecolor='orange',
                      xaxis_rangeselector_bgcolor='#2a9fd6',
                      xaxis_title='Semana', yaxis_title='kilos'
                      )
    return fig

##cards

##kilos esperados

@callback(
    Output('esperado', 'figure'),
    Input('ticker', 'value')
)
def update_kilos(ticker):

    df = all_preds.loc[all_preds['family'] == ticker]
    a = float(str(list(df.pred)[0]))

    return {
        'data': [go.Indicator(
            mode="number",
            value=a,
            number={'suffix': " kg", "font": {"size": 24}, "valueformat": ",.0f"},
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='white'),
            paper_bgcolor='#282828'
        )

    }

##mejor escenario

@callback(
    Output('mejor', 'figure'),
    Input('ticker', 'value')
)
def update_kilos(ticker):

    df = all_preds.loc[all_preds['family'] == ticker]
    a = float(str(list(df.p75)[0]))

    return {
        'data': [go.Indicator(
            mode="number",
            value=a,
            number={'suffix': " kg", "font": {"size": 24}, "valueformat": ",.0f"},
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='white'),
            paper_bgcolor='#282828'
        )

    }

##peor escenario

@callback(
    Output('peor', 'figure'),
    Input('ticker', 'value')
)
def update_kilos(ticker):

    df = all_preds.loc[all_preds['family'] == ticker]
    a = float(str(list(df.p25)[0]))

    return {
        'data': [go.Indicator(
            mode="number",
            value=a,
            number={'suffix': " kg", "font": {"size": 24}, "valueformat": ",.0f"},
            domain={'x': [0, 1], 'y': [0, 1]}
        )],
        'layout': go.Layout(
            height=30,
            font=dict(color='white'),
            paper_bgcolor='#282828'
        )

    }

