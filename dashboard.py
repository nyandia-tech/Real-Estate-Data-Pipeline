import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import folium
from streamlit_folium import st_folium
import numpy as np

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/redfin_hollywood_hills_cleaned.csv")
    # Ensure correct data types
    df["Price"] = df["Price"].astype(float)
    df["Beds"] = df["Beds"].astype(float)
    df["Baths"] = df["Baths"].astype(float)
    df["SqFt"] = df["SqFt"].astype(float)
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    return df.dropna(subset=["Latitude", "Longitude"])  # Remove entries without coordinates

df = load_data()

# Streamlit UI
st.title("🏡 Hollywood Hills Real Estate Dashboard")
st.write("Analyze real estate trends in Hollywood Hills using interactive visualizations.")

# Sidebar Filters
st.sidebar.header("🔍 Filter Listings")

# Show all properties button
show_all = st.sidebar.checkbox("Show All Properties", value=False)

if show_all:
    filtered_df = df  # Show all properties
else:
    # Determine the max price dynamically and round up to the next 1 million
    min_price_value = max(1000, df["Price"].min())  # Ensure minimum is at least 1,000
    max_price_value = np.ceil(df["Price"].max() / 1_000_000) * 1_000_000  # Round up to next 1M

    # Price Slider
    min_price, max_price = st.sidebar.slider(
        "Select Price Range ($)", 
        min_value=int(min_price_value), 
        max_value=int(max_price_value), 
        value=(int(min_price_value), int(max_price_value)),
        format="$%d"
    )

    # Bedrooms: Round up to the next multiple of 5
    min_beds = 1
    max_beds = int(np.ceil(df["Beds"].max() / 5) * 5)

    # Bathrooms: Round up to the next multiple of 5
    min_baths = 1
    max_baths = int(np.ceil(df["Baths"].max() / 5) * 5)

    # Square Footage: Ensure a sensible range
    min_sqft = 100
    max_sqft = int(np.ceil(df["SqFt"].max() / 10_000) * 10_000)

    # Filters
    selected_beds = st.sidebar.slider("Bedrooms", min_beds, max_beds, (1, 5))
    selected_baths = st.sidebar.slider("Bathrooms", min_baths, max_baths, (1, 5))
    selected_sqft = st.sidebar.slider("Square Footage", min_sqft, max_sqft, (500, 5000))

    # Apply Filters
    filtered_df = df[
        (df["Price"] >= min_price) & (df["Price"] <= max_price) &
        (df["Beds"] >= selected_beds[0]) & (df["Beds"] <= selected_beds[1]) &
        (df["Baths"] >= selected_baths[0]) & (df["Baths"] <= selected_baths[1]) &
        (df["SqFt"] >= selected_sqft[0]) & (df["SqFt"] <= selected_sqft[1])
    ]