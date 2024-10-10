#### IMPORT LIBRARIES 

import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import tempfile
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pystac_client
import planetary_computer
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import rioxarray

#### CODE

def main():
    # Streamlit interface for inputs
    st.title("ERA5 Planetary Data Download")
    start_date = st.date_input("Start date", value=datetime(1995, 1, 1))
    end_date = st.date_input("End date", value=datetime(1995, 12, 31))
    
    lat_min = st.number_input("Latitude Min:", value=-31.0)
    lat_max = st.number_input("Latitude Max:", value=-29.0)
    lon_min = st.number_input("Longitude Min:", value=26.0)
    lon_max = st.number_input("Longitude Max:", value=29.0)
    location = [lat_min, lat_max, lon_min, lon_max]
    location1 = [lon_min, lat_min, lon_max, lat_max]
    location_str = ', '.join(map(str, location1))
    print(location_str)

    #var_ERA5 = st.selectbox( "ERA5variable", ('precipitation_amount_1hour_Accumulation', 'air_temperature_at_2_metres_1hour_Maximum', 'air_temperature_at_2_metres_1hour_Minimum','eastward_wind_at_10_metres','northward_wind_at_10_metres'),
    #                        index=None,placeholder="Select Variable.",)

    var_ERA5 = st.selectbox(
    label="Select an ERA5 Variable",
    options=[
        'precipitation_amount_1hour_Accumulation', 
        'air_temperature_at_2_metres_1hour_Maximum', 
        'air_temperature_at_2_metres_1hour_Minimum',
        'eastward_wind_at_10_metres', 
        'northward_wind_at_10_metres'
    ],
    index=0,  # Default selection to the first variable
    help="Choose the variable you wish to analyze from ERA5 data.")
    st.write(f"Selected variable: {var_ERA5}")

     # Button to fetch and process the data
    if st.button("Fetch ERA5 Precipitation Data"):
        precipitation_data = fetch_rain_bbox(varname_Rain, factor, location, start_date, end_date)
        precipitation_data = precipitation_data.rename('precipitation')
        daily_precipitation = precipitation_data.resample(time='D').sum()
        historical_djf_sum = calculate_djf_sum(daily_precipitation)
        historical_djf_sum = historical_djf_sum.chunk({'djf_year': -1})
        lower_tercile = historical_djf_sum.quantile(0.33, dim="djf_year")
        upper_tercile = historical_djf_sum.quantile(0.67, dim="djf_year")
         # Plotting lower tercilet with custom color scale
        fig = px.imshow(lower_tercile, 
                        labels=dict(x="Longitude", y="Latitude", color="lower_tercile"),
                        x=lower_tercile.lon,
                        y=lower_tercile.lat)
        
        fig.update_traces(hoverinfo='x+y+z', showscale=True)
        st.plotly_chart(fig, use_container_width=True)  


        # Create a figure
        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        lon = np.linspace(lon_min, lon_max, lower_tercile.shape[1])  # Replace with actual longitude data
        lat = np.linspace(lat_min, lat_max, lower_tercile.shape[0])     # Replace with actual latitude data

        # Plot data
        c = ax.pcolormesh(lon, lat, lower_tercile, transform=ccrs.PlateCarree(), cmap='viridis')

        # Add state boundaries
        ax.add_feature(cfeature.STATES, edgecolor='black')

        # Add coastlines
        ax.coastlines()

        # Add color bar
        plt.colorbar(c, ax=ax, orientation='vertical', label='lower_tercile')

        # Set labels
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        # Display using Streamlit
        st.pyplot(fig)

    select_start_date = st.date_input("Select date", value=datetime(2024, 9, 20))
    select_end_date = st.date_input("Select date", value=datetime(2024, 9, 22))
    if st.button('Map Sentinel 2'):
        
        location = (lon_min, lat_min, lon_max, lat_max)  # Example bounding box (min_lon, min_lat, max_lon, max_lat) 
        fetch_and_map_sentinel2(location, select_start_date, select_end_date)



        # Convert to GeoDataFrame (if necessary)
        # Plot with Mapbox overlay
        # Mapbox access token
        




if __name__ == "__main__":
    main()
