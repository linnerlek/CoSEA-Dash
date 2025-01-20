import json
from dash import html, dcc
import pandas as pd
from config import (
    GEOJSON_PATH,
    DATA_PATH,
    FILTER_OPTIONS,
    DISPARITY_COLUMNS,
    COLOR_MAPPINGS,
    GEORGIA_COUNTIES_GEOJSON_PATH,
)

with open(GEOJSON_PATH, "r") as geo_file:
    geojson = json.load(geo_file)

with open(GEORGIA_COUNTIES_GEOJSON_PATH, "r") as counties_file:
    counties_geojson = json.load(counties_file)

data = pd.read_csv(DATA_PATH)

def create_layout(app):
    return html.Div(
        [
            html.H1("CoSEA Dashboard"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Select Overlay:"),
                            dcc.Dropdown(
                                id="filter-toggle",
                                options=FILTER_OPTIONS,
                                value="Logic_Class",
                            ),
                        ]
                    ),
                    html.Div(
                        id="disparity-options-container",
                        style={"display": "none"},
                        children=[
                            html.Label(
                                "Disparity Options:"),
                            dcc.RadioItems(
                                id="disparity-toggle",
                                options=[
                                    {
                                        "label": col.replace("Disparity_", ""),
                                        "value": col,
                                    }
                                    for col in DISPARITY_COLUMNS
                                ],
                                value="Disparity_Asian",
                                inline=True,
                            ),
                        ],
                    ),
                    html.Div(
                        id="settings-container",
                        children=[
                            html.Label(
                                "School Options:",
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Approved CS Classes / Extra teachers:",
                                    ),
                                    dcc.Checklist(
                                        id="school-options-toggle",
                                        options=[
                                            {
                                                "label": data[
                                                    data["Logic_Class"] == key
                                                ]["School_Classification"].iloc[0],
                                                "value": key,
                                            }
                                            for key in COLOR_MAPPINGS[
                                                "Logic_Class"
                                            ].keys()
                                        ],
                                        value=list(
                                            COLOR_MAPPINGS["Logic_Class"].keys(
                                            )
                                        ),
                                        inline=True,
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "School Type:"
                                    ),
                                    dcc.Checklist(
                                        id="school-type-toggle",
                                        options=[
                                            {"label": locale, "value": locale}
                                            for locale in data["Locale_Type"].unique()
                                        ],
                                        value=data["Locale_Type"].unique(
                                        ).tolist(),
                                        inline=True,
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Map Options:"),
                                    dcc.Checklist(
                                        id="map-options-toggle",
                                        options=[
                                            {"label": "Show County Outlines",
                                                "value": "county_lines"},
                                            {"label": "Show County Names",
                                                "value": "county_names"},
                                        ],
                                        value=[],
                                    ),
                                ]
                            ),
                        ],
                    ),
                ]
            ),
            dcc.Graph(
                id="map-display",
                config={
                    "displayModeBar": False
                },
            ),
            html.Div(
                id="custom-legend", style={"padding": "20px", "textAlign": "center"}
            ),
        ]
    )
