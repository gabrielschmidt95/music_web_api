import dash_bootstrap_components as dbc
from auth.google_oauth import GoogleAuth
from dash import Dash
from os import environ
from dotenv import load_dotenv

load_dotenv()

port = int(environ.get("PORT", 5000))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.title = "Music Collection"

auth = GoogleAuth(app)
