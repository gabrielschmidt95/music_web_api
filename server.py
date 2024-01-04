from os import environ

import dash_bootstrap_components as dbc
from dash import Dash
from dotenv import load_dotenv

from auth.google_oauth import GoogleAuth

load_dotenv()

port = int(environ.get("PORT", 5000))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.title = "Music Collection"

auth = GoogleAuth(app)
