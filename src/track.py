from datetime import datetime
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from server import app
import requests


class Track:

    def __init__(self, conn):
        self.conn = conn

    def layout(self):
        return dbc.ListGroup(
            [
                dbc.Alert(id="save_alert", is_open=False, dismissable=True),
                dbc.ListGroupItem(dbc.Form(
                    dbc.Row(
                        [
                            dbc.Label("Código de rastreamento", width="auto"),
                            dbc.Col(
                                dbc.Input(
                                    type="text",
                                    id="track_code",
                                ),
                                className="me-3",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    html.I(className="bi bi-search"),
                                    color="info",
                                    outline=True,
                                    id="track_btn"
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                dbc.Button(
                                    html.I(className="bi bi-save"),
                                    color="warning",
                                    outline=True,
                                    id="save_track_btn"
                                ),
                                width="auto"
                            ),
                        ],
                        className="g-2",
                    )
                )),
                html.Div(id="track-saved"),
                html.Div(id="track-selected"),
            ]
        )

    def callbacks(self):
        @ app.callback(
            Output("track-saved", "children"),
            Input('url', 'pathname'),
            State('save_track_btn', 'n_clicks'),
            prevent_initial_call=True,
        )
        def on_track_button_click(click, saved):
            return dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.ListGroupItem(
                                [
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Row(html.Img(
                                                src=f"https://rastreamento.correios.com.br/static/rastreamento-internet/imgs/{event['urlIcone'].split('/')[-1]}"
                                            ), justify="center")
                                        ], width=1, align="center"),
                                        dbc.Col([
                                            html.H6(event["descricao"]),
                                            html.P(
                                                f'Destino: {event["unidadeDestino"]}' if "unidadeDestino" in event else ""),
                                            html.P(
                                                f'Origem: {event["unidade"] if "unidade" in event else ""}'),
                                            html.P(datetime.strptime(event["dtHrCriado"], "%Y-%m-%dT%H:%M:%S").strftime("Dia: %d/%m/%Y Hora: %H:%M:%S"))
                                        ], width=10, align="center"),
                                    ])
                                ]
                            ) for event in requests.get(f"https://proxyapp.correios.com.br/v1/sro-rastro/{postal['TRACK_CODE']}").json()["objetos"][0]["eventos"]
                        ],
                        title=postal["TRACK_CODE"],
                    )
                for postal in self.conn.find_all("POSTAL") ],
            )

        
        @ app.callback(
            Output("track-selected", "children"),
            Input('track_btn', 'n_clicks'),
            State("track_code", "value"),
            prevent_initial_call=True,
        )
        def on_track_button_click(click, _track_id):
            track = requests.get(
                f"https://proxyapp.correios.com.br/v1/sro-rastro/{_track_id}")
            if track.status_code == 200:
                track = track.json()["objetos"][0]
                return dbc.Accordion(
                    [
                        dbc.AccordionItem([
                            dbc.ListGroupItem(
                                [
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Row(html.Img(
                                                src=f"https://rastreamento.correios.com.br/static/rastreamento-internet/imgs/{event['urlIcone'].split('/')[-1]}"
                                            ), justify="center")
                                        ], width=1, align="center"),
                                        dbc.Col([
                                            html.H6(event["descricao"]),
                                            html.P(
                                                f'Destino: {event["unidadeDestino"]}' if "unidadeDestino" in event else ""),
                                            html.P(
                                                f'Origem: {event["unidade"] if "unidade" in event else ""}'),
                                            html.P(datetime.strptime(event["dtHrCriado"], "%Y-%m-%dT%H:%M:%S").strftime("Dia: %d/%m/%Y Hora: %H:%M:%S"))
                                        ], width=10, align="center"),
                                    ])
                                ]
                            ) for event in track["eventos"]
                        ], title=f'{track["codObjeto"]} - {track["tipoPostal"]["categoria"]} - {track["tipoPostal"]["descricao"]}'),
                    ],
                ) if "eventos" in track else dbc.Alert("Objeto nao encontrado", is_open=True, dismissable=True)

        @ app.callback(
            Output("save_alert", "children"),
            Output("save_alert", "is_open"),
            Input('save_track_btn', 'n_clicks'),
            State("track_code", "value"),
            prevent_initial_call=True,
        )
        def on_track_button_click(click, track_code):
            if click > 0 and track_code is not None:
                track = requests.get(
                f"https://proxyapp.correios.com.br/v1/sro-rastro/{track_code}")
                if track.status_code == 200:
                    if "eventos" in track.json()["objetos"][0]:
                        if self.conn.find_custom("POSTAL", "TRACK_CODE",track_code) is None:
                            self.conn.insert_one("POSTAL", {"TRACK_CODE":track_code})
                            return "Salvo", True
                        else:
                            return "Codigo Ja Existente", True
                    else:
                        return "Codigo Inexistente", True
                else:
                    return "Erro Coenxao", True
            else:
                return "Nulo", True