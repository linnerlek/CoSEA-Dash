from dash import Dash
from layout import create_layout
from callbacks import register_callbacks
from helpers import load_data, prepare_options
from config import FILTER_OPTIONS, DISPARITY_COLUMNS

data = load_data()
school_classification_options, locale_options = prepare_options(data)

app = Dash(__name__)
app.layout = create_layout(
    app,
    FILTER_OPTIONS,
    school_classification_options,
    locale_options,
    DISPARITY_COLUMNS,
)

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)