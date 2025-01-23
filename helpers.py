import concurrent.futures
from dash import html
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import requests
from shapely.geometry import Polygon, MultiPolygon
from config import *


def load_data():
    """
    Load and return the dataset from the local CSV file.
    """
    return pd.read_csv(DATA_PATH)


def prepare_options(data):
    """
    Prepare dropdown options based on the dataset.
    """
    school_classification_options = [
        {
            "label": data[data["Logic_Class"] == logic]["School_Classification"].iloc[0],
            "value": logic
        }
        for logic in ORDERED_LOGIC_CLASSES
        if logic in data["Logic_Class"].unique()
    ]

    locale_options = [
        {"label": locale, "value": locale}
        for locale in data["Locale_Type"].unique()
    ]

    return school_classification_options, locale_options


def prepare_layer_options(layers_metadata):
    """
    Prepare dropdown options based on layers metadata,
    only showing layers that have data for Georgia (STATE=13)
    and contain valid GeoJSON geometry, using concurrent.futures for parallel fetching.
    """
    valid_layers = []
    print("Starting layer data check...")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(
            fetch_layer_data, layer["id"]): layer for layer in layers_metadata}

        for future in concurrent.futures.as_completed(futures):
            layer = futures[future]
            try:
                layer_data = future.result()

                if layer_data is not None and not layer_data.empty and not layer_data.geometry.isnull().all():
                    valid_layers.append({
                        "label": layer["name"],
                        "value": layer["id"]
                    })
                else:
                    continue
            except Exception as e:
                print(f"Error processing layer {layer['id']}: {e}")

    print(f"Layer check complete. Found {len(valid_layers)} valid layers.")
    return valid_layers


def simplify_geometry_dynamically(gdf, zoom_level):
    """
    Dynamically simplify geometries based on the map's zoom level.
    """
    tolerance = max(0.005, 0.05 / (zoom_level + 1)
                    )  # Slightly refined tolerance calculation
    gdf["geometry"] = gdf["geometry"].apply(
        lambda geom: geom.simplify(tolerance, preserve_topology=True)
        if isinstance(geom, (Polygon, MultiPolygon)) else geom
    )
    return gdf


def fetch_georgia_outline():
    """
    Fetch the Georgia state boundary from the TIGERweb States layer.
    """
    endpoint = "80/query"
    params = {
        "where": "STATE='13'", 
        "outFields": "*",  
        "outSR": 4326, 
        "f": "geojson", 
    }
    geojson_data = get_api_info(endpoint, params)

    if not geojson_data or "features" not in geojson_data:
        raise ValueError(f"Invalid GeoJSON response: {geojson_data}")

    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    gdf.crs = "EPSG:4326"
    return gdf


def get_api_info(endpoint, params=None):
    """
    Fetch data from the TIGERweb API or Census API dynamically.
    """
    url = f"{TIGERWEB_BASE_URL}/{endpoint}"
    if params is None:
        params = {}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Check for valid GeoJSON or JSON response
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/json" in content_type or "application/geo+json" in content_type:
            return response.json()
        else:
            return None
    except requests.RequestException as e:
        print(f"Request error for URL {url}: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON from URL {url}: {e}")
        return None


def fetch_layers_metadata():
    """
    Fetch metadata about all layers in the TIGERweb MapServer in JSON format.
    """
    url = f"{TIGERWEB_BASE_URL}/layers?f=pjson"  # Ensure JSON format is requested
    try:
        response = requests.get(url)
        response.raise_for_status()
        metadata = response.json()
        layers = metadata.get("layers", [])

        # Extract relevant information
        layer_info = []
        for layer in layers:
            layer_info.append({
                "id": layer["id"],
                "name": layer["name"],
                "display_field": layer.get("displayField", "NAME"),
                "geometry_type": layer["geometryType"],
                "description": layer["description"]
            })
        return layer_info
    except requests.RequestException as e:
        print(f"Error fetching layers metadata: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return []


def fetch_layer_data(layer_id, display_field="NAME"):
    """
    Fetch layer data filtered for Georgia using the STATE FIPS code.

    Args:
        layer_id (int): The ID of the layer to query.
        display_field (str): The field used for display purposes (default is "NAME").
    
    Returns:
        GeoDataFrame: A GeoDataFrame containing the fetched layer data, or None if the request failed.
    """
    endpoint = f"{layer_id}/query"
    params = {
        "where": "STATE='13'", 
        "outFields": display_field,
        "outSR": 4326,
        "f": "geojson",
        "returnGeometry": "true",
    }

    geojson_data = get_api_info(endpoint, params)

    if geojson_data is None or "features" not in geojson_data or not geojson_data["features"]:
        return None

    for feature in geojson_data["features"]:
        if feature.get("geometry") is None:
            return None

    try:
        gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
        gdf.crs = "EPSG:4326"
        return gdf
    except Exception as e:
        return None


def calculate_total_schools(filtered_data, logic_class_keys):
    """
    Calculate total schools and class counts for given logic keys.
    """
    total = 0
    class_counts = {}
    for key in logic_class_keys:
        class_data = filtered_data[filtered_data["Logic_Class"] == key]
        count = len(class_data)
        total += count
        if count > 0:
            class_counts[key] = count
    return total, class_counts


def generate_legend(fig, filtered_data, color_mapping, title, size_func=None, shape_func=None):
    total_schools, class_counts = calculate_total_schools(
        filtered_data, color_mapping.keys()
    )
    legend_items = []

    for value, color in color_mapping.items():
        if value in class_counts:
            count = class_counts[value]

            school_classification = filtered_data[
                filtered_data["Logic_Class"] == value
            ]["School_Classification"].iloc[0]

            legend_items.append(html.Li([
                html.Div(style={
                    "backgroundColor": color,
                    "width": "12px",
                    "height": "12px",
                    "display": "inline-block",
                    "marginRight": "8px",
                    "clipPath": shape_func(value) if shape_func else "circle",
                    "borderRadius": "50%" if not shape_func or shape_func(value) == "circle" else "0%"
                }),
                f"{school_classification} [{count}]"
            ]))

            data_subset = filtered_data[filtered_data["Logic_Class"] == value].copy(
            )
            fig.add_trace(go.Scattergeo(
                lon=data_subset["X"],
                lat=data_subset["Y"],
                mode="markers",
                marker=dict(
                    size=size_func(value) if size_func else 8,
                    color=color,
                    symbol="triangle-up" if shape_func and shape_func(
                        value) == "polygon(50% 0%, 0% 100%, 100% 100%)" else "circle"
                ),
                hoverinfo="text",
                text=data_subset.apply(
                    lambda row: f"School: {row['School_Name']}<br>School Classification: {
                        row['School_Classification']}<br>Total Students: {row['Total_Student_Count']}",
                    axis=1
                )
            ))

    legend_content = html.Div([
        html.H4(title),
        html.H5(f"High Schools [{total_schools}]"),
        html.Ul(legend_items)
    ])

    return fig, legend_content




def create_modality_legend(fig, filtered_data):
    return generate_legend(
        fig,
        filtered_data,
        COLOR_MAPPINGS["Logic_Class"],
        "CS Course Delivery Modality"
    )


def create_course_legend(fig, filtered_data):
    return generate_legend(
        fig,
        filtered_data,
        COLOR_MAPPINGS["Course_Offered"],
        "CS Course Delivery Modality AND the presence of extra CS-certified teachers",
        size_func=lambda value: 12 if value in TRIANGLE_SHAPES else 8,
        shape_func=lambda value: "polygon(50% 0%, 0% 100%, 100% 100%)" if value in TRIANGLE_SHAPES else "circle"
    )


def create_disparity_legend(fig, filtered_data, selected_disparity):
    if selected_disparity not in filtered_data.columns:
        return fig, html.Div(["No data available for the selected disparity."])

    disparity_data = filtered_data[filtered_data[selected_disparity].notna()].copy(
    )

    low_values = disparity_data[disparity_data[selected_disparity]
                                < -0.05][selected_disparity]
    high_values = disparity_data[disparity_data[selected_disparity]
                                 > 0.05][selected_disparity]

    if not low_values.empty:
        low_bins = pd.qcut(low_values, 3, retbins=True, duplicates="drop")[1]
    else:
        low_bins = [-float('inf'), -0.05]

    if not high_values.empty:
        high_bins = pd.qcut(high_values, 3, retbins=True, duplicates="drop")[1]
    else:
        high_bins = [0.05, float('inf')]

    bins = list(low_bins[:-1]) + [-0.05, 0.05] + list(high_bins[1:])
    adjusted_labels = []
    if len(low_bins) > 1:
        adjusted_labels += ["Dark Red", "Red", "Light Red"][:len(low_bins) - 1]
    adjusted_labels += ["White"]
    if len(high_bins) > 1:
        adjusted_labels += ["Light Green", "Green",
                            "Dark Green"][:len(high_bins) - 1]

    disparity_data['Disparity_Category'] = pd.cut(
        disparity_data[selected_disparity], bins=bins, labels=adjusted_labels, include_lowest=True
    )

    category_counts = disparity_data['Disparity_Category'].value_counts(
        sort=False)
    legend_items = []

    for i, (count, color) in enumerate(zip(category_counts, DISPARITY_COLORS[:len(adjusted_labels)])):
        legend_items.append(html.Li([
            html.Div(style={
                "backgroundColor": color,
                "width": "12px",
                "height": "12px",
                "display": "inline-block",
                "border": "1px solid black" if color == "white" else "none",
                "marginRight": "8px",
                "borderRadius": "50%"
            }),
            f"{bins[i] * 100:.2f}% to {bins[i + 1] * 100:.2f}% [{count}]"
        ]))

    fig.add_trace(go.Scattergeo(
        lon=disparity_data["X"],
        lat=disparity_data["Y"],
        mode="markers",
        marker=dict(
            size=8,
            color=disparity_data['Disparity_Category'].map({
                "Dark Red": "darkred",
                "Red": "red",
                "Light Red": "lightcoral",
                "White": "white",
                "Light Green": "lightgreen",
                "Green": "green",
                "Dark Green": "#004d00"
            }),
            line=dict(width=0.5, color="black")
        ),
        hoverinfo="text",
        text=disparity_data.apply(
            lambda row: (
                f"School: {row['School_Name']}<br>"
                f"Course Offered: {row['School_Classification']}<br>"
                f"Total Students: {row['Total_Student_Count']}<br>"
                f"<b>{selected_disparity.replace('Disparity_', '')} Disparity: {
                    row[selected_disparity] * 100:.2f}%</b><br>"
                + "<br>".join(
                    f"{col.replace('Disparity_', '')} Disparity: {
                        row[col] * 100:.2f}%"
                    for col in DISPARITY_COLUMNS if col != selected_disparity
                )
            ),
            axis=1
        )
    ))

    legend_content = html.Div([
        html.H4(f"{selected_disparity.replace(
            'Disparity_', '')} Disproportion Index"),
        html.H5(f"High Schools [{len(disparity_data)}]"),
        html.Ul(legend_items)
    ])

    return fig, legend_content
