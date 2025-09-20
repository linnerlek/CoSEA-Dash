from dash.dash import no_update
from dash.dependencies import State
from dash.dependencies import ALL
import dash
from dash import dcc, html, Input, Output
from dash.dependencies import Output as DOutput
import plotly.graph_objs as go
import pandas as pd
from shapely.geometry import Point
from sqlalchemy import create_engine
import data_loader
import warnings
warnings.filterwarnings(
    "ignore",
    message="Parsing dates involving a day of month without a year specified is ambiguious",
    category=DeprecationWarning,
)


# Database connection (for school/modalities only)
engine = create_engine(
    "postgresql+psycopg2://cosea_user:CoSeaIndex@pgsql.dataconn.net:5432/cosea_db"
)

# Dash app setup
app = dash.Dash(__name__)


# Sidebar overlay options
overlay_options = [
    {"label": "Show Modalities", "value": "modalities"},
    {"label": "Show County Lines", "value": "counties"},
    {"label": "Show Highways", "value": "highways"},
]

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id="main-map",
            className="main-map-graph",
            config={"displayModeBar": False}
        ),
        html.Div(
            id="custom-legend-container",
            className="custom-legend-container"
        )
    ], className="main-map-area"),
    html.Div([
        html.H3("Map Options", className="sidebar-title"),
        dcc.Checklist(
            id="map-options-toggle",
            options=[
                {"label": "Show Legend", "value": "show_legend"},
                {"label": "Highways", "value": "highways"},
                {"label": "County Lines", "value": "counties"},
            ],
            value=["show_legend", "highways", "counties"],
            className="sidebar-legend-toggle"
        ),
        html.Div([
            html.Strong("School Dots"),
            dcc.RadioItems(
                id="school-toggles",
                options=[
                    {"label": "Course Modality", "value": "modalities"},
                    {"label": "Representation Index", "value": "disparity"},
                ],
                value="modalities",
                className="sidebar-school-toggles"
            ),
            html.Label(id="dots-dropdown-label",
                       className="sidebar-dots-dropdown-label"),
            dcc.Dropdown(
                id="dots-dropdown",
                options=[],
                value=None,
                clearable=False,
                className="sidebar-dots-dropdown"
            ),
        ], className="sidebar-section"),
        # Removed 'Dots Filter' and 'Population & Access' options that were marked as coming soon
    ], className="sidebar"),
], className="app-root")

# Callback to update map based on toggles

# Add callback to update dropdown options and label based on school-toggles


@app.callback(
    [DOutput("dots-dropdown", "options"), DOutput("dots-dropdown",
                                                  "value"), DOutput("dots-dropdown-label", "children")],
    [Input("school-toggles", "value")]
)
def update_dots_dropdown(school):
    if school == "modalities":
        options = [
            {"label": "Modality", "value": "LOGIC_CLASS"},
            {"label": "Expanded Modality", "value": "LOGIC_CLASS_2"},
        ]
        value = "LOGIC_CLASS"
        label = "Modality Type"
    elif school == "disparity":
        options = [
            {"label": "Black", "value": "RI_Black"},
            {"label": "Asian", "value": "RI_Asian"},
            {"label": "Hispanic", "value": "RI_Hispanic"},
            {"label": "White", "value": "RI_White"},
            {"label": "Female", "value": "RI_Female"},
        ]
        value = "RI_Black"
        label = "RI Category"
    else:
        options = []
        value = None
        label = ""
    return options, value, label


@app.callback(
    [
        Output("main-map", "figure"),
        Output("custom-legend-container", "children"),
    ],
    [
        Input("map-options-toggle", "value"),
        Input("school-toggles", "value"),
        Input("dots-dropdown", "value"),
    ]
)
def update_map(map_options, school, dots_dropdown):

    fig = go.Figure()
    # Always show Georgia state outline (on top, black line)
    outline_lon = []
    outline_lat = []
    for x, y in data_loader.GEODATA["ga_outline"]:
        outline_lon.extend(x + [None])
        outline_lat.extend(y + [None])
    fig.add_trace(go.Scattermapbox(
        lon=outline_lon, lat=outline_lat, mode="lines",
        # slightly thicker than county lines (0.5)
        line=dict(color="black", width=1),
        opacity=1.0,
        name="Georgia Outline", showlegend=False, visible=True,
        hoverinfo="skip"
    ))

    # County lines (preloaded, combined trace, match map1.py)
    if "counties" in map_options:
        all_lon = []
        all_lat = []
        for x, y in data_loader.GEODATA["county_lines"]:
            all_lon.extend(x + [None])
            all_lat.extend(y + [None])
        fig.add_trace(go.Scattermapbox(
            lon=all_lon, lat=all_lat, mode="lines",
            line=dict(color="gray", width=0.5),
            opacity=0.5,
            name="County Lines", showlegend=True, visible=True,
            hoverinfo="skip"
        ))

    # Highways overlay (preloaded, combined trace, match map1.py)
    if "highways" in map_options:
        all_lon = []
        all_lat = []
        for x, y in data_loader.GEODATA["highway_lines"]:
            all_lon.extend(x + [None])
            all_lat.extend(y + [None])
        fig.add_trace(go.Scattermapbox(
            lon=all_lon, lat=all_lat, mode="lines",
            line=dict(color="gray", width=1),
            opacity=0.9,
            name="Highways", showlegend=True, visible=True,
            hoverinfo="skip"
        ))
    legend_html = None
    legend_extra = None
    # --- Dots legend logic (legend_html) ---
    if school == "modalities":
        modality_type = dots_dropdown
        # Use preloaded school data for modalities and join with coordinates
        merged = data_loader.SCHOOLDATA["gadoe"].copy()
        coords = data_loader.SCHOOLDATA["approved_all"][[
            "UNIQUESCHOOLID", "SCHOOL_NAME", "lat", "lon"]]
        merged = merged.merge(coords, on="UNIQUESCHOOLID", how="left")
        logic_col = modality_type

        def classify(logic_class):
            if logic_class.startswith("11"):
                return "Both"
            elif logic_class.startswith("10"):
                return "In Person"
            elif logic_class.startswith("01"):
                return "Virtual"
            else:
                return "No"
        merged["Classification"] = merged[logic_col].apply(classify)
        color_map = {
            "Both": "#47CEF5",
            "In Person": "#F54777",
            "Virtual": "#FFB300",
            "No": "#636363"
        }
        modality_labels = {
            "Both": "In Person and Virtual",
            "In Person": "In Person Only",
            "Virtual": "Virtual Only",
            "No": "No approved CS Class"
        }
        modality_counts = merged["Classification"].value_counts()
        # Use safe class names for legend dots
        modality_class_map = {
            "Both": "both",
            "In Person": "in-person",
            "Virtual": "virtual",
            "No": "no"
        }
        for modality, color in color_map.items():
            df = merged[merged["Classification"] == modality].copy()
            # Replace missing/None with 'N/A' for display
            df["CS_Enrollment"] = df["CS_Enrollment"].apply(
                lambda x: int(x) if pd.notnull(x) else 0)
            df["Certified_Teachers"] = df["Certified_Teachers"].apply(
                lambda x: int(x) if pd.notnull(x) else 0)

            # Compute student_teacher_ratio safely
            df["student_teacher_ratio"] = df.apply(
                lambda row: row["CS_Enrollment"] / row["Certified_Teachers"]
                if row["Certified_Teachers"] not in [0, None, "", float('nan')] else 0.0,
                axis=1
            )

            def ratio_fmt(val):
                if pd.isnull(val) or val is None:
                    return '0.0 students per teacher'
                try:
                    return f"{val:.1f} students per teacher"
                except Exception:
                    return '0.0 students per teacher'
            df["ratio_display"] = df["student_teacher_ratio"].apply(ratio_fmt)
            # Underline school name in hover
            df["school_hover"] = df["SCHOOL_NAME"].apply(
                lambda x: f"<u>{x}</u>")
            fig.add_trace(go.Scattermapbox(
                lon=df["lon"], lat=df["lat"],
                mode="markers", marker=dict(size=8, color=color, opacity=0.5),
                name="",
                visible=True,
                showlegend=False,
                hovertemplate=(
                    "%{customdata[0]}<br>CS Students: %{customdata[1]}<br>Certified Teachers: %{customdata[2]}<br>Student-Teacher Ratio: %{customdata[3]}"
                ),
                customdata=df[["school_hover", "CS_Enrollment",
                               "Certified_Teachers", "ratio_display"]].values
            ))
        if "show_legend" in map_options:
            # Dynamic legend title for modalities
            modality_title = "Modality" if modality_type == "LOGIC_CLASS" else "Expanded Modality"
            legend_html = html.Div([
                html.Div(modality_title, className="legend-title"),
                html.Div([
                    html.Div([
                        html.Span(
                            className=f"legend-dot legend-dot-{modality_class_map[k]}"),
                        html.Span(
                            f"{modality_labels[k]} ({modality_counts.get(k, 0)})", className="legend-dot-label")
                    ], className="legend-dot-row")
                    for k in color_map
                ], className="legend-dot-row-wrap")
            ], className="legend-block legend-modality-block")
    elif school == "disparity":
        legend_items = []
        disparity_col = dots_dropdown
        schools = data_loader.SCHOOLDATA["approved_all"][[
            "UNIQUESCHOOLID", "SCHOOL_NAME", "lat", "lon"]].copy()
        # Get all RI values from joined table
        ri_cols = ["RI_Asian", "RI_Black",
                   "RI_Hispanic", "RI_White", "RI_Female"]
        query = f'SELECT "UNIQUESCHOOLID", {', '.join([f'"{col}"' for col in ri_cols])
                                            } FROM census.gadoe2024_389'
        disparity = pd.read_sql(query, engine)
        schools = schools.merge(disparity, on="UNIQUESCHOOLID", how="inner")

        # Strict binning for RI using pd.cut (always 5 bins: 2 below, parity, 2 above)
        vals = pd.to_numeric(schools[disparity_col], errors='coerce')
        # Compute bin edges with uniqueness and fallback logic
        below_vals = vals[vals < -0.05]
        above_vals = vals[vals > 0.05]
        eps = 1e-6
        # Below parity edges
        if len(below_vals) > 1:
            min_below = below_vals.min()
            max_below = below_vals.max()
            mid_below = (min_below + max_below) / 2
            below_edges = [min_below, mid_below]
        elif len(below_vals) == 1:
            min_below = max_below = below_vals.iloc[0]
            below_edges = [min_below, min_below + eps]
        else:
            below_edges = [-0.05, -0.05 + eps]

        # Above parity edges
        if len(above_vals) > 1:
            min_above = above_vals.min()
            max_above = above_vals.max()
            mid_above = (min_above + max_above) / 2
            above_edges = [0.05, mid_above, max_above]
            # Use only the last two for bin_edges
            above_edges = [above_edges[1], above_edges[2]]
        elif len(above_vals) == 1:
            min_above = max_above = above_vals.iloc[0]
            above_edges = [min_above, min_above + eps]
        else:
            above_edges = [0.05, 0.05 + eps]

        # Build bin edges, ensuring strictly increasing
        bin_edges = [below_edges[0], below_edges[1], -
                     0.05, 0.05, above_edges[0], above_edges[1]]
        # Guarantee strictly increasing
        for i in range(1, len(bin_edges)):
            if bin_edges[i] <= bin_edges[i-1]:
                bin_edges[i] = bin_edges[i-1] + eps
        # Bin labels and colors (strict order)
        bin_labels = [
            f"{bin_edges[0]:.4f} to {bin_edges[1]:.4f}",
            f"{bin_edges[1]:.4f} to -0.0500",
            "-0.0500 to 0.0500",
            f"0.0500 to {bin_edges[4]:.4f}",
            f"{bin_edges[4]:.4f} to {bin_edges[5]:.4f}"
        ]
        # Strict color order: dark red, light red, white, light blue, dark blue
        bin_colors = ['#7f2704', '#fdae6b', '#ffffff', '#9ecae1', '#08519c']
        # Assign bins using pd.cut
        schools['RI_bin'] = pd.cut(
            vals,
            bins=bin_edges,
            labels=range(5),
            include_lowest=True,
            right=True
        )
        # Assign color by bin
        schools['Color'] = schools['RI_bin'].map(
            lambda x: bin_colors[int(x)] if pd.notnull(x) else None)

        # Plot each bin's dots, using strict bin assignment
        # Plot white (parity) dots first so they appear below other dots
        # 1. Plot parity bin (white) first
        i_parity = 2
        color = bin_colors[i_parity]
        label = bin_labels[i_parity]
        df = schools[schools['RI_bin'] == i_parity].copy()
        if not df.empty:
            def make_ri_hover(row):
                base = f"<u>{row['SCHOOL_NAME']}</u><br>"
                ri_lines = []
                for col in ri_cols:
                    val = row[col]
                    if col == disparity_col:
                        ri_lines.append(
                            f"<b>{col.replace('RI_', '')} RI: {val:.4f}</b>")
                    else:
                        ri_lines.append(
                            f"{col.replace('RI_', '')} RI: {val:.4f}")
                return base + "<br>".join(ri_lines)
            df["ri_hover"] = df.apply(make_ri_hover, axis=1)
            outline_size = 8
            white_size = 6
            fig.add_trace(go.Scattermapbox(
                lon=df['lon'], lat=df['lat'],
                mode='markers', marker=dict(size=outline_size, color='black', opacity=0.7),
                name=None, visible=True, showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scattermapbox(
                lon=df['lon'], lat=df['lat'],
                mode='markers', marker=dict(size=white_size, color='#ffffff', opacity=0.95),
                name="", visible=True, showlegend=False,
                hovertemplate="%{customdata[0]}",
                customdata=df[["ri_hover"]].values
            ))
        # 2. Plot all other bins (except parity)
        for i in [0, 1, 3, 4]:
            color = bin_colors[i]
            label = bin_labels[i]
            df = schools[schools['RI_bin'] == i].copy()
            if not df.empty:
                def make_ri_hover(row):
                    base = f"<u>{row['SCHOOL_NAME']}</u><br>"
                    ri_lines = []
                    for col in ri_cols:
                        val = row[col]
                        if col == disparity_col:
                            ri_lines.append(
                                f"<b>{col.replace('RI_', '')} RI: {val:.4f}</b>")
                        else:
                            ri_lines.append(
                                f"{col.replace('RI_', '')} RI: {val:.4f}")
                    return base + "<br>".join(ri_lines)
                df["ri_hover"] = df.apply(make_ri_hover, axis=1)
                fig.add_trace(go.Scattermapbox(
                    lon=df['lon'], lat=df['lat'],
                    mode='markers', marker=dict(size=8, color=color, opacity=0.8),
                    name="", visible=True, showlegend=False,
                    hovertemplate="%{customdata[0]}",
                    customdata=df[["ri_hover"]].values
                ))
        # Build legend (always show all five bins, in strict order, even if count is zero)
        legend_items = []
        for i in range(5):
            color = bin_colors[i]
            label = bin_labels[i]
            count = (schools['RI_bin'] == i).sum()
            legend_items.append(html.Div([
                html.Span(style={
                    "backgroundColor": color,
                    "width": "12px",
                    "height": "12px",
                    "display": "inline-block",
                    "border": "1px solid black" if color == "#ffffff" else "none",
                    "marginRight": "8px",
                    "borderRadius": "50%"
                }),
                html.Span(f"{label} ({count} schools)",
                          className="legend-dot-label")
            ], className="legend-dot-row"))
        if "show_legend" in map_options:
            disparity_titles = {
                "RI_Black": "Black Representation Index",
                "RI_Asian": "Asian Representation Index",
                "RI_Hispanic": "Hispanic Representation Index",
                "RI_White": "White Representation Index",
                "RI_Female": "Female Representation Index"
            }
            legend_title = disparity_titles.get(
                disparity_col, "Representation Index")
            legend_html = html.Div([
                html.Div(legend_title, className="legend-title"),
                html.Div([
                    html.Div(item, className="legend-dot-row")
                    for item in legend_items
                ], className="legend-dot-row-wrap")
            ], className="legend-block legend-disparity-block")
    elif school == "gender":
        # Dots dropdown: RI_Female, RI_Male
        gender_col = dots_dropdown
        school_query = f"SELECT s.\"UNIQUESCHOOLID\", s.lat, s.lon, g.\"{gender_col}\" FROM \"allhsgrades24\".\"tbl_approvedschools\" s JOIN census.gadoe2024_389 g ON s.\"UNIQUESCHOOLID\" = g.\"UNIQUESCHOOLID\" WHERE s.lat IS NOT NULL AND s.lon IS NOT NULL"
        schools = pd.read_sql(school_query, engine)
        # Use bins from map3.py for female, similar for male
        if gender_col == "RI_Female":
            color_bins = [(-0.864929, -0.296520, '#7f2704'),
                          (-0.296519, -0.211112, '#d94801'),
                          (-0.211111, -0.051748, '#fdae6b'),
                          (-0.051747, 0.032609, '#ffffff'),
                          (0.034510, 0.257576, '#9ecae1'),
                          (0.257577, 0.497095, '#3182bd'),
                          (0.497096, 0.652174, '#08519c')]
            legend_labels = [
                '-0.864929 to -0.296520',
                '-0.296519 to -0.211112',
                '-0.211111 to -0.051748',
                '-0.051747 to 0.032609',
                '0.034510 to 0.257576',
                '0.257577 to 0.497095',
                '0.497096 to 0.652174'
            ]
        else:  # RI_Male
            color_bins = [(-0.864929, -0.296520, '#7f2704'),
                          (-0.296519, -0.211112, '#d94801'),
                          (-0.211111, -0.051748, '#fdae6b'),
                          (-0.051747, 0.032609, '#ffffff'),
                          (0.034510, 0.257576, '#9ecae1'),
                          (0.257577, 0.497095, '#3182bd'),
                          (0.497096, 0.652174, '#08519c')]
            legend_labels = [
                '-0.864929 to -0.296520',
                '-0.296519 to -0.211112',
                '-0.211111 to -0.051748',
                '-0.051747 to 0.032609',
                '0.034510 to 0.257576',
                '0.257577 to 0.497095',
                '0.497096 to 0.652174'
            ]

        def get_color(val):
            for b in color_bins:
                if b[0] <= val <= b[1]:
                    return b[2]
            return None
        schools['Color'] = pd.to_numeric(
            schools[gender_col], errors='coerce').apply(get_color)
        for i, (low, high, color) in enumerate(color_bins):
            df = schools[schools['Color'] == color]
            fig.add_trace(go.Scattermapbox(
                lon=df['lon'], lat=df['lat'],
                mode='markers', marker=dict(size=8, color=color, opacity=0.8),
                name=f"{legend_labels[i]} ({len(df)})",
                visible=True,
                showlegend=False,
                hovertemplate=df["SCHOOL_NAME"] if "SCHOOL_NAME" in df.columns else None
            ))
    # (No-op: legend_html for modalities is now only built in the modalities branch above)

    # Mapbox settings
    fig.update_layout(
        mapbox_style="white-bg",  # blank basemap
        mapbox_zoom=6.5,
        mapbox_center={"lat": 32.9, "lon": -83.5},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    # --- Always show overlay legend if overlays are enabled ---
    overlay_legend = None
    if "show_legend" in map_options:
        overlay_items = []
        if "counties" in map_options:
            overlay_items.append(
                html.Div([
                    html.Span(
                        className="legend-overlay-line legend-overlay-county"),
                    html.Span("County Boundaries",
                              className="legend-overlay-label")
                ], className="legend-overlay-row legend-overlay-county-row")
            )
        if "highways" in map_options:
            overlay_items.append(
                html.Div([
                    html.Span(
                        className="legend-overlay-line legend-overlay-highway"),
                    html.Span("Interstate Highways",
                              className="legend-overlay-label")
                ], className="legend-overlay-row legend-overlay-highway-row")
            )
        if overlay_items:
            overlay_legend = html.Div(
                overlay_items,
                className="legend-block legend-overlay-block"
            )

    # Combine both legends into one container for side-by-side display
    legend_combined = None
    if legend_html and overlay_legend:
        legend_combined = [
            html.Div(legend_html, className="legend-flex-8"),
            html.Div(overlay_legend, className="legend-flex-2")
        ]
    elif legend_html:
        legend_combined = [
            html.Div(legend_html, className="legend-full-width")]
    elif overlay_legend:
        legend_combined = [
            html.Div(overlay_legend, className="legend-full-width")]
    else:
        legend_combined = None
    return fig, legend_combined


if __name__ == "__main__":
    app.run(debug=True)
