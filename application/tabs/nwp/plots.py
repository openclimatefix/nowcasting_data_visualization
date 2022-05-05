""" Make nwp plots """

import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
import xarray as xr
from plotly import graph_objects as go
from tabs.plot_utils import make_buttons, make_slider

logger = logging.getLogger(__name__)


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
