import os
import pandas as pd
import numpy as np

def load_data(selected_date=None):
    if not selected_date:
        return pd.DataFrame()
    
    file_path = f"data/redfin_hollywood_hills_cleaned_{selected_date}.csv"
    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)
        df.replace({'—': np.nan, 'N/A': np.nan, '': np.nan}, inplace=True)
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Beds"] = pd.to_numeric(df["Beds"], errors="coerce")
        df["Baths"] = pd.to_numeric(df["Baths"], errors="coerce")
        df["SqFt"] = pd.to_numeric(df["SqFt"], errors="coerce")
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
        df.dropna(subset=["Price", "Beds", "Baths", "SqFt", "Latitude", "Longitude"], inplace=True)
        return df
    except FileNotFoundError:
        return pd.DataFrame()