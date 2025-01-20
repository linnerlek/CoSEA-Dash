import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output
from helpers import create_modality_legend, create_course_legend, create_disparity_legend
from layout import data, geojson


def register_callbacks(app):
    @app.callback(
        Output("disparity-options-container", "style"),
        Input("filter-toggle", "value")
    )
    def toggle_disparity_options(selected_filter):
        if selected_filter == "Disparity":
            return {"display": "block"}
        else:
            return {"display": "none"}

    @app.callback(
        [Output("map-display", "figure"), Output("custom-legend", "children")],
        [Input("filter-toggle", "value"),
         Input("school-options-toggle", "value"),
         Input("school-type-toggle", "value"),
         Input("disparity-toggle", "value")]
    )
    def update_map(selected_filter, selected_schools, selected_locales, selected_disparity):
        fig = go.Figure()

        fig.add_trace(go.Scattergeo(
            lon=[coord[0] for coord in geojson["geometry"]["coordinates"][0]],
            lat=[coord[1] for coord in geojson["geometry"]["coordinates"][0]],
            mode="lines",
            line=dict(color="black", width=2)
        ))

        filtered_data = data[
            (data["Logic_Class"].isin(selected_schools)) &
            (data["Locale_Type"].isin(selected_locales))
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
            geo=dict(
                projection_type="mercator",
                showcoastlines=False,
                showland=False,
                fitbounds="locations",
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False
        )

        return fig, legend_content
