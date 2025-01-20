from dash import html
import pandas as pd
import plotly.graph_objects as go
from config import *


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


def create_modality_legend(fig, filtered_data):
    total_schools, class_counts = calculate_total_schools(
        filtered_data, COLOR_MAPPINGS["Logic_Class"].keys())
    legend_items = []

    for value, color in COLOR_MAPPINGS["Logic_Class"].items():
        if value in class_counts:
            count = class_counts[value]
            legend_items.append(html.Li([
                html.Div(style={
                    "backgroundColor": color,
                    "width": "12px",
                    "height": "12px",
                    "display": "inline-block",
                    "marginRight": "8px",
                    "borderRadius": "50%"
                }),
                f"{filtered_data[filtered_data['Logic_Class'] == value]
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
        html.Ul(legend_items)
    ])

    return fig, legend_content


def create_course_legend(fig, filtered_data):
    total_schools, class_counts = calculate_total_schools(
        filtered_data, COLOR_MAPPINGS["Course_Offered"].keys())
    legend_items = []

    for value, color in COLOR_MAPPINGS["Course_Offered"].items():
        if value in class_counts:
            count = class_counts[value]
            legend_items.append(html.Li([
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

            course_data = filtered_data[filtered_data["Logic_Class"] == value].copy(
            )
            fig.add_trace(go.Scattergeo(
                lon=course_data["X"],
                lat=course_data["Y"],
                mode="markers",
                marker=dict(
                    size=12 if value in TRIANGLE_SHAPES else 8,
                    color=color,
                    symbol="triangle-up" if value in TRIANGLE_SHAPES else "circle"
                ),
                hoverinfo="text",
                text=course_data.apply(
                    lambda row: f"School: {row['School_Name']}<br>Course Offered: {
                        row['School_Classification']}<br>Total Students: {row['Total_Student_Count']}",
                    axis=1
                )
            ))

    legend_content = html.Div([
        html.H4(
            "CS Course Delivery Modality AND the presence of extra CS-certified teachers"),
        html.H5(f"High Schools [{total_schools}]"),
        html.Ul(legend_items)
    ])

    return fig, legend_content


def create_disparity_legend(fig, filtered_data, selected_disparity):
    # Ensure the selected_disparity exists in the data
    if selected_disparity not in filtered_data.columns:
        return fig, html.Div(["No data available for the selected disparity."])

    # Filter data for non-null disparity values
    disparity_data = filtered_data[filtered_data[selected_disparity].notna()].copy(
    )

    # Separate low and high values
    low_values = disparity_data[disparity_data[selected_disparity]
                                < -0.05][selected_disparity]
    high_values = disparity_data[disparity_data[selected_disparity]
                                 > 0.05][selected_disparity]

    # Bin the values into ranges
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

    # Map the adjusted labels to the data
    disparity_data['Disparity_Category'] = pd.cut(
        disparity_data[selected_disparity], bins=bins, labels=adjusted_labels, include_lowest=True
    )

    # Generate the legend content
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

    # Add data points to the map
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

    # Return the updated figure and legend content
    legend_content = html.Div([
        html.H4(f"{selected_disparity.replace(
            'Disparity_', '')} Disproportion Index"),
        html.H5(f"High Schools [{len(disparity_data)}]"),
        html.Ul(legend_items)
    ])

    return fig, legend_content
