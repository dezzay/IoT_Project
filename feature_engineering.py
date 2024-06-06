import pandas as pd
import numpy as np
from datetime import datetime
from meteostat import Point, Hourly

"""
Attributsbeschreibung:

date_time := Datum (Format: YYYY-MM-DD HH:MM:SS)
device_id := CO2-Ampel-ID
tmp := Durchschnittliche Temperatur
hum := Durchschnittliche Luftfeuchtigkeit
CO2 := Durchschnittlicher CO2-Wert
VOC := Durchschnittliche Schadstoffbelastung
vis := Durchschnittlicher Lichtwert
IR := Durchschnittlicher Infrarotwert
WIFI := Durchschnittliche Anzahl an WiFi-Geräten
BLE := Durchschnittliche Anzahl an Bluetoothgeräten
rssi := received signal strength indication, Empfangsfeldstärke kabelloser Kommunikationsanwendungen
channel_rssi := Gesamtstärke des ganzen Empfangs
snr := Signal-Rausch-Verhältnis
gateway := Genutztes Gateway für die Übertragung des Datenpunktes
channel_index :=
spreading_factor :=
bandwidth :=
f_cnt :=
building_name := Name des Gebäudes, in dem sich die CO2-Ampel befindet 
"""

class FeatureEngineering:
    def __init__(self, df):
        self.df = df

    def feature_engineering(self, n, categorical_features):
        """
        Overall method to perform feature engineering.

        """
        self.create_shifts(n)
        self.cyclical_encoding()
        self.onehotencoding(categorical_features)
        self.delete_columns()

        return self.df.dropna()

    def cyclical_encoding(self):
        # Cyclical encoding for hour of the day
        self.df['hour_sin'] = np.sin(2 * np.pi * self.df['hour'] / 24)
        self.df['hour_cos'] = np.cos(2 * np.pi * self.df['hour'] / 24)

        # Cyclical encoding for day of the week
        self.df['day_of_week_sin'] = np.sin(2 * np.pi * self.df['dayofweek'] / 7)
        self.df['day_of_week_cos'] = np.cos(2 * np.pi * self.df['dayofweek'] / 7)

        # Cyclical encoding for month
        self.df['month_sin'] = np.sin(2 * np.pi * self.df['month'] / 12)
        self.df['month_cos'] = np.cos(2 * np.pi * self.df['month'] / 12)

        return self.df

    def create_shifts(self, n):
        for i in range(1, n+1):
            self.df[f"tmp-{i}"] = self.df['tmp'].shift(i)

        return self.df

    def delete_columns(self):
        """
        Drop columns that are not in use to predict the temperature.
        """

        self.df.drop(columns=[ 
                            'BLE', 
                            'snr', 
                            'rssi',
                            'IR',
                            'VOC',
                            'VOC_diff',
                            'IR_diff',
                            'IR_diff',                                                                                    
                            'BLE_diff',
                            'building_name',
                            'CO2_diff_per_sec', 
                            'VOC_diff_per_sec', 
                            'tmp_diff_per_sec',
                            'hum_diff_per_sec', 
                            'IR_diff_per_sec',
                            'time_diff_sec', 
                            'vis_diff_per_sec'], inplace=True)
    
    def onehotencoding(self, categorical_features:list):
        """
        One-hot-encoding for categorical features e.g room_number.
        """
        for feature in categorical_features:
            ohe_df = pd.get_dummies(self.df[f"{feature}"], prefix = f"{feature}", dtype="int")
            self.df = pd.concat([self.df, ohe_df], axis = 1)
            self.df = self.df.drop(columns = [f"{feature}"], axis = 1)

        return self.df

class WeatherFetcher:
    """
    Class to fetch weather api and combine it with the CO2-Ampeldaten data
    """
    def __init__(self, latitude, longitude, start_date, end_date):
        self.location = Point(latitude, longitude)
        self.start_date = start_date
        self.end_date = end_date
        self.weather = pd.DataFrame()

    def get_weather(self):
        """
        Fetch weather data and store it in the weather DataFrame.
        """
        data = Hourly(self.location, self.start_date, self.end_date)
        data = data.fetch()
        self.weather = pd.DataFrame(data)
        
        return self.weather

    def merge_dataframes(self, other_df):
        """
        Merge the weather data with another DataFrame on the date_time column.
        
        Parameters:
            other_df (pd.DataFrame): The other DataFrame to merge with.
            
        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        other_df['date_time'] = pd.to_datetime(other_df['date_time'])
        merged_df = pd.merge(other_df, self.weather, left_on='date_time', right_on='time', how='inner')
        return merged_df

    def combine_weather(self, other_df):
        """
        Fetch weather data and merge it with another DataFrame.
        
        Parameters:
            other_df (pd.DataFrame): The other DataFrame to merge with.
            
        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        self.get_weather()
        return self.merge_dataframes(other_df)
    

    
                
    

    
        
