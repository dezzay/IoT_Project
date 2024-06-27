import pandas as pd
import numpy as np
from datetime import datetime
from meteostat import Point, Hourly
from sklearn.preprocessing import OneHotEncoder



class FeatureEngineering:
    def __init__(self, df):
        self.df = df
        self.filtered_dataframes = None

    def feature_engineering(self, n):
        """
        Overall method to perform feature engineering.

        """
        self.add_season_column()
        self.create_shifts(n)
        self.cyclical_encoding()
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
                            'CO2',
                            'VOC', 
                            'vis', 
                            'IR', 
                            'BLE',
                            'snr',
                            'color',
                            'rssi',
                            'building_name',
                            'year', 
                            'month', 
                            'dayofweek',
                            'hour',
                            'tmp_diff_per_sec',
                            'time_diff_sec', 
                            ], inplace=True)
    @staticmethod
    def onehotencoding(df, categorical_features:list):
        """
        Performs one-hot encoding on specified categorical features of a DataFrame.

        Parameters:
        df (pd.DataFrame): The input DataFrame.
        categorical_features (list of str): List of column names to be one-hot encoded.

        Returns:
        pd.DataFrame: DataFrame with one-hot encoded columns.
        """
        df_encoded = df.copy()
    
        for feature in categorical_features:
            encoder = OneHotEncoder(sparse_output=False)
            one_hot_encoded = encoder.fit_transform(df_encoded[[feature]])
            encoded_columns = encoder.get_feature_names_out([feature])
            df_one_hot = pd.DataFrame(one_hot_encoded, columns=encoded_columns, index=df_encoded.index)
            
            # Concatenate the original DataFrame with the one-hot encoded DataFrame
            df_encoded = pd.concat([df_encoded, df_one_hot], axis=1)


        return df_encoded

    def get_season(self, date):
        """
        Get season dependent on date
        """
        year = date.year
        seasons = {
            'winter': (pd.Timestamp(f'{year}-12-21'), pd.Timestamp(f'{year+1}-03-20')),
            'spring': (pd.Timestamp(f'{year}-03-21'), pd.Timestamp(f'{year}-06-20')),
            'summer': (pd.Timestamp(f'{year}-06-21'), pd.Timestamp(f'{year}-09-22')),
            'autumn': (pd.Timestamp(f'{year}-09-23'), pd.Timestamp(f'{year}-12-20'))
        }

        for season, (start, end) in seasons.items():
            if start <= date <= end:
                return season

        # Special case for dates in winter spanning across the year boundary
        if date >= pd.Timestamp(f'{year}-12-21') or date <= pd.Timestamp(f'{year+1}-03-20'):
            return 'winter'

    def add_season_column(self):
        """
        Add a season column to the DataFrame based on the date_time column
        """
        self.df['season'] = self.df['date_time'].apply(self.get_season)
        return self.df
    
    def filter_rooms_by_prefix(self):
        """
        Filters the DataFrame based on the start of the room_number column.

        Returns:
            dict: A dictionary of DataFrames where keys are room number prefixes and values are filtered DataFrames.
        """
        if self.filtered_dataframes is None:
            self.filtered_dataframes = {}

            # Extract unique prefixes from room_number column
            prefixes = self.df['room_number'].str.extract(r'^(e\d|eu)').dropna().squeeze().unique()

            # Filter DataFrame for each prefix and store in dictionary
            for prefix in prefixes:
                self.filtered_dataframes[prefix] = self.df[self.df['room_number'].str.startswith(prefix)]

        return self.filtered_dataframes

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
    

    
                
    

    
        
