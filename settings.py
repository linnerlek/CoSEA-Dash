# ---------- LABELS ----------
MODALITY_LABELS = {
    "Both": "In Person and Virtual",
    "In Person": "In Person Only",
    "Virtual": "Virtual Only",
    "No": "No approved CS Class"
}
MODALITY_CLASS_MAP = {
    "Both": "both",
    "In Person": "in-person",
    "Virtual": "virtual",
    "No": "no"
}

LABELS = {
    "overlay_options": [
        {"label": "Show Modalities", "value": "modalities"},
        {"label": "Show County Lines", "value": "counties"},
        {"label": "Show Highways", "value": "highways"},
    ],
    "map_options": [
        {"label": "Show Legend", "value": "show_legend"},
        {"label": "Highways", "value": "highways"},
        {"label": "County Lines", "value": "counties"},
    ],
    "sidebar_title": "Map Options",
    "school_dots": "School Dots",
    "school_toggles": [
        {"label": "Course Modality", "value": "modalities"},
        {"label": "Representation Index", "value": "disparity"},
    ],
    "dots_dropdown_label_modality": "Modality Type",
    "dots_dropdown_label_disparity": "RI Category",
    "dots_dropdown_options_modality": [
        {"label": "Modality", "value": "LOGIC_CLASS"},
        {"label": "Expanded Modality", "value": "LOGIC_CLASS_2"},
    ],
    "dots_dropdown_options_disparity": [
        {"label": "Asian", "value": "RI_Asian"},
        {"label": "Black", "value": "RI_Black"},
        {"label": "Hispanic", "value": "RI_Hispanic"},
        {"label": "White", "value": "RI_White"},
        {"label": "Female", "value": "RI_Female"},
    ],
    "legend_titles": {
        "modality": "Modality",
        "expanded_modality": "Expanded Modality",
        "RI_Black": "Black Representation Index",
        "RI_Asian": "Asian Representation Index",
        "RI_Hispanic": "Hispanic Representation Index",
        "RI_White": "White Representation Index",
        "RI_Female": "Female Representation Index",
        "default": "Representation Index"
    },
    "overlay_legend": {
        "county": "County Boundaries",
        "highway": "Interstate Highways"
    }
}

# ---------- HOVER INFO ----------
HOVER_TEMPLATES = {
    "modality": (
        "<u>{SCHOOL_NAME}</u><br>"
        "Grades: {GRADE_RANGE}<br>"
        "Approved Courses: {approved}<br>"
        "Virtual: {virtual} | In-Person: {inperson}<br>"
        "---<br>"
        "CS Students: {CS_Enrollment}<br>"
        "Certified Teachers: {Certified_Teachers}<br>"
        "Student-Teacher Ratio: {ratio_display}"
    ),
    "disparity_female": (
        "<u>{SCHOOL_NAME}</u><br>"
        "Grades: {GRADE_RANGE}<br>"
        "Total Student Count: {Total_Student_Count}<br>"
        "Total Female: {Female}<br>"
        "Total Male: {Male}<br>"
        "---<br>"
        "CS Students: {CS_Enrollment}<br>"
        "CS Female: {CS_Female}<br>"
        "CS Male: {CS_Male}<br>"
        "---<br>"
        "<b>RI Female: {RI_Female:.4f}</b>"
    ),
    "disparity_race": (
        "<u>{SCHOOL_NAME}</u><br>"
        "Grades: {GRADE_RANGE}<br>"
        "Total Student Count: {Total_Student_Count}<br>"
        "{total_race_vals}<br>"
        "---<br>"
        "CS Enrollment: {CS_Enrollment}<br>"
        "{cs_race_vals}<br>"
        "---<br>"
        "{ri_vals}"
    )
}
# ---------- COLORS ----------
MODALITY_COLOR_MAP = {
    "Both": "#47CEF5",
    "In Person": "#F54777",
    "Virtual": "#FFB300",
    "No": "#636363"
}

RI_BIN_COLORS = ['#7f2704', '#fdae6b', '#ffffff', '#9ecae1', '#08519c']

GENDER_COLOR_BINS = [
    (-0.864929, -0.296520, '#7f2704'),
    (-0.296519, -0.211112, '#d94801'),
    (-0.211111, -0.051748, '#fdae6b'),
    (-0.051747, 0.032609, '#ffffff'),
    (0.034510, 0.257576, '#9ecae1'),
    (0.257577, 0.497095, '#3182bd'),
    (0.497096, 0.652174, '#08519c')
]

# ---------- DATABASE LINK ----------
DATABASE_URL = "postgresql+psycopg2://cosea_user:CoSeaIndex@pgsql.dataconn.net:5432/cosea_db"

# ---------- SHAPEFILES ----------
GA_OSM_QUERY = "Georgia, USA"
COUNTY_SHAPEFILE_URL = "https://www2.census.gov/geo/tiger/TIGER2022/COUNTY/tl_2022_us_county.zip"
ROAD_SHAPEFILE_URL = "https://www2.census.gov/geo/tiger/TIGER2022/PRIMARYROADS/tl_2022_us_primaryroads.zip"

# ---------- DEFAULTS ----------
DEFAULT_MAP_OPTIONS = ["show_legend", "highways", "counties"]
DEFAULT_SCHOOL_TOGGLE = "modalities"
DEFAULT_DOTS_DROPDOWN_MODALITIES = "LOGIC_CLASS"
DEFAULT_DOTS_DROPDOWN_DISPARITY = "RI_Asian"
DEFAULT_UNDERLAY_OPTION = "none"

UNDERLAY_OPTIONS = [
    {"label": "None", "value": "none"},
    {"label": "Black Population Ratio (ACS)",
     "value": "black_population_ratio"}
]
