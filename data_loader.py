import os
from shapely.geometry import Polygon, MultiPolygon
import osmnx as ox
import geopandas as gpd
import requests
import tempfile
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Database connection string (should match app.py)
engine = create_engine(
    "postgresql+psycopg2://cosea_user:CoSeaIndex@pgsql.dataconn.net:5432/cosea_db"
)


# --- Load all school data (must be defined before preload) ---
def load_all_school_data():
    # Load all relevant precomputed tables and columns from the database
    # Main school-level table with all computed columns (enrollment, RI, logic flags, etc)
    gadoe = pd.read_sql('SELECT * FROM "census"."gadoe2024_389"', engine)

    # Course-level logic table
    course_logic = pd.read_sql(
        'SELECT * FROM "census"."course_logic_2024"', engine)

    # All info from allhsgrades24.tbl_approvedschools
    approved_all = pd.read_sql(
        'SELECT * FROM "allhsgrades24"."tbl_approvedschools"', engine)

    # Return as a dictionary for easy access
    return {
        "gadoe": gadoe,
        "course_logic": course_logic,
        "approved_all": approved_all
    }

# --- Load static geospatial data at startup ---
def load_geodata():
    # ...existing code...
    ga_boundary = ox.geocode_to_gdf("Georgia, USA").to_crs(epsg=4326)
    county_url = "https://www2.census.gov/geo/tiger/TIGER2022/COUNTY/tl_2022_us_county.zip"
    county_zip = os.path.join(tempfile.gettempdir(), "tl_2022_us_county.zip")
    if not os.path.exists(county_zip):
        r = requests.get(county_url, verify=False)
        with open(county_zip, "wb") as f:
            f.write(r.content)
    counties = gpd.read_file(f"zip://{county_zip}")
    ga_counties = counties[counties["STATEFP"] == "13"].to_crs(epsg=4326)
    county_lines = []
    simplify_tol = 0.01
    for _, row in ga_counties.iterrows():
        geom = row.geometry.simplify(simplify_tol, preserve_topology=True)
        if isinstance(geom, Polygon):
            x, y = geom.exterior.xy
            county_lines.append((list(x), list(y)))
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                x, y = poly.exterior.xy
                county_lines.append((list(x), list(y)))
    road_url = "https://www2.census.gov/geo/tiger/TIGER2022/PRIMARYROADS/tl_2022_us_primaryroads.zip"
    road_zip = os.path.join(tempfile.gettempdir(),
                            "tl_2022_us_primaryroads.zip")
    if not os.path.exists(road_zip):
        r = requests.get(road_url, verify=False)
        with open(road_zip, "wb") as f:
            f.write(r.content)
    roads = gpd.read_file(f"zip://{road_zip}")
    interstates = roads[roads["RTTYP"] == "I"].to_crs(epsg=4326)
    interstates = gpd.clip(interstates, ga_boundary)
    highway_lines = []
    for _, row in interstates.iterrows():
        geom = row.geometry.simplify(simplify_tol, preserve_topology=True)
        x, y = geom.xy
        highway_lines.append((list(x), list(y)))
    ga_outline = []
    for _, row in ga_boundary.iterrows():
        geom = row.geometry.simplify(simplify_tol, preserve_topology=True)
        if isinstance(geom, Polygon):
            x, y = geom.exterior.xy
            ga_outline.append((list(x), list(y)))
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                x, y = poly.exterior.xy
                ga_outline.append((list(x), list(y)))
    return {
        "ga_boundary": ga_boundary,
        "county_lines": county_lines,
        "highway_lines": highway_lines,
        "ga_outline": ga_outline
    }


# --- Preload geodata and school data at module import for fast app startup ---
GEODATA = load_geodata()
SCHOOLDATA = load_all_school_data()