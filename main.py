# Deribit IVRank/IVPercentile app

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
import plotly.graph_objects as go
from api_functions import get_volatility_index_data
from datetime import datetime

now = datetime.now()
end_timestamp = round(datetime.timestamp(now) * 1000)
year_milliseconds = 1000 * 60 * 60 * 24 * 365
start_timestamp = end_timestamp - year_milliseconds
currency = "BTC"
resolution = 43200  # resolution of vol data in seconds, e.g. 1 hour = 3600


def get_data():
    # fetch the DVOL data from the api
    raw_data = get_volatility_index_data(currency, start_timestamp, end_timestamp, resolution)

    # put data into a dataframe, add column names
    columns = ['timestamp', 'open', 'high', 'low', 'close']
    df = pd.DataFrame(raw_data['data'], columns=columns)
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

    candles = go.Figure(
        data=[
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],

            )
        ]
    )
    candles.update_layout(height=500, template='plotly_dark')

    # vol stats
    current_vol = df.iloc[-1]['close']  # the last row (current candle) updates when fresh data is pulled

    # IV Rank
    year_min = df['low'].min()
    year_max = df['high'].max()
    iv_rank = (current_vol - year_min) / (year_max - year_min) * 100

    # IV percentile
    total_periods = len(df)
    periods_lower = len(df[(df['close'] <= current_vol)])
    iv_percentile = (periods_lower / total_periods) * 100

    return candles, iv_rank, iv_percentile


candles, iv_rank, iv_percentile = get_data()

# create dash app
app = dash.Dash(title="IV Rank", external_stylesheets=[dbc.themes.DARKLY])

# app layout
app.layout = html.Div(children=[
    # refresh button
    dbc.Row([
        html.Div([
            dbc.Button(
                html.B("Refresh"),
                color="info",
                id="refresh_button",
                className="mb-3",
            ),
        ])
    ], style={'margin': 'auto', 'margin-top': '1rem'}),
    # the DVOL Chart
    dbc.Row([
        html.Div(
            dcc.Graph(id='dvol_candles', figure=candles),
            style={'margin': 'auto', 'max-width': '1600px'})
    ]),
    # Gauges
    dbc.Row([
        dbc.Col([
            daq.Gauge(
                id='iv_rank_gauge',
                color="#00cfbe",
                showCurrentValue=True,
                min=0,
                max=100,
                label={'label': 'IV Rank', 'style': {'font-size': '30px'}},
                scale={'custom': {
                    '0': {'label': '0', 'style': {'font-size': '20px'}},
                    '20': {'label': '20', 'style': {'font-size': '20px'}},
                    '40': {'label': '40', 'style': {'font-size': '20px'}},
                    '60': {'label': '60', 'style': {'font-size': '20px'}},
                    '80': {'label': '80', 'style': {'font-size': '20px'}},
                    '100': {'label': '100', 'style': {'font-size': '20px'}},
                }},
                value=iv_rank,
                size=300,
            ),
            html.Div(
                dbc.Label("IV Rank shows where the current IV level sits within the range of IV in the last year. IV as measured by DVOL."),
                style={'margin': 'auto', 'max-width': '400px'}
            )
        ]),
        dbc.Col([
            daq.Gauge(
                id='iv_percentile_gauge',
                color="#00cfbe",
                showCurrentValue=True,
                min=0,
                max=100,
                label={'label': 'IV Percentile', 'style': {'font-size': '30px'}},
                scale={'custom': {
                    '0': {'label': '0', 'style': {'font-size': '20px'}},
                    '20': {'label': '20', 'style': {'font-size': '20px'}},
                    '40': {'label': '40', 'style': {'font-size': '20px'}},
                    '60': {'label': '60', 'style': {'font-size': '20px'}},
                    '80': {'label': '80', 'style': {'font-size': '20px'}},
                    '100': {'label': '100', 'style': {'font-size': '20px'}},
                }},
                value=iv_percentile,
                size=300,
            ),
            html.Div(
                dbc.Label("IV Percentile shows what percentage of time (in the last year) IV has been lower than the current level. IV as measured by DVOL."),
                style={'margin': 'auto', 'max-width': '400px'}
            )
        ])
    ], style={'margin': 'auto'}),

], style={'margin': 'auto', 'max-width': '1600px'})


@app.callback(
    [
        Output('dvol_candles', 'figure'),
        Output('iv_rank_gauge', 'value'),
        Output('iv_percentile_gauge', 'value'),
    ],
    Input('refresh_button', 'n_clicks'),
)
def refresh_data(n_clicks):
    print(n_clicks)

    candles, iv_rank, iv_percentile = get_data()

    return candles, iv_rank, iv_percentile


# run local server
if __name__ == '__main__':
    app.run_server(debug=True)
