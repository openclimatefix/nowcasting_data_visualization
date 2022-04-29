""" Callbacks functions """
from datetime import datetime, timezone

from dash import Input, Output

from .database import get_consumer_status


def make_status_callbacks(app):
    """Make callbacks"""

    @app.callback(
        [Output("pv-refresh-datetime", "children"), Output("pv-table-status", "data")],
        [Input("pv-interval", "n_intervals")],
    )
    def update_display_time_and_consumer_status(n):
        """Update consumer status and refresh time"""
        print("update_display_time_and_consumer_status")
        consumer_status = get_consumer_status()
        now_text = datetime.now(timezone.utc).strftime("Refresh time: %Y-%m-%d %H:%M:%S  [UTC]")

        return now_text, consumer_status

    return app
