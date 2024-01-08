import requests
from os import environ
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

discogs_url = "https://api.discogs.com/database/search"

def get_album_for_artist(artist, album):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = sp.search(q="artist:" + artist + " album:" + album, type="album")
    if results:
        items = results["albums"]["items"]
        if len(items) > 0:
            return items
        else:
            return None
    else:
        return None


def def_get_discogs(params):
    resp = requests.get(discogs_url, params=params)
    return resp.json()["results"]


def get_params(row):
    return {
        "token": environ["DISCOGS_TOKEN"],
        "artist": row["artist"].lower() if row["artist"] is not None else "",
        "release_title": row["title"].lower()
        if row["title"].lower() is not None
        else "",
        "barcode": str(row["barcode"])
        if row["barcode"] is not None and row["barcode"] != "None"
        else "",
        "country": row["origin"].lower()
        if not None and row["origin"].lower() != "none"
        else "",
        "year": str(row["releaseYear"]) if row["artist"] is not None else "",
        "format": "album",
    }


def try_get_discogs(params):
    params.pop("format")
    result = def_get_discogs(params)
    if len(result) == 0:
        params.pop("year")
        result = def_get_discogs(params)
        if len(result) == 0:
            params.pop("country")
            result = def_get_discogs(params)
            if len(result) == 0:
                params.pop("barcode")
                result = def_get_discogs(params)

    return result

def get_tracks(_type, _id):
    tracks = requests.get(f"https://api.discogs.com/{_type}s/{_id}")
    if tracks.status_code == 200:
        return tracks.json()["tracklist"]
    
    return None

def get_discogs(row):
    params = get_params(row)
    response = requests.get(discogs_url, params=params)

    if response.status_code == 200:
        return response
    
    return None