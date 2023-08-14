import dash_bootstrap_components as dbc
from dash_google_oauth.google_auth import GoogleAuth
from dash import Dash
from os import environ

port = int(environ.get("PORT", 5000))


app = Dash(__name__, external_stylesheets=[
           dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.title = 'Music Collection'

auth = GoogleAuth(app)
