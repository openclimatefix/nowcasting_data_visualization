""" Make nwp plots """

from datetime import datetime
from typing import Optional

import pandas as pd
import xarray as xr
from log import logger
from plotly import graph_objects as go

from application.tabs.plot_utils import make_buttons, make_slider


def plot_nwp_data(init_time, variable, filename: Optional[str] = "./nwp_latest.netcdf"):
    """Plot nwp data"""

    logger.debug(f"Plotting data {filename=}, {init_time=}, {variable=}")
    print(filename)
    with xr.load_dataset("nwp_latest.netcdf")["UKV"] as nwp_xr:

        init_time = datetime.fromisoformat(init_time)

        nwp_xr = nwp_xr.sel(init_time=init_time)
        nwp_xr = nwp_xr.sel(variable=variable)

        zmax = float(nwp_xr.max())
        zmin = float(nwp_xr.min())

        # flip horizontally
        nwp_xr = nwp_xr.reindex(y=nwp_xr.y[::-1])

        # TODO
        # reproject to lat lon and put on coastline

        logger.debug("Making nwp traces for animation")
        traces = []
        labels = []
        for i in range(len(nwp_xr.step)):
            traces.append(go.Heatmap(z=nwp_xr[i].values, zmin=zmin, zmax=zmax))
            # do we need pandas here?
            step = pd.to_timedelta(nwp_xr.step[i].values)
            labels.append(init_time + step)

        # make animation
        logger.debug("Making np figure")
        fig = go.Figure(
            data=traces[0],
            layout=go.Layout(
                title=f"Start Title - {variable} - {init_time}",
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
