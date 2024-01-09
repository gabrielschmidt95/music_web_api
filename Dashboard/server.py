from os import environ

import dash_bootstrap_components as dbc
from dash import Dash

from dotenv import load_dotenv
load_dotenv(override=True)

from auth.google_oauth import GoogleAuth
from auth.token import get_token

get_token()

port = int(environ.get("PORT", 8050))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.title = "Music Collection"

auth = GoogleAuth(app)
