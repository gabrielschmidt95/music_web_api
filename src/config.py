from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from io import StringIO, BytesIO
from server import app
import pandera as pa
import pandas as pd
import numpy as np
import base64

class Config:

    def __init__(self, conn):
        self.conn = conn

    def layout(self):
        return dbc.Row(
            [
                dcc.Download(id="download_xlsx"),
                html.Div(id="download_alert"),
                html.Div(id="upload_alert"),
                dbc.Col(
                    dbc.Button(
                        " Download XLSX",
                        color="success",
                        className="bi bi-download",
                        id="download_xlsx_btn"
                    ),
                    width=12
                ),
                dbc.Col(
                    dcc.Upload(
                        dbc.Button(
                            " Upload XLSX",
                            color="info",
                            className="bi bi-upload",
                        ),
                        id="upload_xlsx"
                    ),
                    width=12
                ),
                dbc.Col(
                    dbc.Button(
                        " Adicionar",
                        color="secondary",
                        className="bi bi-plus-circle",
                        id="insert_btn"
                    ), width=12
                ),
            ],
            className="g-2",
        )

    def callbacks(self):
        @ app.callback(
            Output("upload_alert", "children"),
            Input('upload_xlsx', 'contents'),
            State("upload_xlsx", "filename"),
            prevent_initial_call=True,
        )
        def on_button_click(data, filename):
            content_type, content_string = data.split(',')
            decoded = base64.b64decode(content_string)

            if filename is None:
                raise ""
            else:
                if 'csv' in filename:
                    df = pd.read_csv(
                        StringIO(decoded.decode('utf-8')), sep=";")
                elif 'xls' in filename:
                    df = pd.read_excel(
                        BytesIO(decoded), dtype={'BARCODE': str})
                else:
                    return dbc.Alert("FORMATO INVALIDO",
                                     is_open=True,  duration=4000, color="danger")

                COLUMNS = ('RELEASE_YEAR', 'ARTIST', 'TITLE', 'MEDIA', 'PURCHASE', 'ORIGIN',
                           'EDITION_YEAR', 'IFPI_MASTERING', 'IFPI_MOULD', 'BARCODE', 'MATRIZ', 'LOTE', 'ANO_AQUISICAO', 'RECENTE', 'LISTA')

                for col in df.select_dtypes(include=['datetime64']).columns.tolist():
                    df[col] = df[col].astype(str)

                validate_schema = pa.DataFrameSchema({
                    "RELEASE_YEAR": pa.Column(int),
                    "ARTIST": pa.Column(str),
                    "TITLE": pa.Column(str),
                    "MEDIA": pa.Column(str),
                    "PURCHASE": pa.Column(object, nullable=True),
                    "ORIGIN": pa.Column(str, nullable=True),
                    "EDITION_YEAR": pa.Column(float, nullable=True),
                    "IFPI_MASTERING": pa.Column(str, nullable=True),
                    "IFPI_MOULD": pa.Column(str, nullable=True),
                    "MATRIZ": pa.Column(str, nullable=True),
                    "LOTE": pa.Column(str, nullable=True)
                })

                try:
                    validate_schema(df)
                    df.replace({pd.NaT: None, np.nan: None, "NaT": None,
                                "": None, "None": None}, inplace=True)
                    df = df.to_dict("records")

                    newList = []

                    for d in df:
                        newDf = {}
                        for key, value in d.items():
                            if key in COLUMNS:
                                newDf[key] = value
                        newList.append(newDf)

                    self.conn.drop("CD")
                    self.conn.insert_many("CD", newList)

                    return dbc.Alert("SALVO",
                                     is_open=True,  duration=4000)
                except pa.errors.SchemaError as error:
                    return dbc.Alert([
                            html.P(f"ERRO NOS DADOS DA COLUNA: {error.schema.name}"),
                            html.P(f"TIPO ESPERADO: {error.check}")
                        ],is_open=True,color="danger"
                    )

        @app.callback(
            Output("download_xlsx", "data"),
            Input("download_xlsx_btn", "n_clicks"),
            prevent_initial_call=True,
        )
        def on_button_click(n):
            if n is None:
                raise ""
            else:
                df = self.conn.qyery("CD")
                df.drop('_id', axis=1, inplace=True)
                df['PURCHASE'] = pd.to_datetime(df['PURCHASE']).dt.date
                df.replace({pd.NaT: None, np.nan: None, "NaT": None,
                           "": None, "None": None}, inplace=True)
                return dcc.send_data_frame(df.to_excel, "collection.xlsx")