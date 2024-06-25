import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
from dashboard_functions import *

# Daten - Seite 1
df_hourly = pd.read_csv(r'Dashboard\hourly_data.csv')

# Daten - Seite 2

season_data = pd.read_csv(r'Dashboard\predictions.csv') 

df_vanilla = pd.read_csv(r'Dashboard\df_vanilla.csv')

# Daten - Seite 3


# Beispielhafte Daten

data_scatter = {
    'x': [1, 2, 3, 4, 5],
    'y': [2, 1, 3, 5, 4]
}

# Figures - Seite 1
last_selected_metric_seite1_fig1 = 'CO2'  # Startwert, wenn nichts ausgewählt ist

seite1_fig1 = seite1_figure1(df_hourly,last_selected_metric_seite1_fig1)

# Figures - Seite 2
last_selected_floor_seite2 = 'Etage EU'
last_selected_room_seite2 = 'eu02'

# Figure 1
seite2_fig1 = seite2_figure1(season_data,df_vanilla,last_selected_room_seite2)


# Figure 2

seite2_fig2 = seite2_figure2(season_data,['Everything'],last_selected_floor_seite2,last_selected_room_seite2)

# Dashboard App erstellen
app = Dash(__name__)


# Layout des Dashboards
app.layout = html.Div([
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Explorative Datenanalyse', children=[
            html.Br(),
        dcc.Dropdown(
        id='averages_dropdown', 
        options=[
            {'label': 'CO2', 'value': 'CO2'},
            {'label': 'VOC', 'value': 'VOC'},
            {'label': 'Temperature', 'value': 'Temperature'},
            {'label': 'Humidity', 'value': 'Humidity'}
        ], 
        value=last_selected_metric_seite1_fig1
    ),
    html.Br(),
            dcc.Graph(
                id='line-chart',
                figure=seite1_fig1
            )
        ]),
        dcc.Tab(label='ML-Predictions', children=[
            html.Br(),
            html.Br(),
        dcc.Dropdown(
        id='floors_dropdown',
        options=[{'label':'Etage EU','value':'Etage EU'},
                 {'label':'Etage 0','value':'Etage 0'},
                 {'label':'Etage 1','value':'Etage 1'},
                 {'label':'Etage 2','value':'Etage 2'},
                 {'label':'Etage 3','value':'Etage 3'},
                 ],
        value=last_selected_floor_seite2
    ),
    html.Br(),
        dcc.Dropdown(
        id='rooms_dropdown',
        options=[room_choice for room_choice in season_data[season_data['Etage'] == last_selected_room_seite2]['room_number'].unique()],
        value=last_selected_room_seite2
    ),
            html.Br(),
            dcc.Graph(
                        id='smile-chart',
                        figure=seite2_fig1  # Pass the entire Figure object directly here
                    ),
            html.Br(),
        dcc.Dropdown(id='predictions_dropdown',
                     options=['Everything', 'Vanilla True Values', 'Vanilla Predictions', 'Seasons Predictions', 'Weather Predictions', 'Combined Predictions'],
                     value=['Everything'],
                     multi=True),

    html.Br(),
            dcc.Graph(
    id='bar-chart',
    figure=seite2_fig2  # Pass the entire Figure object directly here
)

        ]),
        dcc.Tab(label='Sonderfälle', children=[
            dcc.Graph(
                id='scatter-chart',
                figure={
                    'data': [
                        go.Scatter(x=data_scatter['x'], y=data_scatter['y'], mode='markers', name='Streudiagramm')
                    ],
                    'layout': go.Layout(title='Streudiagramm')
                }
            )
        ])
    ])
])

@callback(
    Output('line-chart', 'figure'),
    Input('averages_dropdown', 'value'),
    )
def update_graph_seite1_fig1(metric):
    
    global last_selected_metric_seite1_fig1

    if metric is None:
        metric = last_selected_metric_seite1_fig1

    last_selected_metric_seite1_fig1 = metric

    fig = seite1_figure1(df_hourly,metric)
    return fig


@callback(
    Output('rooms_dropdown', 'options'),
    Output('rooms_dropdown', 'value'),
    Input('floors_dropdown', 'value'),
    Input('rooms_dropdown', 'value'),
)
def update_dropdowns_seite2(floor,room):
    
    bedingung1 = season_data['Etage'] == floor
    
    options=[room_choice for room_choice in season_data[bedingung1]['room_number'].unique()]

    if last_selected_floor_seite2 != floor:
        room = options[0]

    value = room
    return options,value

@callback(
    Output('smile-chart', 'figure'),
    Input('floors_dropdown', 'value'),
    Input('rooms_dropdown', 'value'),
)
def update_graph_seite2_fig1(floor,room):
    global last_selected_floor_seite2
    global last_selected_room_seite2

    if floor == None:
        floor = last_selected_floor_seite2
    if room == None:
        room = last_selected_room_seite2


    fig = seite2_figure1(season_data,df_vanilla,room)

    return fig

@callback(
    Output('bar-chart', 'figure'),
    Input('predictions_dropdown', 'value'),
    Input('floors_dropdown', 'value'),
    Input('rooms_dropdown', 'value'),
)
def update_graph_seite2_fig2(views,floor,room):

    global last_selected_floor_seite2
    global last_selected_room_seite2

    if floor == None:
        floor = last_selected_floor_seite2
    if room == None:
        room = last_selected_room_seite2
    
    last_selected_floor_seite2 = floor
    last_selected_room_seite2 = room 

    fig = seite2_figure2(season_data,views,floor,room)

    return fig

# Server starten
if __name__ == '__main__':
    app.run_server(debug=True)
