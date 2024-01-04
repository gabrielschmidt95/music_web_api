from time import sleep

import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, html

from server import app


class Track:

    def __init__(self, conn):
        self.conn = conn
        self.correiosUri = "http://webservice.correios.com.br/service/rest/rastro/rastroMobile"

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
                                    title="Pesquisar",
                                    color="info",
                                    outline=True,
                                    id="track_btn"
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                dbc.Button(
                                    html.I(className="bi bi-save"),
                                    title="Salvar",
                                    color="warning",
                                    outline=True,
                                    id="save_track_btn"
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                dbc.Button(
                                    html.I(className="bi bi-trash"),
                                    title="Deletar",
                                    color="danger",
                                    outline=True,
                                    id="delete_track_btn"
                                ),
                                width="auto"
                            ),
                        ],
                        className="g-2",
                    )
                )),
                html.Div(id="track-saved"),
                html.Div(id="track-selected"),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Remover Rastreios")),
                        dbc.ModalBody(
                            dbc.Checklist(
                                id="track_delete-checklist",
                            ), id="delete-modal-body"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Confirmar", id="confirm_track_delete", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    is_open=False,
                    id="delete-modal"
                )
            ]
        )

    def getTrack(self, trackId):
        return requests.post(
            self.correiosUri,
            headers={"Content-Type": "application/xml"},
            data=f"""
            <rastroObjeto>
                <usuario>USER</usuario>
                <senha>PASS</senha>
                <tipo>L</tipo>
                <resultado>T</resultado>
                <objetos>{trackId}</objetos>
                <lingua>101</lingua>
                <token>TOKEN</token>
            </rastroObjeto>"""
        )

    def track_table(self, event):
        return dbc.Row([
            dbc.Col([
                html.H5(event["descricao"]),
                dbc.Table([
                    html.Thead(
                        html.Tr([
                            html.Th(
                                "Data") if "dataPostagem" in event else None,
                            html.Th(
                                "Origem") if "unidade" in event else None,
                            html.Th(
                                "Destino") if "destino" in event else None
                        ])
                    )
                ] + [
                    html.Tbody([
                        html.Tr([
                            html.Td(
                                event["dataPostagem"]
                            ) if "dataPostagem" in event else None,
                            html.Td(event["unidade"]["local"] if "local" in event["unidade"]
                                    else event["unidade"]
                            ) if "unidade" in event else None,
                            html.Td(event["destino"][0]["local"] if "local" in event["destino"]
                                    [0] else event["destino"][0]
                            ) if "destino" in event else None
                        ])
                    ])
                ],
                    bordered=False,
                    responsive=True),
            ], width=6, align="center"),
        ])

    def callbacks(self):
        @ app.callback(
            Output("track-saved", "children"),
            Input("confirm_track_delete", "n_clicks"),
            Input('save_track_btn', 'n_clicks'),
            prevent_initial_call=True
        )
        def on_track_button_click(delete, saved):
            sleep(1)
            return dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.ListGroupItem(
                                [
                                    self.track_table(event)
                                ]
                            ) for event in self.getTrack(postal["TRACK_CODE"]).json()["objeto"][0]["evento"]
                        ],
                        title=f'{postal["TRACK_CODE"]}',
                    )
                    for postal in self.conn.find_all("POSTAL")],
                start_collapsed=True
            )

        @ app.callback(
            Output("track-selected", "children"),
            Input('track_btn', 'n_clicks'),
            State("track_code", "value"),
            prevent_initial_call=True,
        )
        def on_track_button_click(click, _track_id):
            track = self.getTrack(_track_id)
            if track.status_code == 200:
                track = track.json()["objeto"][0]
                return dbc.Accordion(
                    [
                        dbc.AccordionItem([
                            dbc.ListGroupItem(
                                [
                                    self.track_table(event)
                                ]
                            ) for event in track["evento"]
                        ], title=f'{track["numero"]} - {track["evento"][0]["descricao"]}'),
                    ],
                ) if "evento" in track else dbc.Alert("Objeto nao encontrado", is_open=True, dismissable=True)
            else:
                return dbc.Alert(f"Erro {track.status_code}- {track}", is_open=True, dismissable=True)

        @ app.callback(
            Output("save_alert", "children"),
            Output("save_alert", "is_open"),
            Input('save_track_btn', 'n_clicks'),
            State("track_code", "value"),
            prevent_initial_call=True,
        )
        def on_track_button_click(click, track_code):
            if click > 0 and track_code is not None:
                track = self.getTrack(track_code)
                if track.status_code == 200:
                    if "evento" in track.json()["objeto"][0]:
                        if self.conn.find_custom("POSTAL", "TRACK_CODE", track_code) is None:
                            self.conn.insert_one(
                                "POSTAL", {"TRACK_CODE": track_code})
                            return "", False
                        else:
                            return "Codigo Ja Existente", True
                    else:
                        return "Codigo Inexistente", True
                else:
                    return "Erro Coenxao", True
            else:
                return "Nulo", True

        @app.callback(
            Output("delete-modal", "is_open"),
            Output("track_delete-checklist", "options"),
            Input("delete_track_btn", "n_clicks"),
            Input("confirm_track_delete", "n_clicks"),
            State("delete-modal", "is_open"),
            State("track_delete-checklist", "value"),
            prevent_initial_call=True,
        )
        def toggle_modal(n1, n2, is_open, check_list):
            list_track = [
                {"label": v["TRACK_CODE"], "value": str(v["_id"])} for v in self.conn.find_all("POSTAL")
            ]
            if n2:
                self.conn.delete_many("POSTAL", check_list)
                return not is_open, list_track
            if n1:
                return not is_open, list_track
