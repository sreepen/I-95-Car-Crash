#init
import pyspark
from pyspark import SparkContext
from pyspark.sql import SparkSession
import os
import datetime

import geopandas as gpd
import pandas as pd
import geoplot as gplt
import geoplot.crs as gcrs
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, Point

ss=SparkSession.builder.appName("final_snakey").getOrCreate()

#Load CSV
df = ss.read.csv('/storage/work/krt5335/ds410/final/clusterdata.csv', header=True, inferSchema=True)
df.printSchema()


def snakey(my_state: str):
    #Create dataframe: only rows with end points can be used.
    df_startend = df[['Start_Lat', 'Start_Lng', 'End_Lng', 'End_Lat', 'State', 'City', 'Severity']].dropna()
    df_startend = df_startend[df_startend['State'].isin([my_state])]
    pdf = df_startend.toPandas()

    #Create dataframe: use coordinates to create lines
    gdf = gpd.GeoDataFrame(
        pdf,
        geometry = pdf.apply(
        lambda r: LineString([
            (r['Start_Lng'], r['Start_Lat']),
            (r['End_Lng'], r['End_Lat'])
        ]),
        axis=1
    ),
        crs="EPSG:4326" #Coordinate Reference System WGS84: Latitude and longitude based coordinate system
    )

    #Shape files
    states = gpd.read_file("/storage/work/krt5335/ds410/final/cb_stateshapes.shp")
    states = states.set_crs(epsg=4269)
    states_4326 = states.to_crs(epsg=4326)

    #Finding which state based on listed coordinates (for flexibility)
    center_lat = pdf['Start_Lat'].mean()
    center_lng = pdf['Start_Lng'].mean()
    center_point = Point(center_lng, center_lat)
    
    mask = states_4326.contains(center_point)
    bg_geom = states_4326[mask].iloc[[0]]

    #Adhere projection to state (makes the projection look better)
    def state_albers(state_geom_4326: gpd.GeoDataFrame):
        minx, miny, maxx, maxy = state_geom_4326.total_bounds
        central_lon = 0.5 * (minx + maxx)
        central_lat = 0.5 * (miny + maxy)
        p1 = miny + (maxy - miny) * 0.25
        p2 = miny + (maxy - miny) * 0.75
        return ccrs.AlbersEqualArea(
            central_longitude=central_lon,
            central_latitude=central_lat,
            standard_parallels=(p1, p2)
        )

    #Align maps
    proj = state_albers(bg_geom)
    fig, ax = plt.subplots(
        1, 1, figsize=(12, 12),
        subplot_kw={'projection': proj}
    )
    
    state_geom = bg_geom.geometry.iloc[0]
    minx, miny, maxx, maxy = state_geom.bounds

    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    half_width  = (maxx - minx) * 0.8
    half_height = (maxy - miny) * 0.8

    ax.set_extent(
        [cx - half_width, cx + half_width,
         cy - half_height, cy + half_height],
        crs=ccrs.PlateCarree()
    )

    #Background projection
    ax.add_geometries(
        bg_geom.geometry,
        crs=ccrs.PlateCarree(),   # data are in lon/lat
        facecolor='lightgray',
        edgecolor='black',
        linewidth=0.5
    )

    #Foreground projection
    gplt.sankey(
        gdf, ax=ax,
        scale=None, limits=(0.1, 10), hue='Severity', cmap='Set1', 
        linewidth=0.5
    )

    #Realignment
    ax.set_extent(
        [cx - half_width, cx + half_width,
         cy - half_height, cy + half_height],
        crs=ccrs.PlateCarree()
    )
    plt.title(f"Snake Plot for {my_state}")

  # SAVE PNG
    os.makedirs("plots_cluster", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f"plots_cluster/{my_state}_snakey_{timestamp}.png", dpi=300)

    plt.show()
    
states = (
    df.select("State")
      .distinct()
      .rdd.flatMap(lambda x: x)
      .collect()
)

for st in states:
   print(st)
   snakey(st)
#--Katherine

ss.stop()





