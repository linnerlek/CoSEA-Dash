# Paths
GEOJSON_PATH = "./data/georgia.geojson"
DATA_PATH = "./data/dataset.csv"

# Filter options
FILTER_OPTIONS = [
    {"label": "Modality", "value": "Logic_Class"},
    {"label": "Certification", "value": "Course_Offered"},
    {"label": "Disparity", "value": "Disparity"},
]

# Disparity column values
DISPARITY_COLUMNS = sorted(
    ["Disparity_Asian", "Disparity_Black", "Disparity_Hispanic", "Disparity_White"]
)

# Disparity Color gradient
DISPARITY_COLORS = [
    "darkred", "red", "lightcoral", "white", "lightgreen", "green", "#004d00"
]

# Color mappings
COLOR_MAPPINGS = {
    "Logic_Class": {
        "0,0,0": "red",
        "0,0,1": "red",
        "0,1,0": "orange",
        "0,1,1": "orange",
        "1,0,0": "green",
        "1,0,1": "green",
        "1,1,0": "purple",
        "1,1,1": "purple",
    },
    "Course_Offered": {
        "0,0,0": "red",
        "0,0,1": "red",
        "0,1,0": "purple",
        "0,1,1": "purple",
        "1,0,0": "green",
        "1,0,1": "green",
        "1,1,0": "blue",
        "1,1,1": "blue",
    },
}

# Triangle shaped plots for CS-Certified teachers
TRIANGLE_SHAPES = {"0,0,1", "1,0,1", "0,1,1", "1,1,1"}

# Map overlay options
MAP_OVERLAY_OPTIONS = [
    {"label": "Show County Lines", "value": "county_lines"},
]
