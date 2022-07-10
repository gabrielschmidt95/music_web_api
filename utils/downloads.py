from dash import dcc, Input, Output
from server import app

class Downloads:

    def __init__(self, df):
        self.df = df
    
    def xlsx(self):
        @app.callback(
                Output("download_xlsx", "data"),
                Input("download_xlsx_btn", "n_clicks"),
                prevent_initial_call=True,
            )
        def on_button_click(n):
            if n is None:
                raise ""
            else:
                return dcc.send_data_frame(self.df.to_excel, "collection.xlsx")