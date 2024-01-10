import requests
from os import environ
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from typing import List, Any
from dataclasses import dataclass

discogs_url = "https://api.discogs.com/database/search"


@dataclass
class Track:
    position: str
    type_: str
    title: str
    duration: str

    @staticmethod
    def from_dict(obj: Any) -> "Track":
        _position = str(obj.get("position"))
        _type_ = str(obj.get("type_"))
        _title = str(obj.get("title"))
        _duration = str(obj.get("duration"))
        return Track(_position, _type_, _title, _duration)

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "type_": self.type_,
            "title": self.title,
            "duration": self.duration,
        }


@dataclass
class Url:
    id: int
    uri: str

    @staticmethod
    def from_dict(obj: Any) -> "Url":
        _id = int(obj.get("id"))
        _uri = str(obj.get("uri"))
        return Url(_id, _uri)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "uri": self.uri,
        }


@dataclass
class UserData:
    in_wantlist: bool
    in_collection: bool

    @staticmethod
    def from_dict(obj: Any) -> "UserData":
        _in_wantlist = bool(obj.get("in_wantlist"))
        _in_collection = bool(obj.get("in_collection"))
        return UserData(_in_wantlist, _in_collection)

    def to_dict(self) -> dict:
        return {
            "in_wantlist": self.in_wantlist,
            "in_collection": self.in_collection,
        }


@dataclass
class Community:
    want: int
    have: int

    @staticmethod
    def from_dict(obj: Any) -> "Community":
        _want = int(obj.get("want"))
        _have = int(obj.get("have"))
        return Community(_want, _have)

    def to_dict(self) -> dict:
        return {
            "want": self.want,
            "have": self.have,
        }


@dataclass
class Format:
    name: str
    qty: str
    descriptions: List[str]

    @staticmethod
    def from_dict(obj: Any) -> "Format":
        _name = str(obj.get("name"))
        _qty = str(obj.get("qty"))
        _descriptions = [y for y in obj.get("descriptions")]
        return Format(_name, _qty, _descriptions)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "qty": self.qty,
            "descriptions": self.descriptions,
        }


@dataclass
class Discogs:
    country: str
    year: str
    format: List[str]
    label: List[str]
    type: str
    genre: List[str]
    style: List[str]
    id: int
    barcode: List[str]
    user_data: UserData
    master_id: int
    master_url: str
    uri: str
    catno: str
    title: str
    thumb: str
    cover_image: str
    resource_url: str
    community: Community
    format_quantity: int
    formats: List[Format]
    urls: List[Url]
    len: int
    tracks: List[Track]

    @staticmethod
    def from_dict(obj: Any) -> "Discogs":
        _country = str(obj.get("country"))
        _year = str(obj.get("year"))
        _format = [y for y in obj.get("format")]
        _label = [y for y in obj.get("label")]
        _type = str(obj.get("type"))
        _genre = [y for y in obj.get("genre")]
        _style = [y for y in obj.get("style")]
        _id = int(obj.get("id"))
        _barcode = [y for y in obj.get("barcode")]
        _user_data = UserData.from_dict(obj.get("user_data"))
        _master_id = int(obj.get("master_id"))
        _master_url = str(obj.get("master_url"))
        _uri = str(obj.get("uri"))
        _catno = str(obj.get("catno"))
        _title = str(obj.get("title"))
        _thumb = str(obj.get("thumb"))
        _cover_image = str(obj.get("cover_image"))
        _resource_url = str(obj.get("resource_url"))
        _community = Community.from_dict(obj.get("community"))
        _format_quantity = int(obj.get("format_quantity"))
        _formats = [Format.from_dict(y) for y in obj.get("formats")]
        _urls = [Url.from_dict(y) for y in obj.get("urls")]
        _len = int(obj.get("len"))
        _tracks = [Track.from_dict(y) for y in obj.get("tracks")]
        return Discogs(
            _country,
            _year,
            _format,
            _label,
            _type,
            _genre,
            _style,
            _id,
            _barcode,
            _user_data,
            _master_id,
            _master_url,
            _uri,
            _catno,
            _title,
            _thumb,
            _cover_image,
            _resource_url,
            _community,
            _format_quantity,
            _formats,
            _urls,
            _len,
            _tracks,
        )

    def to_dict(self) -> dict:
        return {
            "country": self.country,
            "year": self.year,
            "format": self.format,
            "label": self.label,
            "type": self.type,
            "genre": self.genre,
            "style": self.style,
            "id": self.id,
            "barcode": self.barcode,
            "user_data": self.user_data.to_dict(),
            "master_id": self.master_id,
            "master_url": self.master_url,
            "uri": self.uri,
            "catno": self.catno,
            "title": self.title,
            "thumb": self.thumb,
            "cover_image": self.cover_image,
            "resource_url": self.resource_url,
            "community": self.community.to_dict(),
            "format_quantity": self.format_quantity,
            "formats": [y.to_dict() for y in self.formats],
            "urls": [y.to_dict() for y in self.urls],
            "len": self.len,
            "tracks": [y.to_dict() for y in self.tracks],
        }


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


def get_data_by_id(row, discogs_id: int) -> None:
    resp = requests.get(
        f"https://api.discogs.com/releases/{discogs_id}",
        params={"token": environ["DISCOGS_TOKEN"]},
    )

    if resp.status_code != 200:
        return None

    resp = resp.json()

    discogs = Discogs(
        country=resp["country"],
        year=resp["year"],
        format=[y["name"] for y in resp["formats"]],
        label=[y["name"] for y in resp["labels"]],
        type="album",
        genre=resp["genres"],
        style=resp["styles"],
        id=resp["id"],
        barcode=[y["value"] for y in resp["identifiers"] if y["type"] == "Barcode"],
        user_data=UserData(
            in_wantlist=resp["community"]["want"],
            in_collection=resp["community"]["have"],
        ),
        master_id=resp["master_id"],
        master_url=resp["master_url"],
        uri=resp["uri"],
        catno=resp["labels"][0]["catno"],
        title=resp["title"],
        thumb=resp["thumb"],
        cover_image=resp["images"][0]["uri"],
        resource_url=resp["resource_url"],
        community=Community.from_dict(resp["community"]),
        format_quantity=resp["format_quantity"],
        formats=[
            Format(
                name=y["name"],
                qty=y["qty"],
                descriptions=[z for z in y["descriptions"]],
            )
            for y in resp["formats"]
        ],
        urls=[],
        len=1,
        tracks=[Track.from_dict(y) for y in resp["tracklist"]],
    ).to_dict()

    row["discogs"] = discogs

    row["discogs"]["urls"] = [
        {
            "id": discogs["id"],
            "uri": "/release" + discogs["uri"][discogs["uri"].rfind("/") :],
        }
    ]

    return row
