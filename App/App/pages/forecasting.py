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

dash.register_page(__name__, path='/forecasting', name='FORECASTING')

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
            html.H5("FORECASTING", className="card-title"),
            html.P(" "),
            html.P("Seleccione el motivo para obtener las predicciones de las proximas 10 semanas"),
            dcc.Download(id="download-dataframe-xlsx"),
            dropdown,
            dbc.Button('Predict', id="btn_saldos", href='http://127.0.0.1:8088/control', external_link=True,
                       color="primary", style={'margin-top': '20px'}),
            dbc.Button('Dashboard', id="btn_dashboard", color="primary",
                       style={'margin-top': '20px', 'margin-left': '8px'}),
        ]
    )
)

# https://towardsdatascience.com/create-a-professional-dasbhoard-with-dash-and-css-bootstrap-e1829e238fc5


layout = html.Div(
    dbc.Row([
        dbc.Col([first_card], width=3, style={'marginLeft': '30px',
                                              'margin-right': '0px',
                                              'marginTop': '3px',
                                              'background-color': 'black'}),
        dbc.Col([dbc.Card(dbc.CardBody([html.P(" "),
                                        html.H5("Motivo", className="card-title"),
                                        html.P(" "),
                                        html.P("El pronostico de kilos brutos para la semana del ... es .... kg")])),
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

    fig.update_xaxes(
        rangeslider_visible=False,
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
                      xaxis_title='Semana', yaxis_title=f'{ticker}'
                      )
    return fig
