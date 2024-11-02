from dash import (
    Dash, html, dash_table, dcc, callback, Output, Input, no_update
)
import numpy as np
import pandas as pd
from gcd_table import build_gcd_table


a_0 = 27
b_0 = 18
df_columns = list(build_gcd_table(a_0, b_0).columns)

app = Dash()

app.layout = [
    dcc.Markdown('''
This is a an example of the use of the extended Euclidean algorithm.

The result is integers `u`, `v`, `GCD(a, b)` such that `u * a + v * b = GCD(a, b)`,
and `GCD(a, b)` is the greatest common divisor of `a` and `b`.

The method calculates `GCD(a, b)` by building table forward row by row, using 
the reduction `GCD(a, b) = GCD(b, a % b)` when `b >= 1, a >= b`. Then `GCD(a, b)`, `u`, and `v`
and are back-filled from the last row (where these values are known).

To use: enter integers for `a` and `b`, and then press "Update Table".

A description of the methodology can be found 
[here](https://github.com/WinVector/Examples/blob/main/puzzles/DividingCoconuts/Monkey_and_Coconuts.ipynb).
    '''),
    html.Div(
        [
            "a: ",
            dcc.Input(id="a", type="number", value=a_0, min=1),
            ", b: ",
            dcc.Input(id="b", type="number", value=b_0, min=1),
            ", ",
            html.Button("Update Table", id="update-button"),
        ]
    ),
    dash_table.DataTable(
        id="data-table",
        columns=[{"name": i, "id": i} for i in df_columns],
        fill_width=False,
        style_data={
            "color": "black",
            "backgroundColor": "white",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "rgb(220, 220, 220)",
            }
        ],
        style_header={
            "backgroundColor": "rgb(180, 180, 180)",
            "color": "black",
            "fontWeight": "bold",
        },
    ),
]

last_clicks = None


@app.callback(
    Output("data-table", "data"),
    Input("update-button", "n_clicks"),
    Input("a", "value"),
    Input("b", "value"),
)
def update_table(n_clicks, a, b):
    global last_clicks
    if (n_clicks is None) or (
        n_clicks == last_clicks
    ):  # Prevents update on initial load
        return no_update
    last_clicks = n_clicks
    return build_gcd_table(a, b).to_dict("records")


if __name__ == "__main__":
    app.server.run(port=8000, host="127.0.0.1")
