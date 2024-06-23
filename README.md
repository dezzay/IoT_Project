# IoT_Project für das E-Gebäude
## Inhaltsverzeichnis
1. [Datenanalyse](#datenanalyse)
2. [Preprocessing](#preprocessing)
3. [Feature Engineering](#feature-engineering)
4. [Forecast](#forecast)
   - [Forecast abhängig von Wetter/Jahreszeit](#forecast-abhängig-von-wetter/jahreszeit)
   - [Verbesserung des Forecasts](#verbesserung-des-forecasts)
5. [Dashboard](#dashboard)








### Feature Engineering
Um die Sensor Daten für den Forecast vorzubereiten wird in der Datei `feature_engineering.py` eine Klasse `FeatureEngineering` verwendet, um verschiedene Schritte des Feature Engineerings auf einem DataFrame durchzuführen. Die Klasse dient insbesondere als `helper class` in den Notebooks, um den Code übersichtlich zu gestalten. Des weiteren wird eine Klasse `WeatherFetcher` verwendet, um mit der API meteostat Wetterdaten abzurufen.

### Forecast
In dem Forecast wird mit Hilfe eines LSTMs das Feature `tmp (Temperatur)` vorhergesagt. Um die Daten in geeignetes Format für den Forecast zu transformieren wurde die `sliding window` Methode verwendet. Dabei wurde ein `feature lag = 2` verwendet sprich, mit t-1 und t wurde die Temperatur für t+1 vorhergesagt. Die Modelle wurden auf Grund der langen Trainingszeit in dem Ordner `trained_models` gespeichert.

#### Forecast abhängig von Wetter/Jahreszeit
In der Datei `forecast with weather_seasons.ipynb` wurde untersucht, welche Auswirkungen das Wetter und die Jahreszeiten auf den Forecast haben.

#### Verbesserung des Forecasts
Die Idee lag hierbei, die Daten nach Etagen des Gebäudes zu unterteilen und für `jede Etage ein eigenes Modell zu trainieren.` In der Tat wurden die Modelle durch diese Unterscheidung besser. Grund hierfür ist vorallem die Dimensionsreduktion des Datensatzes, der ohne hin schon komplexer war, da wir jeden Raum one-hot-encoded haben. Die verbesserten Modelle sind in der Datei ´forecast.ipynb´ zu finden.

