from config import *
import json
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go

# Opens the geojson file and reads it
with open(GEOJSON_PATH, "r") as geo_file:
    geojson = json.load(geo_file)

# Reads the data from the csv file
data = pd.read_csv(DATA_PATH)

# Current total schools displayed on map
def calculate_total_schools(filtered_data, logic_class_keys):
    total = 0
    class_counts = {}
    for key in logic_class_keys:
        class_data = filtered_data[filtered_data["Logic_Class"] == key]
        count = len(class_data)
        total += count
        if count > 0:
            class_counts[key] = count
    return total, class_counts

app = Dash(__name__)

# App layout
app.layout = html.Div([
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
            style={"display": "none"},  # Initially hidden 
            children=[
                html.Label("Disparity Options:", style={"fontWeight": "bold"}),
                dcc.RadioItems(
                    id="disparity-toggle",
                    options=[
                        {"label": col.replace("Disparity_", ""), "value": col}
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



# Show or hide Disparity Options 
@app.callback(
    Output("disparity-options-container", "style"),
    Input("filter-toggle", "value")
)
def toggle_disparity_options(selected_filter):
    if selected_filter == "Disparity":
        return {"display": "block"}  
    else:
        return {"display": "none"}  



# Update map and legend
@app.callback(
    [Output("map-display", "figure"), Output("custom-legend", "children")],
    [Input("filter-toggle", "value"),
     Input("school-options-toggle", "value"),
     Input("school-type-toggle", "value"),
     Input("disparity-toggle", "value")]
)
def update_map(selected_filter, selected_schools, selected_locales, selected_disparity):
    fig = go.Figure()

    # Add Georgia outline
    fig.add_trace(go.Scattergeo(
        lon=[coord[0] for coord in geojson["geometry"]["coordinates"][0]],
        lat=[coord[1] for coord in geojson["geometry"]["coordinates"][0]],
        mode="lines",
        line=dict(color="black", width=2)
    ))

    legend_content = [] # Default to empty legend

    # Filter school data based on selected school options
    filtered_data = data[
        (data["Logic_Class"].isin(selected_schools)) &
        (data["Locale_Type"].isin(selected_locales))
    ].copy()

    # Modality section
    if selected_filter == "Logic_Class":
        total_schools, class_counts = calculate_total_schools(
            filtered_data, COLOR_MAPPINGS["Logic_Class"].keys())
        modality_legend_items = []
        for value, color in COLOR_MAPPINGS["Logic_Class"].items():
            if value in class_counts:
                count = class_counts[value]
                modality_legend_items.append(html.Li([
                    html.Div(style={
                        "backgroundColor": color,
                        "width": "12px",
                        "height": "12px",
                        "display": "inline-block",
                        "marginRight": "8px",
                        "borderRadius": "50%"
                    }),
                    f"{data[data['Logic_Class'] == value]
                        ['School_Classification'].iloc[0]} [{count}]"
                ]))

                modality_data = filtered_data[filtered_data["Logic_Class"] == value].copy(
                )
                fig.add_trace(go.Scattergeo(
                    lon=modality_data["X"],
                    lat=modality_data["Y"],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=color,
                        symbol="circle"
                    ),
                    hoverinfo="text",
                    text=modality_data.apply(
                        lambda row: f"School: {row['School_Name']}<br>School Classification: {
                            row['School_Classification']}<br>Total Students: {row['Total_Student_Count']}",
                        axis=1
                    )
                ))

        legend_content = html.Div([
            html.H4("CS Course Delivery Modality"),
            html.H5(f"High Schools [{total_schools}]"),
            html.Ul(modality_legend_items)
        ])

    # Modality and CS-Certification section
    elif selected_filter == "Course_Offered":
        total_schools, class_counts = calculate_total_schools(
            filtered_data, COURSE_OFFERED_COLORS.keys())
        course_legend_items = []

        for value, color in COURSE_OFFERED_COLORS.items():
            if value in class_counts:
                count = class_counts[value]
                course_legend_items.append(html.Li([
                    html.Div(style={
                        "backgroundColor": color,
                        "width": "12px",
                        "height": "12px",
                        "display": "inline-block",
                        "marginRight": "8px",
                        "clipPath": "polygon(50% 0%, 0% 100%, 100% 100%)" if value in TRIANGLE_SHAPES else "circle",
                        "borderRadius": "50%" if value not in TRIANGLE_SHAPES else "0%"
                    }),
                    f"{filtered_data[filtered_data['Logic_Class'] == value]
                        ['School_Classification'].iloc[0]} [{count}]"
                ]))

                course_offered_data = filtered_data[filtered_data["Logic_Class"] == value].copy(
                )
                fig.add_trace(go.Scattergeo(
                    lon=course_offered_data["X"],
                    lat=course_offered_data["Y"],
                    mode="markers",
                    marker=dict(
                        size=12 if value in TRIANGLE_SHAPES else 8,
                        color=color,
                        symbol="triangle-up" if value in TRIANGLE_SHAPES else "circle"
                    ),
                    hoverinfo="text",
                    text=course_offered_data.apply(
                        lambda row: f"School: {row['School_Name']}<br>Course Offered: {
                            row['School_Classification']}<br>Total Students: {row['Total_Student_Count']}",
                        axis=1
                    )
                ))

        legend_content = html.Div([
            html.H4(
                f"CS Course Delivery Modality AND the presence of extra CS-certified teachers"),
            html.H5(f"High Schools [{total_schools}]"),
            html.Ul(course_legend_items)
        ])

    # Disparity section
    elif selected_filter == "Disparity" and selected_disparity:
        if selected_disparity in data.columns:
            disparity_data = filtered_data[filtered_data[selected_disparity].notna()].copy(
            )

            low_values = disparity_data[disparity_data[selected_disparity]
                                        < -0.05][selected_disparity]
            high_values = disparity_data[disparity_data[selected_disparity]
                                         > 0.05][selected_disparity]

            if not low_values.empty:
                low_bins = pd.qcut(low_values, 3, retbins=True,
                                   duplicates="drop")[1]
            else:
                low_bins = [-float('inf'), -0.05]

            if not high_values.empty:
                high_bins = pd.qcut(
                    high_values, 3, retbins=True, duplicates="drop")[1]
            else:
                high_bins = [0.05, float('inf')]

            bins = list(low_bins[:-1]) + [-0.05, 0.05] + list(high_bins[1:])

            adjusted_labels = []
            if len(low_bins) > 1:
                adjusted_labels += ["Dark Red", "Red",
                                    "Light Red"][:len(low_bins) - 1]
            adjusted_labels += ["White"]
            if len(high_bins) > 1:
                adjusted_labels += ["Light Green", "Green",
                                    "Dark Green"][:len(high_bins) - 1]

            disparity_data['Disparity_Category'] = pd.cut(
                disparity_data[selected_disparity], bins=bins, labels=adjusted_labels, include_lowest=True
            )

            category_counts = disparity_data['Disparity_Category'].value_counts(
                sort=False)

            disparity_legend_items = []
            for i, (count, color) in enumerate(zip(
                    category_counts,
                    DISPARITY_COLORS[:len(adjusted_labels)])):
                disparity_legend_items.append(html.Li([
                    html.Div(style={
                        "backgroundColor": color,
                        "width": "12px",
                        "height": "12px",
                        "display": "inline-block",
                        "border": "1px solid black" if color == "white" else "none",
                        "marginRight": "8px",
                        "borderRadius": "50%"
                    }),
                    f"{bins[i]*100:.2f}% to {bins[i+1]*100:.2f}% [{count}]"
                ]))

            legend_content = html.Div([
                html.H4(f"{selected_disparity.replace(
                    'Disparity_', '')} disproportion index"),
                html.H5(f"High Schools [{len(disparity_data)}]"),
                html.Ul(disparity_legend_items)
            ])

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
                            row[selected_disparity]*100:.2f}%</b><br>"
                        + "<br>".join(
                            f"{col.replace('Disparity_', '')} Disparity: {
                                row[col]*100:.2f}%"
                            for col in DISPARITY_COLUMNS if col != selected_disparity
                        )
                    ),
                    axis=1
                )
            ))

    # Update layout
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

if __name__ == "__main__":
    app.run_server(debug=True)
