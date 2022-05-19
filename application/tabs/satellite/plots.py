""" Make nwp plots """

from typing import List, Optional

import pandas as pd
import xarray as xr
from log import logger
from plotly import graph_objects as go


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
            dict(label="Play", method="animate", args=[None]),
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


def plot_satellite_data(variable, filename: Optional[str] = "./satellite_latest.netcdf"):
    """Plot nwp data"""

    logger.debug(f"Plotting data {filename=}, {variable=}")
    print(filename)
    with xr.load_dataset("zip::satellite_latest.zarr.zip", engine="zarr") as satellite_xr:


        satellite_xr = satellite_xr.sel(variable=variable)
        satellite_xr = satellite_xr.data

        zmax = float(satellite_xr.max())
        zmin = float(satellite_xr.min())

        # flip horizontally
        satellite_xr = satellite_xr.reindex(x_geostationary=satellite_xr.x_geostationary[::-1])

        # TODO
        # reproject to lat lon and put on coastline

        logger.debug("Making satellite traces for animation")
        traces = []
        labels = []
        for i in range(len(satellite_xr.time)):
            traces.append(go.Heatmap(z=satellite_xr[i].values, zmin=zmin, zmax=zmax))
            # do we need pandas here?
            step = pd.to_datetime(satellite_xr.time[i].values)
            labels.append(step)

        # make animation
        logger.debug("Making satellite figure")
        fig = go.Figure(
            data=traces[0],
            layout=go.Layout(
                title=f"Start Title - {variable}",
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

        logger.debug("Done making satellite plot")
    return fig
