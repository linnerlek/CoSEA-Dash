# Paths
GEOJSON_PATH = "./data/georgia.geojson"
DATA_PATH = "./data/dataset.csv"

# Disparity column names
DISPARITY_COLUMNS = sorted(
    ["Disparity_Asian", "Disparity_Black", "Disparity_Hispanic", "Disparity_White"]
)

# Disparity Color mappings
# Color mappings based on (p.7.1.7) Methodology Draft 01/16/2025
DISPARITY_COLORS = [
    "darkred", "red", "lightcoral", "white", "lightgreen", "green", "#004d00"
]

# Filter options
FILTER_OPTIONS = [
    {"label": "Modality", "value": "Logic_Class"},
    {"label": "Certification", "value": "Course_Offered"},
    {"label": "Disparity", "value": "Disparity"},
]

# Modality Color mappings
# Color mappings based on (p.7.1.2) Methodology Draft 01/16/2025
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
    }
}

# CS-Certified Color mappings
# Color mappings based on (p.11 Figure 5) Methodology Draft 01/16/2025
COURSE_OFFERED_COLORS = {
    "0,0,0": "red",
    "0,0,1": "red",
    "0,1,0": "purple",
    "0,1,1": "purple",
    "1,1,1": "blue",
    "1,1,0": "blue",
    "1,0,1": "green",
    "1,0,0": "green",
}

# Which plots are triangle shaped for CS-Certified
# based on (p.11 Figure 5) Methodology Draft 01/16/2025
TRIANGLE_SHAPES = {"0,0,1", "1,0,1", "0,1,1", "1,1,1"}


# Map overlay options
MAP_OVERLAY_OPTIONS = [
    {"label": "Show County Lines", "value": "county_lines"},
]
