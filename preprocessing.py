import os, io
import pandas as pd
import tarfile, zipfile
import numpy as np
from sklearn.ensemble import IsolationForest
pd.options.mode.chained_assignment = None  # default='warn'

class DataExtractor:
    """Extrahiert den historischen CO2-Ampeldatensatz und erstellt ein DataFrame aus den vorliegenden Dateien"""
    def __init__(self, first_directory, new_directory):
        self.first_directory = first_directory
        self.new_directory = new_directory
    def create_df(self):
        """Erstellt ein pandas.DataFrame Objekt, indem .dat Dateien ausgelesen werden. Das Auslesen erfolgt normalerweise nach einem Extrahieren der zip-Ordner,
        da die historischen Dateien in diesem Format vorliegen. Das Auslesen kann aber auch bei entpackten Dateien erfolgen."""
        self.extract_zip_files(self.first_directory, self.new_directory)
        self.delete_zip_files(self.first_directory)
        self.df = self.get_data(self.new_directory)
        return self.df
    def extract_zip_files(self, directory, new_directory):
        """Extrahiert alle zip- und tar-Dateien im Parameterverzeichnis und seinen Unterverzeichnissen.
        
        Args:
            directory (str): Name des aktuellen Verzeichnisses mit allen zip-Dateien.
            new_directory (str): Name des Verzeichnisses, in das die Dateien extrahiert werden sollen.
        """
        for root, _, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.endswith(".zip"):
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(new_directory)
                            print(f"Extracted {file_name} in {new_directory}")
                    except zipfile.BadZipFile as e:
                        print(f"Failed to extract {file_name}: {e}")
                elif file_name.endswith(".tar") or file_name.endswith(".tar.gz") or file_name.endswith(".tgz") or file_name.endswith(".tar.bz2"):
                    try:
                        with tarfile.open(file_path, 'r') as tar_ref:
                            tar_ref.extractall(new_directory)
                            print(f"Extracted {file_name} in {new_directory}")
                    except tarfile.TarError as e:
                        print(f"Failed to extract {file_name}: {e}")
    def delete_zip_files(self, directory):
        """Löscht alle zip- und tar-Dateien in einem Verzeichnis und seinen Unterverzeichnissen.
        
        Args:
            directory (str): Name des Verzeichnisses, in dem die zip-Dateien gelöscht werden sollen.
        """
        for root, _, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.endswith((".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2")):
                    try:
                        os.remove(file_path)
                        print(f"File {file_name} has been deleted.")
                    except Exception as e:
                        print(f"Failed to delete {file_name}: {e}")
    def get_data(self, directory):
        """Liest alle extrahierten .dat-Dateien in einen Pandas DataFrame ein.
        
        Args:
            directory (str): Name des Verzeichnisses, aus dem die .dat-Dateien extrahiert werden sollen.
        Returns:
            df (pandas.DataFrame): ein DataFrame-Objekt, das die gelesenen Daten enthält.
        """
        dataframes = []
        for root, _, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    # Lese alle .dat Dateien aus, um ein DataFrame zu erstellen
                    df = pd.read_csv(file_path, delimiter=';', 
                                    header = 1, encoding='unicode_escape', on_bad_lines='skip')
                    dataframes.append(df)
                except Exception as e:
                    print(f"Failed to read {file_name} into DataFrame: {e}")
                    continue
        # Konkateniere alle DataFrames aus dem Listobjekt 'dataframes' in ein pandas.DataFrame Objekt
        if dataframes:
            print("Read data successfully.")
            final_df = pd.concat(dataframes, ignore_index=True)
            print(f"Data contains {final_df.shape[0]} data points and {final_df.shape[1]} columns.")
            return final_df
        else:
            print(f"No .dat files found in {self.new_directory}. \n Trying to extract files from the original directory {self.first_directory}")
            # Falls es keine Dateien zu extrahieren gab und kein neues Verzeichnis erstellt wurde, wird versucht, die Daten aus dem ursprünglichen ersten Verzeichnis zu lesen.
            try:
                return self.get_data(self.first_directory)
            except:
                print(f"No .dat files found in {self.first_directory}. Empty DataFrame returned.")
                return pd.DataFrame()
    
    
class DataPreprocessing:
    """Führt ein Preprocessing auf den CO2-Ampeldaten durch."""
    def __init__(self, get_outliers_out = True, roll:bool = True, date_time_column:str = "date_time"):
        """
        Args
            get_outliers_out (bool): Ausreißer entfernen, wenn True, sonst nicht.
            roll (bool): erstellt rolling windows für die Daten, wenn True, sonst nicht.
            date_time_column (str): der Spaltenname in den Daten, der die Datums- und Zeitinformationen enthält.
        """
        self.get_outliers_out = get_outliers_out
        self.roll = roll
        self.date_time_column = date_time_column
    def preprocess_df(self, df, rolling_window:str, sample_time:str = "60min"):
        """Allgemeine Methode zur Durchführung der Vorverarbeitungsschritte für einen gegebenen Datenrahmen df.
        Args
            df (pandas.DataFrame): ein gegebener DataFrame, der vorverarbeitet werden soll.
            rolling_window (str): die Größe des rollenden Fensters (z.B. '1s', '1min', '1h').
            sample_time (str): die Größe, die für das Resampling des DataFrame df verwendet wird. Das Resampling wird auf der Spalte, 
                               die in 'date_time_column' definiert wurde, durchgeführt.
        Rückgabe
            df (pandas.DataFrame): das vorverarbeitete DataFrame-Objekt.
        """
        try:
            # Räume wie N005 haben NaN-Werte für die ersten Einträge in den Spalten 'WIFI' und 'BLE'.
            df[["WIFI", "BLE"]].fillna(value = 0, inplace = True)
        except:
            pass
        df = self.drop_na_rows(df)
        df = self.convert_features(df)
        if self.get_outliers_out:
            df = self.remove_outliers(df)
        df = self.extract_room_and_building(df)
        df = self.remove_duplicates(df)
        df = self.remove_features(df)
        df = self.remove_invalid_values(df)
        df = self.create_rolling_windows(df, rolling_window = rolling_window, sample_time = sample_time)
        df = self.create_time_diff_features(df)
        df = self.create_average_differentials(df)
        df = self.create_new_features(df)
        df = self.fill_na(df)
        if self.date_time_column in df.columns:
            df = df.sort_values([self.date_time_column])
            # Setze Index zurück, der zu diesem Zeitpunkt aus normalen int-Werten besteht. Da vorhin Datenpunkte entfernt wurden, gab es
            # Lücken zwischen den Indexwerten (z.B. 1,3,7 etc. --> 1,2,3)
            df = df.reset_index(drop = True)
        else:
            # falls 'date_time_column' den Index bildet.
            df = df.sort_index()
        return df
    
    def drop_na_rows(self, df):
        """Zeilen entfernen, in denen mehr als 90% der Spalten eines Datenpunktes keinen gültigen Wert aufweisen.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        try:
            threshold = 0.9
            df = df[df.isna().sum(axis=1) <= threshold]
        except Exception as e:
            print(e)
            pass
    
        return df
    
    def remove_outliers(self, df, contamination:float = 0.075):
            """Entferne Ausreißer mit einem Isolation Forest.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
            contamination (float): relativer Anteil des Datensatzes, der als Ausreißer entfernt werden soll.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
            # n_estimators: wie viele Bäume sollen genutzt werden?
            # contamination: welcher relativer Anteil des Datensatzes soll als Ausreißer detektiert werden?
            # max_samples: mit wie vielen Datenpunkten soll der IsolationForest trainiert werden?
            isoforest = IsolationForest(n_estimators = 100, contamination = contamination, max_samples = int(df.shape[0]*0.8))
            # Isolation Forest auf den wichtigsten numerischen Werten durchführen (CO2, tmp, vis, hum und VOC).
            prediction = isoforest.fit_predict(df[["CO2", "tmp", "vis", "hum", "VOC"]])
            print("Number of outliers detected: {}".format(prediction[prediction < 0].sum()))
            print("Number of normal samples detected: {}".format(prediction[prediction >= 0].sum()))
            score = isoforest.decision_function(df[["CO2", "tmp", "vis", "hum", "VOC"]])
            df["anomaly_score"] = score
            # Zeilen mit anomaly_score < 0 werden vom Isolation Forest als Ausreißer interpretiert.
            df = df[df.anomaly_score >= 0]
            return df
    
    def convert_features(self, df):
        """Korrekte Formatierung von Dateitypen von bestimmten Features.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        
        if self.date_time_column in df.columns:
            try:
                df = df[df[self.date_time_column].notna()]
                df[self.date_time_column] = pd.to_datetime(df[self.date_time_column])
            except Exception as e:
                print(e)
                pass
        if "snr" in df.columns:
            try:
                df["snr"] = df["snr"].astype("float")
            except Exception as e:
                print(e)
                pass
        return df
    
    def extract_room_and_building(self, df):
        """Erstellt neue Features für die Trainingsphase eines Machine Learning Modells.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        try:
            df.loc[:, "room_number"] = df["device_id"].str.split("-").str[-1]
            df.loc[:, "building_name"] = df["room_number"].str.replace(r'\d+', '', regex = True)
            building_dict = {"ama":"am","amb":"am", 
                                "ba":"b", "bb":"b",
                                "eu":"e",
                                "fa":"f","fu":"f",
                                "lia":"li","lib":"li","lie":"li","liu":"li",
                                "mu":"m"}
            
            df.replace({"building_name": building_dict}, inplace = True)
        
        except Exception as e:
            print(e)
        return df
    
    
    def remove_duplicates(self, df):
        """Entfernt Duplikate aus dem Datensatz.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        df = df.drop_duplicates([self.date_time_column, "room_number"])
        return df
    
    def remove_features(self, df):
        """Entfernt redundante Features aus dem Datensatz.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        columns = ["bandwidth", "channel_rssi", "channel_index", "device_id", "gateway", "f_cnt", "spreading_factor"]
        for col in columns:
            # for-Schleife, falls nicht alle Spalten im Datensatz enthalten sind.
            try:
                df.drop(columns = [col], axis = 1, inplace = True)
            except:
                continue
        
        return df
    
    def remove_invalid_values(self, df):
        """Entfernt ungültige Datenpunkte aus dem Datensatz.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        # hum beschreibt die relative Luftfeuchtigkeit in %. Daher sind Werte über 100% ungültig.
        df = df[df.hum <= 100]
        # Die Temperatur wird in °C gemessen. Daher gehen wir davon aus, dass es keine Raumtemperaturen über 50°C geben kann. 
        # Auch wegen des Frostschutzes der Heizkörper sollte die Temperatur nicht unter 10°C liegen.
        
        df = df[(df.tmp <= 50) & (df.tmp >= 10)]
        # Der VOC-Wert ist in der Regel etwa gleich hoch oder höchstens sechsmal höher als der CO2-Wert. 
        # Einige Ausreißer geben ein Verhältnis von 156:1 an, was nicht plausibel ist.
        df = df[(df.VOC/df.CO2) < 10]
        # Datenpunkte mit verdächtig großen Wertänderungen bei VOC und CO2 über einen kurzen Zeitraum (60 Sekunden) entfernen
        too_fast_VOC_rise = (df.VOC.diff() >= 1000) & (df[self.date_time_column].diff().dt.seconds < 60)
        too_fast_CO2_rise = (df.CO2.diff() >= 1000) & (df[self.date_time_column].diff().dt.seconds < 60)
        suspicious_rises = too_fast_VOC_rise | too_fast_CO2_rise
        # Filtere den DataFrame
        df = df[~suspicious_rises]
        # Der Datensatz enthält Datenpunkte mit mehreren Nullen. Wir gehen davon aus, dass diese von falschen Messwerten oder Rücksetzungen der Sensorgeräte herrühren könnten.
        df = df[(df.CO2 != 0) & (df.VOC != 0) & (df.tmp != 0) & (df.hum != 0)]
        # Bei Tausenden von Datenpunkten steigt der CO2-Wert stark an, während die anderen Messgrößen einfrieren (z. B. bleibt der VOC-Wert bei einigen Datenpunkten konstant bei 450).
        invalid_values = (df.CO2 > 20000) & (df.VOC.diff() == 0) & (df.VOC.diff() == 0) & (df.BLE.diff() == 0) & (df.tmp.diff() == 0)
        df = df[invalid_values == False]
        df.reset_index(drop = True, inplace = True)
        return df
    
    
    def create_rolling_windows(self, df, rolling_window, sample_time = "60min"):
        """Neuabtastung der Daten in einem bestimmten Zeitintervall (sample_time) und Erstellung von Rolling Windows mit der Größe von rolling_window.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
            rolling_window (str): die Größe des rollierenden Fensters ('1h').
            sample_time (str): die Größe, die für das Resampling des DataFrame df verwendet werden soll. Das Resampling wird an der 'date_time_column' durchgeführt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        df_sorted = df.sort_values(self.date_time_column)
        all_results = list()
        for room in df.room_number.unique():
            room_df = df_sorted[df_sorted.room_number == room]
            numerical_features = ["tmp","hum","CO2","VOC","vis","IR", "BLE", 'rssi', "snr"]
            room_df = room_df.set_index(self.date_time_column)
            if self.roll:
                # Neuabtastung der Datenpunkte (das Abtastintervall sollte kleiner sein als die Größe des rollenden Fensters)
                room_df_resampled = room_df[numerical_features].resample(sample_time).mean()
                # berechne die rollierenden Fenster
                room_df_rolled = room_df_resampled.rolling(rolling_window).mean()
                # Wiedervereinigung der nicht-numerischen Features mit den numerischen Features in dem DataFrame (Features mit Zeitinformationen werden separat hinzugefügt)
                non_numerical_df = room_df.select_dtypes(exclude=['number']).resample(sample_time).first()
                result = room_df_rolled.join(non_numerical_df)
            else:
                result = room_df
            result.loc[:, "room_number"] = room
            all_results.append(result)
            
        # Konkateniere alle DataFrames aus der vorherigen for-Schleife zu einem Objekt.
        all_results_df = pd.concat([result_df for result_df in all_results if not result_df.empty])
        # Entferne leere Datenpunkte, die durch das Resampling entstanden sind.
        all_results_df = self.drop_na_rows(all_results_df)
        return all_results_df
    
    def create_time_diff_features(self, df):
        """Erstelle Features, die zeitliche Werteänderungen darstellen.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        if self.date_time_column not in df.columns:
            # Index zurücksetzen, da die Spalte mit den Zeitinformationen benötigt wird.
            df = df.reset_index()
        df = df.sort_values(by = [self.date_time_column])
        df["time_diff_sec"] = df.groupby('room_number')[self.date_time_column].diff().dt.seconds
        # Iteriere über jedes numerische Feature und berechne die zeitliche Werteänderungen
        for feature in ["tmp"]:
                df[f"{feature}_diff"] = df.groupby('room_number')[feature].diff()
        # es entstehen ggf. unendlich große Werte. Ersetze sie durch 0.
        df = df.replace([np.inf, -np.inf], 0)
        return df
    
    def create_average_differentials(self, df):
        """Berechne die durchschnittliche Änderungsrate pro Sekunde für CO2, VOC, tmp, hum, IR und vis.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt."""
        for feature in ["tmp_diff"]:
                df[f"{feature}_per_sec"] = df[feature].div(df["time_diff_sec"])
        df = df.replace([np.inf, -np.inf], 0)
        return df
    
    def fill_na(self, df):
        """Fülle fehlende Werte im DataFrame auf.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        for col in df.columns:
            is_na = df[col].isna().any()
            if is_na:
                if "_diff" in col:
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(method = "bfill")
                    df[col] = df[col].fillna(method = "ffill")
        return df
    
    def create_new_features(self, df):
        """Füge neue Features hinzu wie z.B. die Farbe der CO2-Ampeldaten in Abhängigkeit vom gemessenen CO2-Wert.
        
        Args:
            df (pandas.DataFrame): DataFrame Objekt.
        Returns:
            df (pandas.DataFrame): DataFrame Objekt.
        """
        # Jahr 2022 wird als 1 behandelt, da die Messung in 2022 angefangen hat. 2023 wird als 2 berechnet etc.
        df.loc[:, "year"] = df[self.date_time_column].dt.year
        df.loc[:, "month"] = df[self.date_time_column].dt.month
        df.loc[:, "dayofweek"] = df[self.date_time_column].dt.dayofweek
        df.loc[:, "hour"] = df[self.date_time_column].dt.hour
        # Farben der CO2-Ampeln laut der Quelle https://www.h-ka.de/fileadmin/Hochschule_Karlsruhe_HKA/Bilder_VW-EBI/HKA_VW-EBI_Anleitung_CO2-Ampeln.pdf
        # Der Einfachheit halber behandeln wir jeden Wert unter 850 als grün, da der CO2-Wert von 850 auf 700 ohnehin schnell abfällt.
        df.loc[(df.CO2 < 850), "color"] = "green"
        df.loc[(df.CO2 >= 850) & (df.CO2 < 1200), "color"] = "yellow"
        df.loc[(df.CO2 >= 1200) & (df.CO2 < 1600), "color"] = "red"
        df.loc[(df.CO2 >= 1600), "color"] = "red_blinking"
        # Einige Räume haben unterschiedliche Verhältnisse zwischen VOC und CO2.
        return df