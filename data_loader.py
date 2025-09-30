from settings import *
import os
import tempfile
import requests
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Polygon, MultiPolygon
from sqlalchemy import create_engine
import pandas as pd


def ratio_fmt(val):
    if pd.isnull(val) or val is None:
        return '0.0 students per teacher'
    try:
        return f"{val:.1f} students per teacher"
    except Exception:
        return '0.0 students per teacher'


def build_modality_hover(row, modality_type, HOVER_TEMPLATES):
    if modality_type == "LOGIC_CLASS_2":
        virtual = row['virtual_course_count_2'] if pd.notnull(
            row['virtual_course_count_2']) else 0
        inperson = row['inperson_course_count_2'] if pd.notnull(
            row['inperson_course_count_2']) else 0
        approved = row['approved_course_count_2'] if pd.notnull(
            row['approved_course_count_2']) else 0
    else:
        virtual = row['virtual_course_count'] if pd.notnull(
            row['virtual_course_count']) else 0
        inperson = row['inperson_course_count'] if pd.notnull(
            row['inperson_course_count']) else 0
        approved = row['approved_course_count'] if pd.notnull(
            row['approved_course_count']) else 0
    return HOVER_TEMPLATES["modality"].format(
        SCHOOL_NAME=row['SCHOOL_NAME'],
        GRADE_RANGE=row['GRADE_RANGE'] if pd.notnull(
            row['GRADE_RANGE']) else "",
        approved=approved,
        virtual=virtual,
        inperson=inperson,
        CS_Enrollment=row['CS_Enrollment'],
        Certified_Teachers=row['Certified_Teachers'],
        ratio_display=row['ratio_display']
    )


def make_ri_hover(row, disparity_col, ri_cols, HOVER_TEMPLATES):
    def safe_fmt(val, label, bold=False):
        if pd.isnull(val):
            return None
        txt = f"RI {label}: {val:.4f}"
        return f"<b>{txt}</b>" if bold else txt

    total_race_map = {
        "RI_Asian": ("Race: Asian", "Total Asian"),
        "RI_Black": ("Race: Black", "Total Black"),
        "RI_Hispanic": ("Ethnicity: Hispanic", "Total Hispanic"),
        "RI_White": ("Race: White", "Total White"),
    }

    if disparity_col == "RI_Female":
        return HOVER_TEMPLATES["disparity_female"].format(
            SCHOOL_NAME=row.get("SCHOOL_NAME", ""),
            GRADE_RANGE=row.get("GRADE_RANGE", ""),
            Total_Student_Count=row.get("Total Student Count", ""),
            Female=row.get("Female", ""),
            Male=row.get("Male", ""),
            CS_Enrollment=int(row.get("CS_Enrollment", 0)) if row.get(
                "CS_Enrollment", None) is not None else '',
            CS_Female=int(row.get("CS_Female", 0)) if row.get(
                "CS_Female", None) is not None else '',
            CS_Male=int(row.get("CS_Male", 0)) if row.get(
                "CS_Male", None) is not None else '',
            RI_Female=row.get("RI_Female", 0.0)
        )
    else:
        race_cols = [c for c in ri_cols if c != "RI_Female"]
        cs_race_cols = ["CS_Asian", "CS_Black", "CS_Hispanic", "CS_White"]
        ri_to_cs = {"RI_Asian": "CS_Asian", "RI_Black": "CS_Black",
                    "RI_Hispanic": "CS_Hispanic", "RI_White": "CS_White"}
        cs_race_labels = {
            "CS_Asian": "CS Asian",
            "CS_Black": "CS Black",
            "CS_Hispanic": "CS Hispanic",
            "CS_White": "CS White"
        }
        cs_race_vals = []
        for cs_col in cs_race_cols:
            val = row.get(cs_col, None)
            label = cs_race_labels.get(cs_col, cs_col)
            bold = (ri_to_cs.get(disparity_col) == cs_col)
            if val is not None:
                try:
                    val_int = int(val)
                except Exception:
                    val_int = val
                if bold:
                    cs_race_vals.append(f"<b>{label}: {val_int}</b>")
                else:
                    cs_race_vals.append(f"{label}: {val_int}")
        total_race_vals = []
        for ri_key, (total_col, total_label) in total_race_map.items():
            val = row.get(total_col, None)
            bold = (ri_key == disparity_col)
            if val is not None:
                if bold:
                    total_race_vals.append(f"<b>{total_label}: {val}</b>")
                else:
                    total_race_vals.append(f"{total_label}: {val}")
        total_students = row.get("Total Student Count", None)
        ri_vals = []
        for col in race_cols:
            val = row.get(col, None)
            if col == disparity_col:
                ri_vals.append(
                    safe_fmt(val, col.replace('RI_', ''), bold=True))
            else:
                ri_vals.append(safe_fmt(val, col.replace('RI_', '')))
        return HOVER_TEMPLATES["disparity_race"].format(
            SCHOOL_NAME=row.get("SCHOOL_NAME", ""),
            GRADE_RANGE=row.get("GRADE_RANGE", ""),
            Total_Student_Count=total_students if total_students is not None else '',
            total_race_vals='<br>'.join(total_race_vals),
            CS_Enrollment=int(row.get("CS_Enrollment", 0)) if row.get(
                "CS_Enrollment", None) is not None else '',
            cs_race_vals='<br>'.join(cs_race_vals),
            ri_vals='<br>'.join([v for v in ri_vals if v])
        )


def classify_modality(logic_class):
    if logic_class.startswith("11"):
        return "Both"
    elif logic_class.startswith("10"):
        return "In Person"
    elif logic_class.startswith("01"):
        return "Virtual"
    else:
        return "No"


def get_ri_bin_edges(vals, eps=1e-6):
    below_vals = vals[vals < -0.05]
    above_vals = vals[vals > 0.05]
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
    if len(above_vals) > 1:
        min_above = above_vals.min()
        max_above = above_vals.max()
        mid_above = (min_above + max_above) / 2
        above_edges = [0.05, mid_above, max_above]
        above_edges = [above_edges[1], above_edges[2]]
    elif len(above_vals) == 1:
        min_above = max_above = above_vals.iloc[0]
        above_edges = [min_above, min_above + eps]
    else:
        above_edges = [0.05, 0.05 + eps]
    bin_edges = [below_edges[0], below_edges[1], -
                 0.05, 0.05, above_edges[0], above_edges[1]]
    for i in range(1, len(bin_edges)):
        if bin_edges[i] <= bin_edges[i-1]:
            bin_edges[i] = bin_edges[i-1] + eps
    return bin_edges


def get_gender_color(val, color_bins):
    for b in color_bins:
        if b[0] <= val <= b[1]:
            return b[2]
    return None


engine = create_engine(DATABASE_URL)


def load_all_school_data():
    print("Loading school data...")
    gadoe = pd.read_sql('SELECT * FROM "census"."gadoe2024_389"', engine)

    course_logic = pd.read_sql(
        'SELECT * FROM "census"."course_logic_2024_389"', engine)

    approved_all = pd.read_sql(
        'SELECT * FROM "allhsgrades24"."tbl_approvedschools"', engine)

    approved_logic = course_logic[course_logic["approved_flag"] == True]
    modality_counts = approved_logic.groupby(
        ["UNIQUESCHOOLID", "is_virtual"]).size().unstack(fill_value=0).reset_index()
    modality_counts = modality_counts.rename(columns={
        True: "virtual_course_count",
        False: "inperson_course_count"
    })
    if "virtual_course_count" not in modality_counts:
        modality_counts["virtual_course_count"] = 0
    if "inperson_course_count" not in modality_counts:
        modality_counts["inperson_course_count"] = 0

    approved_logic2 = course_logic[course_logic["approved_flag_2"] == True]
    modality_counts2 = approved_logic2.groupby(
        ["UNIQUESCHOOLID", "is_virtual"]).size().unstack(fill_value=0).reset_index()
    modality_counts2 = modality_counts2.rename(columns={
        True: "virtual_course_count_2",
        False: "inperson_course_count_2"
    })
    if "virtual_course_count_2" not in modality_counts2:
        modality_counts2["virtual_course_count_2"] = 0
    if "inperson_course_count_2" not in modality_counts2:
        modality_counts2["inperson_course_count_2"] = 0

    approved_counts = approved_logic.groupby(
        "UNIQUESCHOOLID").size().reset_index(name="approved_course_count")
    approved_counts2 = approved_logic2.groupby(
        "UNIQUESCHOOLID").size().reset_index(name="approved_course_count_2")

    school_modality_info = approved_all[[
        "UNIQUESCHOOLID", "SCHOOL_NAME", "GRADE_RANGE", "lat", "lon"
    ]].merge(modality_counts, on="UNIQUESCHOOLID", how="left")
    school_modality_info = school_modality_info.merge(
        modality_counts2, on="UNIQUESCHOOLID", how="left")
    school_modality_info = school_modality_info.merge(
        approved_counts, on="UNIQUESCHOOLID", how="left")
    school_modality_info = school_modality_info.merge(
        approved_counts2, on="UNIQUESCHOOLID", how="left")
    for col in ["virtual_course_count", "inperson_course_count", "virtual_course_count_2", "inperson_course_count_2", "approved_course_count", "approved_course_count_2"]:
        if col in school_modality_info:
            school_modality_info[col] = school_modality_info[col].fillna(
                0).astype(int)

    ri_cols = ["RI_Asian", "RI_Black", "RI_Hispanic", "RI_White", "RI_Female"]
    cs_race_cols = ["CS_Asian", "CS_Black", "CS_Hispanic", "CS_White"]
    extra_cols = ["CS_Enrollment", "CS_Female", "CS_Male"] + cs_race_cols
    all_cols = ri_cols + extra_cols
    disparity_query = f'SELECT "UNIQUESCHOOLID", {', '.join([f'"{col}"' for col in all_cols])
                                                  } FROM census.gadoe2024_389'
    disparity = pd.read_sql(disparity_query, engine)

    gender_query = (
        'SELECT s."UNIQUESCHOOLID", s.lat, s.lon, g."RI_Female" '
        'FROM "allhsgrades24"."tbl_approvedschools" s '
        'JOIN census.gadoe2024_389 g ON s."UNIQUESCHOOLID" = g."UNIQUESCHOOLID" '
        'WHERE s.lat IS NOT NULL AND s.lon IS NOT NULL'
    )
    gender = pd.read_sql(gender_query, engine)

    # Load courses data
    approved_courses = course_logic[course_logic['approved_flag'] == 1]
    courses_grouped = approved_courses.groupby('UNIQUESCHOOLID')['COURSE_TITLE'].apply(list).reset_index()
    courses_dict = {str(k): v for k, v in zip(courses_grouped['UNIQUESCHOOLID'], courses_grouped['COURSE_TITLE'])}

    school_names = {str(k): v for k, v in zip(approved_all['UNIQUESCHOOLID'], approved_all['SCHOOL_NAME'])}

    return {
        "gadoe": gadoe,
        "course_logic": course_logic,
        "approved_all": approved_all,
        "school_modality_info": school_modality_info,
        "disparity": disparity,
        "gender": gender,
        "courses": courses_dict,
        "school_names": school_names
    }


def load_geodata():
    print("Loading geospatial data...")
    ga_boundary = ox.geocode_to_gdf(GA_OSM_QUERY).to_crs(epsg=4326)
    county_url = COUNTY_SHAPEFILE_URL
    county_zip = os.path.join(tempfile.gettempdir(), "tl_2022_us_county.zip")
    if not os.path.exists(county_zip):
        r = requests.get(county_url, verify=False)
        with open(county_zip, "wb") as f:
            f.write(r.content)
    counties = gpd.read_file(f"zip://{county_zip}")
    ga_counties = counties[counties["STATEFP"] == "13"].to_crs(epsg=4326)
    county_lines = []
    for _, row in ga_counties.iterrows():
        geom = row.geometry
        if isinstance(geom, Polygon):
            x, y = geom.exterior.xy
            county_lines.append((list(x), list(y)))
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                x, y = poly.exterior.xy
                county_lines.append((list(x), list(y)))
    road_url = ROAD_SHAPEFILE_URL
    road_zip = os.path.join(tempfile.gettempdir(),
                            "tl_2022_us_primaryroads.zip")
    if not os.path.exists(road_zip):
        r = requests.get(road_url, verify=False)
        with open(road_zip, "wb") as f:
            f.write(r.content)
    roads = gpd.read_file(f"zip://{road_zip}")
    interstates = roads[roads["RTTYP"] == "I"].to_crs(epsg=4326)
    interstates = gpd.clip(interstates, ga_boundary)
    highway_lines = []
    for _, row in interstates.iterrows():
        geom = row.geometry
        x, y = geom.xy
        highway_lines.append((list(x), list(y)))
    ga_outline = []
    for _, row in ga_boundary.iterrows():
        geom = row.geometry
        if isinstance(geom, Polygon):
            x, y = geom.exterior.xy
            ga_outline.append((list(x), list(y)))
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                x, y = poly.exterior.xy
                ga_outline.append((list(x), list(y)))
    return {
        "ga_boundary": ga_boundary,
        "county_lines": county_lines,
        "highway_lines": highway_lines,
        "ga_outline": ga_outline
    }


SCHOOLDATA = load_all_school_data()
GEODATA = load_geodata()


def load_cbg_underlay(selected_field, bins=5):
    """
    Load block group geometries and ACS data for the selected field.
    Returns GeoDataFrame with binned values for grayscale mapping.
    """
    # Load block group geometries
    block_query = (
        'SELECT "GEOID", cbgpolygeom AS geom FROM "allhsgrades24"."tbl_cbg_finalassignment"'
    )
    block_groups = gpd.read_postgis(block_query, engine, geom_col='geom')
    block_groups['GEOID'] = block_groups['GEOID'].astype(str).str.zfill(12)

    # Load ACS data for selected field
    acs_query = f'SELECT geoid, "{selected_field}" FROM census.acs2023_combined'
    acs_df = pd.read_sql(acs_query, engine)
    acs_df['geoid'] = acs_df['geoid'].astype(str).str.zfill(12)

    # Merge ACS data into block groups
    block_groups = block_groups.merge(
        acs_df, left_on='GEOID', right_on='geoid', how='left')

    # Bin the selected field for grayscale mapping
    if block_groups[selected_field].notnull().sum() > 0:
        block_groups['underlay_bin'] = pd.qcut(
            block_groups[selected_field], bins, labels=False, duplicates='drop')
    else:
        block_groups['underlay_bin'] = None

    # Grayscale colors (light to dark)
    gray_colors = ["#f0f0f0", "#bdbdbd", "#969696", "#636363", "#252525"]
    block_groups['underlay_color'] = block_groups['underlay_bin'].map(
        lambda x: gray_colors[int(x)] if pd.notnull(x) else None)

    return block_groups
