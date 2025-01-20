import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output
from helpers import create_modality_legend, create_course_legend, create_disparity_legend
from layout import data, geojson, counties_geojson
from config import FIGURE_LAYOUT
from shapely.geometry import shape


def register_callbacks(app):
    @app.callback(
        Output("disparity-options-container", "style"),
        Input("filter-toggle", "value"),
    )
    def toggle_disparity_options(selected_filter):
        if selected_filter == "Disparity":
            return {"display": "block"}
        else:
            return {"display": "none"}

    @app.callback(
        [Output("map-display", "figure"), Output("custom-legend", "children")],
        [
            Input("filter-toggle", "value"),
            Input("school-options-toggle", "value"),
            Input("school-type-toggle", "value"),
            Input("disparity-toggle", "value"),
            Input("map-options-toggle", "value"),
        ],
    )
    def update_map(
        selected_filter, selected_schools, selected_locales, selected_disparity, map_options
    ):
        fig = go.Figure()

        fig.add_trace(
            go.Scattergeo(
                lon=[coord[0] for coord in geojson["geometry"]["coordinates"][0]],
                lat=[coord[1] for coord in geojson["geometry"]["coordinates"][0]],
                mode="lines",
                line=dict(color="black", width=2),
                hoverinfo="skip", 
            )
        )

        if "county_lines" in map_options:
            for feature in counties_geojson["features"]:
                geometry = feature["geometry"]

                if geometry["type"] == "Polygon":
                    for polygon in geometry["coordinates"]:
                        lon_coords, lat_coords = zip(*polygon)
                        fig.add_trace(
                            go.Scattergeo(
                                lon=lon_coords,
                                lat=lat_coords,
                                mode="lines",
                                line=dict(color="grey", width=0.5),
                                showlegend=False,
                                hoverinfo="skip", 
                            )
                        )
                elif geometry["type"] == "MultiPolygon":
                    for multipolygon in geometry["coordinates"]:
                        for polygon in multipolygon:
                            lon_coords, lat_coords = zip(*polygon)
                            fig.add_trace(
                                go.Scattergeo(
                                    lon=lon_coords,
                                    lat=lat_coords,
                                    mode="lines",
                                    line=dict(color="grey", width=0.5),
                                    showlegend=False,
                                    hoverinfo="skip",  
                                )
                            )

        if "county_names" in map_options:
            for feature in counties_geojson["features"]:
                geometry = feature["geometry"]
                county_name = feature["properties"]["name"]
                geom = shape(geometry)
                lon, lat = geom.centroid.x, geom.centroid.y

                fig.add_trace(
                    go.Scattergeo(
                        lon=[lon],
                        lat=[lat],
                        mode="text",
                        text=county_name,
                        textfont=dict(size=10, color="darkgrey"),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )

        filtered_data = data[
            (data["Logic_Class"].isin(selected_schools))
            & (data["Locale_Type"].isin(selected_locales))
        ].copy()

        if selected_filter == "Logic_Class":
            fig, legend_content = create_modality_legend(fig, filtered_data)
        elif selected_filter == "Course_Offered":
            fig, legend_content = create_course_legend(fig, filtered_data)
        elif selected_filter == "Disparity" and selected_disparity:
            fig, legend_content = create_disparity_legend(
                fig, filtered_data, selected_disparity)
        else:
            legend_content = []

        fig.update_layout(
            **FIGURE_LAYOUT,
            uirevision="constant", 
        )
        return fig, legend_content
