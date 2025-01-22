from dash import Input, Output
import plotly.graph_objects as go
from config import FIGURE_LAYOUT
from helpers import *

georgia_outline_gdf = simplify_geometry(load_georgia_outline())
school_districts_gdf = simplify_geometry(load_school_districts())
data = load_data()


def register_callbacks(app):
    @app.callback(
        Output("disparity-options-container", "style"),
        Input("filter-toggle", "value"),
    )
    def toggle_disparity_options(selected_filter):
        if selected_filter == "Disparity":
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        [Output("map-display", "figure"), Output("custom-legend", "children")],
        [
            Input("filter-toggle", "value"),
            Input("school-options-toggle", "value"),
            Input("school-type-toggle", "value"),
            Input("map-options-toggle", "value"),
            Input("disparity-toggle", "value"),
        ],
    )
    def update_map(selected_filter, selected_schools, selected_types, map_options, selected_disparity):
        """
        Update the map based on selected options.
        """
        fig = go.Figure()

        state_outline = georgia_outline_gdf.unary_union
        if state_outline.geom_type == "Polygon":
            lon_coords, lat_coords = zip(*state_outline.exterior.coords)
            fig.add_trace(
                go.Scattergeo(
                    lon=lon_coords,
                    lat=lat_coords,
                    mode="lines",
                    line=dict(color="black", width=2),
                    hoverinfo="skip",
                )
            )
        elif state_outline.geom_type == "MultiPolygon":
            for polygon in state_outline.geoms:
                lon_coords, lat_coords = zip(*polygon.exterior.coords)
                fig.add_trace(
                    go.Scattergeo(
                        lon=lon_coords,
                        lat=lat_coords,
                        mode="lines",
                        line=dict(color="black", width=2),
                        hoverinfo="skip",
                    )
                )

        if "school_districts" in map_options:
            for _, row in school_districts_gdf.iterrows():
                geometry = row.geometry
                district_type = "Unified" if "unsd" in row["GEOID"] else "Secondary"
                color = "blue" if district_type == "Unified" else "green"
                dash_style = "solid" if district_type == "Unified" else "dot"

                if geometry.geom_type == "Polygon":
                    lon_coords, lat_coords = zip(*geometry.exterior.coords)
                    fig.add_trace(
                        go.Scattergeo(
                            lon=lon_coords,
                            lat=lat_coords,
                            mode="lines",
                            line=dict(color=color, width=1, dash=dash_style),
                            hoverinfo="text",
                            text=row["NAME"],
                        )
                    )
                elif geometry.geom_type == "MultiPolygon":
                    for polygon in geometry.geoms:
                        lon_coords, lat_coords = zip(*polygon.exterior.coords)
                        fig.add_trace(
                            go.Scattergeo(
                                lon=lon_coords,
                                lat=lat_coords,
                                mode="lines",
                                line=dict(color=color, width=1,
                                          dash=dash_style),
                                hoverinfo="text",
                                text=row["NAME"],
                            )
                        )

        filtered_data = data[
            (data["Logic_Class"].isin(selected_schools)) &
            (data["Locale_Type"].isin(selected_types))
        ]

        legend_content = []
        if selected_filter == "Logic_Class":
            fig, legend_content = create_modality_legend(fig, filtered_data)
        elif selected_filter == "Course_Offered":
            fig, legend_content = create_course_legend(fig, filtered_data)
        elif selected_filter == "Disparity":
            if selected_disparity:
                fig, legend_content = create_disparity_legend(
                    fig, filtered_data, selected_disparity)

        fig.update_layout(
            **FIGURE_LAYOUT,
            uirevision="constant",
        )
        return fig, legend_content
