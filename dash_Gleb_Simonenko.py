import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# Read in data
df = pd.read_csv('games.csv')
df = df[df['Year_of_Release'] >= 2000].dropna()
# Convert year column to datetime
df['Year_of_Release'] = df['Year_of_Release'].apply(lambda x: str(x))
# Extract the year value from the date string and convert to float
df['Year_of_Release'] = df['Year_of_Release'].apply(lambda x: float(x[:4]))



# Group data by year and platform and count number of games
grouped_df = df.groupby(['Year_of_Release', 'Platform'])['Name'].count().reset_index(name='Count')

# Create stacked area plot
fig = go.Figure()

for platform in grouped_df['Platform'].unique():
    platform_df = grouped_df[grouped_df['Platform'] == platform]
    fig.add_trace(go.Scatter(
        x=platform_df['Year_of_Release'],
        y=platform_df['Count'],
        mode='lines',
        stackgroup='one',
        name=platform
    ))

# Add title and axis labels
fig.update_layout(
    title='Game Releases by Year and Platform',
    xaxis_title='Year',
    yaxis_title='Number of Games Released'
)

# Create scatter plot
fig2 = px.scatter(df, x='User_Score', y='Critic_Score', color='Genre')
fig2.update_layout(
    title='User Ratings vs. Critic Ratings by Genre',
    xaxis_title='User Rating',
    yaxis_title='Critic Rating'
)

# Create Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define app layout
app.layout = html.Div([
    html.H1("Games Market Dashboard", style={'margin-left': '20px'}),
    html.P("This dashboard provides an interactive analysis of the gaming industry,\nallowing users to explore game releases by platform and genre, "
"as well as player and critic scores. "
"Users can also filter by age rating, release year, and select multiple genres.", style={'margin-left': '20px','color': '#808080'}),

    # Filter 1: Genre filter
    dbc.Row([dbc.Col(
    html.Div([
        html.Label("Filter by Genre", style={'margin-left': '20px'}),
        dcc.Dropdown(
            id='genre-filter',
            options=[{'label': i, 'value': i} for i in df['Genre'].unique()],
            value=[],
            style={'paddingLeft': '20px'},
            multi=True
        )
    ]) ,width=6),
           dbc.Col(
    # Filter 2: Ratings filter
    html.Div([
        html.Label("Filter by Ratings"),
        dcc.Dropdown(
            id='ratings-filter',
            options=[{'label': i, 'value': i} for i in df['Rating'].unique()],
            value=[],
            style={'paddingLeft': '20px'},
            multi=True
        )
    ]),width=6)
    ])    ,
# Interactive text 1: Number of selected games
    html.Div([
        html.Div([
            html.H3(id='game-count', children='', style={'margin-left': '20px','margin-top': '20px'})
        ], className='six columns'),
    ]),

    dbc.Row([dbc.Col(dcc.Graph(id='game-releases', figure=fig, style={'height': '38rem'}),width=6),
    dbc.Col(dcc.Graph(id='genre-scatter-plot', figure=fig2, style={'height': '38rem'}),width=6)
    ]),
# Filter 3: Interval of release years
    html.Div([
        html.Label("Filter by Release Year", style={'margin-left': '20px'}),
        dcc.RangeSlider(
            id='year-slider',
            min=df['Year_of_Release'].min(),
            max=df['Year_of_Release'].max(),
            value=[df['Year_of_Release'].min(), df['Year_of_Release'].max()],
            marks={str(year): str(year) for year in df['Year_of_Release'].unique()},
            step=None
        ),
    html.Div(
        children=[html.Div(int(year), style={'flex': '1'}) for year in sorted(df['Year_of_Release'].unique())],
        style={'display': 'flex', 'margin-left': '15px', 'justify-content': 'space-around', 'margin-right': '20px', 'font-size': 14, 'width': str(len(df['Year_of_Release'].unique()) * 116.5) + 'px'}
    )

    ])
])


# Callback for the number of selected games text
@app.callback(
    Output('game-count', 'children'),
    [Input('genre-filter', 'value'),
     Input('ratings-filter', 'value'),
     Input('year-slider', 'value')])

def update_game_count(genre, rating, year):
    filtered_data = df[(df['Genre'].isin(genre)) & (df['Rating'].isin(rating)) &
                         (df['Year_of_Release'] >= year[0]) & (df['Year_of_Release'] <= year[1])]
    count = len(filtered_data)
    return f'Number of selected games: {count}'

# Define callback function for stacked area plot
@app.callback(Output('game-releases', 'figure'),
              [Input('genre-filter', 'value'),
               Input('ratings-filter', 'value'),
               Input('year-slider', 'value')])

def update_game_releases(genres, ratings,year):
    filtered_games = df[(df['Genre'].isin(genres)) & (df['Rating'].isin(ratings)) &
                        (df['Year_of_Release'] >= year[0]) & (df['Year_of_Release'] <= year[1])]
    year_platform_counts = filtered_games.groupby(['Year_of_Release', 'Platform'])['Name'].count().reset_index().rename(columns={'Name':'Count'})
    fig = px.area(year_platform_counts, x='Year_of_Release', y='Count', color='Platform',
                  title='Game Releases by Year and Platform')
    fig.update_layout(transition_duration=500)
    return fig

# Define callback function for scatter plot
@app.callback(
    Output('genre-scatter-plot', 'figure'),
    [Input('genre-filter', 'value'),
     Input('ratings-filter', 'value'),
     Input('year-slider', 'value')])

def update_genre_scatter(genres, ratings,year):
    df['User_Score'] = pd.to_numeric(df['User_Score'], errors='coerce')
    df.loc[df['User_Score'].isna(), 'User_Score'] = 'tdb'
    filtered_df = df[(df['Genre'].isin(genres)) & (df['Rating'].isin(ratings)) &
                        (df['Year_of_Release'] >= year[0]) & (df['Year_of_Release'] <= year[1])]
    fig = px.scatter(filtered_df, x='User_Score', y='Critic_Score', color='Genre',
                     title='Scatter Plot of User Scores vs Critic Scores by Genre')
    fig.update_layout(
        xaxis_title='User Rating',
        yaxis_title='Critic Rating'
    )
    fig.update_traces(marker={'size': 10})
    return fig


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
