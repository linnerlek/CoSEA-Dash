from dash import Input, Output
import plotly.graph_objects as go
from config import FIGURE_LAYOUT
from helpers import *

layer_data_cache = {}


def register_callbacks(app, georgia_outline_gdf, data, layer_metadata):
    @app.callback(
        Output("disparity-options-container", "style"),
        Input("filter-toggle", "value"),
    )
    def toggle_disparity_options(selected_filter):
        if selected_filter == "Disparity":
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        [
            Output("map-display", "figure"),
            Output("custom-legend", "children"),
        ],
        [
            Input("layer-dropdown", "value"),
            Input("filter-toggle", "value"),
            Input("school-options-toggle", "value"),
            Input("school-type-toggle", "value"),
            Input("disparity-toggle", "value"),
        ],
    )
    def update_map(
        selected_layer,
        selected_filter,
        selected_schools,
        selected_types,
        selected_disparity,
    ):
        filtered_data = data[
            (data["Grade_Range"].isin(["09-12", "10-12"]))
            & (data["Logic_Class"].isin(selected_schools))
            & (data["Locale_Type"].isin(selected_types))
        ]

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

        if selected_layer:
            selected_layer_metadata = next(
                (layer for layer in layer_metadata if layer["id"]
                 == selected_layer), None
            )

            if selected_layer_metadata:
                print(f"Layer selected: {selected_layer_metadata['name']}")
                if selected_layer not in layer_data_cache:
                    layer_data = fetch_layer_data(
                        selected_layer_metadata["id"],
                        selected_layer_metadata.get("display_field", "NAME")
                    )
                    if layer_data is not None and not layer_data.empty:
                        layer_data_cache[selected_layer] = layer_data
                layer_data = layer_data_cache.get(selected_layer)

                if layer_data is not None:
                    simplified_layer_data = simplify_geometry_dynamically(
                        layer_data, zoom_level=8
                    )
                    for _, feature in simplified_layer_data.iterrows():
                        geometry = feature.geometry
                        name = feature.get(selected_layer_metadata.get(
                            "display_field", "NAME"), "Unnamed Layer")
                        if geometry.geom_type == "Polygon":
                            lon_coords, lat_coords = zip(
                                *geometry.exterior.coords)
                            fig.add_trace(
                                go.Scattergeo(
                                    lon=lon_coords,
                                    lat=lat_coords,
                                    mode="lines",
                                    line=dict(color="blue", width=1),
                                    hoverinfo="text",
                                    text=name,
                                )
                            )
                        elif geometry.geom_type == "MultiPolygon":
                            for polygon in geometry.geoms:
                                lon_coords, lat_coords = zip(
                                    *polygon.exterior.coords)
                                fig.add_trace(
                                    go.Scattergeo(
                                        lon=lon_coords,
                                        lat=lat_coords,
                                        mode="lines",
                                        line=dict(color="blue", width=1),
                                        hoverinfo="text",
                                        text=name,
                                    )
                                )
            else:
                print(f"Layer {selected_layer} not found in layer_metadata.")

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
