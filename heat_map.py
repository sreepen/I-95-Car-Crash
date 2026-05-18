# -*- coding: utf-8 -*-
#!pip install folium

import folium
from folium.plugins import HeatMap
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output

# Load and clean data
df = pd.read_csv("/storage/work/mpd5779/Project/US_Accidents_March23.csv")
df_clean = df[['Start_Lat', 'Start_Lng', 'State', 'Severity']].dropna()

def generate_map(state, severity):
  filtered = df_clean.copy()
  # Filter by state
  if state != 'All':
    filtered = df_clean[df_clean['State'] == state]

  # Filter by severity
  if severity != 'All':
    filtered = filtered[filtered['Severity'] == severity]

  # Create map
  center_lat = filtered['Start_Lat'].mean()
  center_lng = filtered['Start_Lng'].mean()
  base_map = folium.Map(location=[center_lat, center_lng])
  heat_data = filtered[['Start_Lat', 'Start_Lng']].values.tolist()
  HeatMap(heat_data, radius=10, blur=12).add_to(base_map)

  # Fit to bounds
  sw = [filtered['Start_Lat'].min(), filtered['Start_Lng'].min()]
  ne = [filtered['Start_Lat'].max(), filtered['Start_Lng'].max()]
  base_map.fit_bounds([sw, ne])

  base_map.save(f"heatmap_{state}_{severity}.html")

generate_map('PA', 'All')
generate_map('PA', 1)
generate_map('PA', 2)
generate_map('PA', 3)
generate_map('PA', 4)
generate_map('All', 'All')
generate_map('All', 1)
generate_map('All', 2)
generate_map('All', 3)
generate_map('All', 4)