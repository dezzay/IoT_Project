# IoT_Project für das E-Gebäude
## Inhaltsverzeichnis
1. [Datenanalyse](#datenanalyse)
2. [Preprocessing](#preprocessing)
3. [Feature Engineering](#feature_engineering)
4. [Forecast](#forecast)
   - [Forecast abhängig von Wetter/Jahreszeit](#forecast_mit_Abhänigkeiten)
   - [Verbesserung des Forecasts](#forecast_pro_Etage)
5. [Dashboard](#dashboard)








### Feature Engineering
Um die Sensor Daten für den Forecast vorzubereiten wird `feature_engineering.py` eine Klasse `FeatureEngineering` verwendet, um verschiedene Schritte des Feature Engineerings auf einem DataFrame durchzuführen. Die Klasse dient insbesondere als `helper class` in den Notebooks, um den Code übersichtlich zu gestalten. Des weiteren wird eine Klasse `WeatherFetcher` verwendet, um mit der API meteostat Wetterdaten abzurufen.
