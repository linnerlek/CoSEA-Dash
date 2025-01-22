# Paths
GEORGIA_OUTLINE_PATH = "./data/shapefiles/tlgdb_2024_a_13_ga.gdb"
SECONDARY_SCHOOL_DISTRICTS_PATH = "./data/shapefiles/districts/tl_2024_13_scsd/tl_2024_13_scsd.shp"
UNIFIED_SCHOOL_DISTRICTS_PATH = "./data/shapefiles/districts/tl_2024_13_unsd/tl_2024_13_unsd.shp"
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
    "map_style": "satellite",
}
