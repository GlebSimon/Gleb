import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import requests
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime
import dash_bootstrap_components as dbc

# Define API endpoint
base_url = 'https://api.coincap.io/v2/'

app = dash.Dash(__name__)

# Define layout
sidebar = html.Div([

    html.H1('Crypto Historical Data'),
    html.Div([
        html.Label('Select an asset'),
        dcc.Dropdown(
            id='asset-dropdown',
            options=[],
            value=None,
            style={'max-width': '70%','margin-top':'10px'}
        ) ]),
        dbc.Row([dbc.Col(
        html.Div([
            html.Div('Date from', style={'margin-top': '10px'}),
            html.Div(
                dcc.DatePickerSingle(
                    id='date-from-picker',
                    min_date_allowed=datetime(2013, 4, 28),
                    max_date_allowed=datetime.now(),
                    initial_visible_month=datetime.now(),
                    date=datetime.now().replace(year=datetime.now().year - 1),
                    style={'margin-top': '10px'}
                ),
                style={'display' : 'flex', 'flex-direction': 'column', 'align-items': 'left'}
            )
        ]),width=2)
    , dbc.Col(
    html.Div([
        html.Div('Date to', style={'margin-top': '10px'}),
        html.Div(
            dcc.DatePickerSingle(
                id='date-to-picker',
                min_date_allowed=datetime(2013, 4, 28),
                max_date_allowed=datetime.now(),
                initial_visible_month=datetime.now(),
                date=datetime.now(),
                style={'margin-top': '10px'}
            ),
            style={'display' : 'flex', 'flex-direction': 'column', 'align-items': 'right'}
        )
    ]),width=2) ])

],  style={"position": "fixed", "top": 0, "left": 0, "bottom": 0,
    'width': '33%', "padding": "4rem 1rem", "background-color": "#F8F9FA"})



content = html.Div([

    dcc.Graph(id='closing-price-graph',style={"margin-left": "40rem", "margin-right": "2rem",
    "padding": "2rem 1rem", "display": "inline-block",'height': '38rem','width': '67%'})

])

app.layout = html.Div([sidebar, content], style={'width': '100%'})

@app.callback(Output('asset-dropdown', 'options'),
              [Input('asset-dropdown', 'search_value')])
def update_asset_options(search_value):
    url = f'{base_url}assets'
    response = requests.get(url)
    data = response.json()['data']
    options = [{'label': asset['name'], 'value': asset['id']} for asset in data]
    if search_value:
        options = [option for option in options if search_value.lower() in option['label'].lower()]
    return options


@app.callback(Output('closing-price-graph', 'figure'),
              [Input('asset-dropdown', 'value'),
               Input('date-from-picker', 'date'),
               Input('date-to-picker', 'date')])
def update_graph(selected_asset, start_date, end_date):
    # Format start and end dates
    start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')

    # Make API request for historical data
    url = f'{base_url}assets/{selected_asset}/history?interval=d1&start={start_date.timestamp() * 1000}&end={end_date.timestamp() * 1000}'
    response = requests.get(url)

    # Convert response to pandas dataframe
    df = pd.DataFrame(response.json()['data'], columns=['time', 'priceUsd'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    # Create line chart of closing prices
    fig = {
        'data': [{'x': df['time'], 'y': df['priceUsd'], 'type': 'bar'}],
         'layout': {'title': f'Closing Price for {selected_asset.capitalize()}'}
    }

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)



