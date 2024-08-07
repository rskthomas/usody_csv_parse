import os
import math

from weasyprint import HTML
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/files'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        from . import routes
    return app


def format_csv(data):

    for row in data:
        for key, value in row.items():
            if isinstance(value, float) and math.isnan(value):
                row[key] = None  # Replace NaN with None
            if value == 0:
                row[key] = None
    return data

