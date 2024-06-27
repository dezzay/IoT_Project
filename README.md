# IoT_Projekt für das E-Gebäude
Das Ziel des Projekts ist es die gegebenen Zeitreihendaten der CO2-Ampeln zu verstehen und sie zu analysieren, um Besonderheiten und Beziehungen in den Daten zu finden.
Zusätzlich zur Analyse wurde ein Forecast implementiert, um die Temperatur in dem jeweiligen Raum zu vorhersagen.
Letzteres wrude ein Dashboard entwickelt, um die Ergebnisse zu visualisieren.


## Inhaltsverzeichnis
1. [Datenanalyse](#datenanalyse)
2. [Preprocessing](#preprocessing)
3. [Feature Engineering](#feature-engineering)
4. [Forecast](#forecast)
   - [Verbesserung des Forecasts](#verbesserung-des-forecasts)
5. [Dashboard](#dashboard)







### Datenanalyse
Ziel der Analyse ist das Verstehen der Daten und auftretender Anomalien,Ausreißer,Correlation und Verhalten der Daten.

### Preprocessing
Im Preprocessing bereinigen wir die Daten und samplen sie mit einem Rolling Window um sie für die Analyse und das ML Modell zu nutzen.

### Feature Engineering
Um die Sensor Daten für den Forecast vorzubereiten wird in der Datei `feature_engineering.py` eine Klasse `FeatureEngineering` verwendet, um verschiedene Schritte des Feature Engineerings auf einem DataFrame durchzuführen. Die Klasse dient insbesondere als `helper class` in den Notebooks, um den Code übersichtlich zu gestalten. Nennenswert ist hierbei das Cycling encoding der Zeitkomponenten, die einen besseren Input für deep learning Modelle abbilden. Des weiteren wird eine Klasse `WeatherFetcher` verwendet, um mit der API meteostat Wetterdaten abzurufen.

### Forecast
In dem Forecast wird mit Hilfe eines BI-LSTMs das Feature `tmp (Temperatur)` vorhergesagt. Um die Daten in geeignetes Format für den Forecast zu transformieren wurde die `sliding window` Methode verwendet. Dabei wurde ein `feature lag = 2` verwendet sprich, mit t-1 und t wurde die Temperatur für t+1 vorhergesagt. Die Modelle wurden auf Grund der langen Trainingszeit in dem Ordner `trained_models` gespeichert.


#### Verbesserung des Forecasts
Die Idee lag hierbei, die Daten so zu splitten, das wir für jeden Raum im Gebäude trainings/testendaten haben. Dafür wurde eine `Funktion` implementiert, die es ermöglicht die letzten 20% von jeden Raum als Testdaten zu verwenden. Die Nodelle wurden in der Tat durch diese Unterscheidung besser. Modelle sind in der Datei ´forecast.ipynb´ zu finden.

### Dashboard
Das Dashboard befindet sich in der Datei `dashboard.py`, welches mit Plotly Dash erstellt wurde. Ingesamt gibt es zwei Seiten: [Datenanalyse, ML-Predictions] In der Datei ´dashboard_functions.py` ist der Code für die Plots in Plotly.GO implementiert.



