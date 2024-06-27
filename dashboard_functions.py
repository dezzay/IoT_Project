import pandas as pd
import plotly.graph_objects as go

# Annahme: season_data und df_vanilla sind bereits definierte DataFrames

def seite1_figure1(df_hourly,metric):

    colors = {'CO2' : 'blue', 'VOC' : 'green', 'Temperature' : 'orange', 'Humidity' : 'red'}
    metrics = {'CO2' : 'CO2', 'VOC' : 'VOC', 'Temperature' : 'tmp', 'Humidity' : 'hum'}

    # Create the line plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_hourly['date_time'],
        y=df_hourly[metrics[metric]],
        mode='lines',
        line=dict(color=colors[metric]),
        name=f'Average {metric} Level'
    ))

    # Update layout with title and labels
    fig.update_layout(
        title=f'Average {metric} Levels per Hour',
        xaxis_title='Hour',
        yaxis_title=f'Average {metric} Level'
    )
    return fig

def seite1_figure2(room_value_counts):
    # Create the bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=room_value_counts.index,
        y=room_value_counts['datapoints'],
        text=room_value_counts['datapoints'],               # Text to display on the bars
        textposition='outside',          # Position the text on top of the bars
        marker_color='#64378C',
        textfont=dict(
            family='Arial',      # Font family
            size=15,             # Font size
            color='black',       # Font color
            weight='bold'        # Font weight (bold)
        )
    ))
    # Customize the layout
    fig.update_layout(
        title='Room Value Counts',
        xaxis_title='Room',
        yaxis_title='Count',
        yaxis=dict(
            range=[0, 150000] 
        ) 
    )

    # Return the bar chart
    return fig

def seite1_figure3(dataframe):
    df_ampel = dataframe.copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_ampel.room_number,y=df_ampel.red_yellow_rate, name="yellow", marker_color="orange"))
    fig.add_trace(go.Bar(x=df_ampel.room_number,y=df_ampel.red_rate, name="red", marker_color="red"))
    fig.add_trace(go.Bar(x=df_ampel.room_number,y=df_ampel.red_blinking_rate, name="red_blinking", marker_color="black"))
    fig.update_layout(barmode="stack")
    fig.update_layout(
        title='Räume nach Ampelfarbe "gelb" sortiert',
        xaxis_title='Raum',
        yaxis_title='Rate',
        showlegend=True,
        
    )
    return fig

def seite2_figure1(season_data, df_vanilla, room):
    # Filterdaten basierend auf dem Raum
    data1 = season_data[season_data['room_number'] == room][["Vanilla Predictions",'date_time']].copy()
    data2 = df_vanilla[df_vanilla['room_number'] == room][["tmp",'date_time']].copy()

    # Erstellen der Trainings- und Vorhersage-Datenframes
    test_len = int(len(data2) * 0.8 + 1)
    test = data2.iloc[:test_len]
    df_pred = data1
    df_pred.index = range(test_len, test_len + len(data1))
    
    df_real = pd.concat([test.reset_index(drop=True), df_pred.rename(columns={"Vanilla Predictions": "tmp"})])

    # Erstellen der Figur
    fig = go.Figure()

    # Hinzufügen der realen Daten-Spur
    fig.add_trace(go.Scatter(x=df_real['date_time'], y=df_real['tmp'], mode='lines', name='Real', line=dict(color='red')))

    # Hinzufügen der vorhergesagten Daten-Spur
    fig.add_trace(go.Scatter(x=df_pred['date_time'], y=df_pred['Vanilla Predictions'], mode='lines', name='Predicted', line=dict(color='blue')))

    # Hinzufügen der vertikalen Linie zur Trennung von Trainings- und Vorhersagedaten
    cutoff_date = df_real['date_time'].iloc[test_len]
    y_min = min(df_real['tmp'].min(), df_pred['Vanilla Predictions'].min()) - 1
    y_max = max(df_real['tmp'].max(), df_pred['Vanilla Predictions'].max()) + 1
    
    fig.add_shape(
        type="line",
        x0=cutoff_date,
        y0=y_min,
        x1=cutoff_date,
        y1=y_max,
        line=dict(color="black", width=3, dash="dash")
    )

    # Aktualisieren des Layouts
    fig.update_layout(
        title='Temperature True Value and Prediction',
        xaxis_title='Index',
        yaxis_title='Temperature',
        showlegend=True
    )

    return fig

def seite2_figure2(season_data, views, floor, room):
    bedingung1 = season_data['Etage'] == floor
    bedingung2 = season_data['room_number'] == room
    data = season_data[bedingung1 & bedingung2].copy().reset_index(drop=True)

    fig = go.Figure()

    if not views or 'Everything' in views:
        views_to_plot = ['Vanilla True Values', 'Vanilla Predictions', 'Seasons Predictions', 'Weather Predictions', 'Combined Predictions']
    else:
        views_to_plot = views

    for view in views_to_plot:
        fig.add_trace(go.Scatter(x=data['date_time'], y=data[view], mode='lines', name=view))

    fig.update_layout(
        title='Vorhersage der Temperatur t+1 mit und ohne Wetter/Jahreszeiten',
        xaxis_title='Index',
        yaxis_title='Values',
        showlegend=False
    )
    return fig

