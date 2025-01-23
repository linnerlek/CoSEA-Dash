from dash import html, dcc


def create_layout(app, filter_options, school_classification_options, locale_options, disparity_columns, valid_layer_options):
    valid_layer_options.insert(0, {"label": "No Layer", "value": "none"})
    return html.Div(
        [
            html.H1("CoSEA Dashboard"),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Plot Options"),
                            html.Div(
                                [
                                    html.Label("Select Overlay:"),
                                    dcc.Dropdown(
                                        id="filter-toggle",
                                        options=filter_options,
                                        value="Logic_Class",
                                    ),
                                ]
                            ),
                            html.Div(
                                id="settings-container",
                                children=[
                                    html.H4("School Classification:"),
                                    dcc.Checklist(
                                        id="school-options-toggle",
                                        options=school_classification_options,
                                        value=[opt["value"]
                                               for opt in school_classification_options],
                                        inline=True,
                                    ),
                                    html.H4("School Type:"),
                                    dcc.Checklist(
                                        id="school-type-toggle",
                                        options=locale_options,
                                        value=[opt["value"]
                                               for opt in locale_options],
                                        inline=True,
                                    ),
                                    html.Div(
                                        id="disparity-options-container",
                                        style={"display": "none"},
                                        children=[
                                            html.H4("Disparity Options:"),
                                            dcc.RadioItems(
                                                id="disparity-toggle",
                                                options=[
                                                    {"label": col.replace(
                                                        "Disparity_", ""), "value": col}
                                                    for col in disparity_columns
                                                ],
                                                value="Disparity_Asian",
                                                inline=True,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.H3("Map Options"),
                            html.Div(
                                [
                                    html.Label("Select Layer:"),
                                    dcc.Dropdown(
                                        id="layer-dropdown",
                                        options=valid_layer_options,
                                        placeholder="Choose a layer...",
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            dcc.Graph(id="map-display", config={"displayModeBar": False}),
            html.Div(id="custom-legend",
                     style={"padding": "20px", "textAlign": "center"}),
        ]
    )
