from dash import html, dcc
import pandas as pd
import json
from config import GEOJSON_PATH, DATA_PATH, FILTER_OPTIONS, DISPARITY_COLUMNS, COLOR_MAPPINGS

# Opens the geojson file and reads it
with open(GEOJSON_PATH, "r") as geo_file:
    geojson = json.load(geo_file)

# Reads the data from the CSV file
data = pd.read_csv(DATA_PATH)


def create_layout(app):
    return html.Div([
        html.H1("CoSEA Dashboard", style={"textAlign": "center"}),
        html.Div([
            html.Div([
                html.Label("Select Overlay:"),
                dcc.Dropdown(
                    id="filter-toggle",
                    options=FILTER_OPTIONS,
                    value="Logic_Class"
                )
            ]),
            html.Div(
                id="disparity-options-container",
                style={"display": "none"},
                children=[
                    html.Label("Disparity Options:", style={
                               "fontWeight": "bold"}),
                    dcc.RadioItems(
                        id="disparity-toggle",
                        options=[
                            {"label": col.replace(
                                "Disparity_", ""), "value": col}
                            for col in DISPARITY_COLUMNS
                        ],
                        value="Disparity_Black",
                        inline=True
                    )
                ]
            ),
            html.Div(id="settings-container", children=[
                html.Label("School Settings:", style={
                           "fontWeight": "bold", "marginTop": "20px"}),
                html.Div([
                    html.Label("Offering Approved CS Classes:",
                               style={"fontWeight": "bold"}),
                    dcc.Checklist(
                        id="school-options-toggle",
                        options=[
                            {"label": data[data['Logic_Class'] == key]
                                ['School_Classification'].iloc[0], "value": key}
                            for key in COLOR_MAPPINGS["Logic_Class"].keys()
                        ],
                        value=list(COLOR_MAPPINGS["Logic_Class"].keys()),
                        inline=True
                    )
                ], style={"marginBottom": "20px"}),
                html.Div([
                    html.Label("School Type:", style={"fontWeight": "bold"}),
                    dcc.Checklist(
                        id="school-type-toggle",
                        options=[
                            {"label": locale, "value": locale}
                            for locale in data["Locale_Type"].unique()
                        ],
                        value=data["Locale_Type"].unique().tolist(),
                        inline=True
                    )
                ], style={"marginBottom": "20px"}),
            ])
        ]),
        dcc.Graph(id="map-display", config={'displayModeBar': False}),
        html.Div(id="custom-legend",
                 style={"padding": "20px", "textAlign": "center"})
    ])
