""" Make status layout """
import logging

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table

from .database import get_consumer_status

logger = logging.getLogger(__name__)


def make_status_layout():
    tab3 = html.Div(
        [
            html.H3("Data Consumers"),
            dash_table.DataTable(
                data=get_consumer_status(),
                id="table-status",
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{Status} = "Warning"',
                            'column_id': 'Status'
                        },
                        "backgroundColor": "orange",
                        "color": "white",
                    },
                    {
                        'if': {
                            'filter_query': '{Status} = "Error"',
                            'column_id': 'Status'
                        },
                        "backgroundColor": "red",
                        "color": "white",
                    },
                    {
                        'if': {
                            'filter_query': '{Status} = "Ok"',
                            'column_id': 'Status'
                        },
                        "backgroundColor": "green",
                        "color": "white",
                    },
                ],
            ),
        ],
        style={"width": "49%"},
    )

    return tab3
