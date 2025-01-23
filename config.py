# TIGERweb base URL
TIGERWEB_BASE_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer"

# Census API details
CENSUS_API_URL = "https://api.census.gov/data/2023/acs/acs5"
# Request key at: https://api.census.gov/data/key_signup.html the email might take a while, i had to use gmail
CENSUS_API_KEY = "YOUR KEY HERE"

# File paths
DATA_PATH = "./data/dataset.csv"

# Filter options
FILTER_OPTIONS = [
    {"label": "None", "value": "None"},
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

ORDERED_LOGIC_CLASSES = [
    "0,0,0", "0,0,1", "0,1,0", "0,1,1",
    "1,0,0", "1,0,1", "1,1,0", "1,1,1"
]

# Triangle shapes for CS-Certified teachers
TRIANGLE_SHAPES = {"0,0,1", "1,0,1", "0,1,1", "1,1,1"}

# Default figure layout
FIGURE_LAYOUT = {
    "geo": {
        "showcoastlines": False,
        "showland": False,
        "showframe": False,
        "showocean": False,
        "fitbounds": "locations",
        "resolution": 50,
        "scope": "usa",
    },
    "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
    "showlegend": False,
}
