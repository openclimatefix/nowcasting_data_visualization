""" Make nwp plots """

import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
import xarray as xr
from plotly import graph_objects as go

logger = logging.getLogger(__name__)


def make_slider(labels: List[str]) -> dict:
    """Make slider for animation"""
    sliders = [
        dict(
            steps=[
                dict(
                    method="animate",
                    args=[
                        [f"frame{k+1}"],
                        dict(
                            mode="immediate",
                            frame=dict(duration=600, redraw=True),
                            transition=dict(duration=200),
                        ),
                    ],
                    label=f"{labels[k]}",
                )
                for k in range(0, len(labels))
            ],
            transition=dict(duration=100),
            x=0,
            y=0,
            currentvalue=dict(font=dict(size=12), visible=True, xanchor="center"),
            len=1.0,
        )
    ]
    return sliders


def make_buttons() -> dict:
    """Make buttons Play and Pause"""
    return dict(
        type="buttons",
        buttons=[
            dict(label="Play", method="animate", args=[None], name="play-button"),
            dict(
                args=[
                    [None],
                    {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0},
                    },
                ],
                label="Pause",
                method="animate",
            ),
        ],
    )


def plot_nwp_data(init_time, variable, filename: Optional[str] = "./nwp_latest.netcdf"):
    """Plot nwp data"""

    logger.debug(f"Plotting data {filename=}, {init_time=}, {variable=}")
    print(filename)
    nwp_xr = xr.load_dataset(filename)["UKV"]
    init_time = datetime.fromisoformat(init_time)

    nwp_xr = nwp_xr.sel(init_time=init_time)
    nwp_xr = nwp_xr.sel(variable=variable)

    # TODO
    # reproject to lat lon and put on coastline

    logger.debug("Making nwp traces for animation")
    traces = []
    labels = []
    for i in range(len(nwp_xr.step)):
        traces.append(go.Heatmap(z=nwp_xr[i].values, zmin=0, zmax=1000))
        # do we need pandas here?
        step = pd.to_timedelta(nwp_xr.step[i].values)
        labels.append(init_time + step)

    # make animation
    logger.debug("Making np figure")
    fig = go.Figure(
        data=traces[0],
        layout=go.Layout(
            title="Start Title",
        ),
    )

    frames = []
    for i, trace in enumerate(traces):
        frames.append(go.Frame(data=trace, name=f"frame{i + 1}"))

    fig.update(frames=frames)
    fig.update_layout(updatemenus=[make_buttons()])

    sliders = make_slider(labels=labels)
    fig.update_layout(sliders=sliders)
    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 30},
        height=700,
    )

    logger.debug("Done making nwp plot")
    return fig
