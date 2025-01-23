from dash import Dash
from layout import create_layout
from callbacks import register_callbacks
from helpers import *
from config import FILTER_OPTIONS, DISPARITY_COLUMNS

app = Dash(__name__)

data = load_data()
school_classification_options, locale_options = prepare_options(data)

layer_metadata = fetch_layers_metadata()
valid_layer_options = prepare_layer_options(layer_metadata)

georgia_outline_gdf = fetch_georgia_outline()

app.layout = create_layout(
    app,
    FILTER_OPTIONS,
    school_classification_options,
    locale_options,
    DISPARITY_COLUMNS,
    valid_layer_options, 
)

register_callbacks(app, georgia_outline_gdf, data, layer_metadata)

if __name__ == "__main__":
    app.run_server(debug=False)
