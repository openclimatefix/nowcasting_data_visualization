""" Make status layout """
from datetime import datetime, timezone

from dash import dash_table, dcc, html

from .database import get_consumer_status, get_forecast_status


def make_status_layout():
    """Make html status page"""

    now_text = datetime.now(timezone.utc).strftime("Refresh time: %Y-%m-%d %H:%M:%S  [UTC]")
    style_data_conditional = [
                    {
                        "if": {"filter_query": '{Status} = "Warning"', "column_id": "Status"},
                        "backgroundColor": "orange",
                        "color": "white",
                    },
                    {
                        "if": {"filter_query": '{Status} = "Error"', "column_id": "Status"},
                        "backgroundColor": "red",
                        "color": "white",
                    },
                    {
                        "if": {"filter_query": '{Status} = "Ok"', "column_id": "Status"},
                        "backgroundColor": "green",
                        "color": "white",
                    },
                ]

    tab3 = html.Div(
        [
            html.H3("Data Consumers"),
            dash_table.DataTable(
                data=get_consumer_status(),
                id="pv-table-status",
                style_data_conditional=style_data_conditional
            ),
            html.H3("Forecasts"),
            dash_table.DataTable(
                data=get_forecast_status(),
                id="table-status-forecast",
                style_data_conditional=style_data_conditional
            ),
            html.Div(now_text, id="pv-refresh-datetime"),
            dcc.Interval(id="pv-interval", interval=30000),
            html.P(id="output"),
        ],
        style={"width": "49%"},
    )

    return tab3
