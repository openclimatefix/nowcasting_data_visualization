"""Main plots function """
import json
import os
from datetime import datetime, timezone
from typing import Optional, Union

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from log import logger
from nowcasting_datamodel.models import ForecastValue, GSPYield, ManyForecasts
from plotly import graph_objects as go

API_URL = os.getenv("API_URL")
assert API_URL is not None, "API_URL has not been set"


def get_gsp_boundaries() -> json:
    """Get boundaries for gsp regions"""

    # get gsp boundaries
    logger.info("Get gsp boundaries")
    r = requests.get(API_URL + "/v0/GB/solar/gsp/gsp_boundaries/")
    d = r.json()
    boundaries = gpd.GeoDataFrame.from_features(d["features"])

    # simplify geometyr to roughly every 100meter
    boundaries["geometry"] = boundaries.geometry.simplify(360 / 432000)

    return boundaries.to_json()


def make_plots(gsp_id: int = 0, show_yesterday: Union[str, bool] = "both"):
    """
    Make true and forecast plots

    :param gsp_id: gsp id number
    :param show_yesterday: option to show yesterday results or not.
    If 'both' is used, then both plots that include yesterday and not are returned
    :return: figure, or list of figures
    """

    logger.info(f"Making plot for gsp {gsp_id}, {show_yesterday=}")
    logger.debug("API request: day after")
    response = requests.get(f"{API_URL}/v0/GB/solar/gsp/truth/one_gsp/{gsp_id}/?regime=day-after")
    r = response.json()
    gsp_truths_day_after = pd.DataFrame([GSPYield(**i).__dict__ for i in r])
    logger.debug(f"API request: day after. Found {len(gsp_truths_day_after)} data points")

    logger.debug("API request: in day")
    response = requests.get(f"{API_URL}/v0/GB/solar/gsp/truth/one_gsp/{gsp_id}/?regime=in-day")
    r = response.json()
    gsp_truths_in_day = pd.DataFrame([GSPYield(**i).__dict__ for i in r])
    logger.debug(f"API request: in day. Found {len(gsp_truths_in_day)} data points")

    logger.debug(f"API request: forecast {gsp_id=}")
    response = requests.get(f"{API_URL}/v0/GB/solar/gsp/forecast/latest/{gsp_id}")
    r = response.json()
    forecast = pd.DataFrame([ForecastValue(**i).__dict__ for i in r])
    logger.debug(f"API request: forecast. Found {len(forecast)} data points")

    figs = []
    if show_yesterday == "both":
        options = [True, False]
    else:
        options = [show_yesterday]
    for option in options:

        if not option:
            logger.debug("Only showing todays results")
            today_start_datetime = datetime.now(timezone.utc)
            today_start_datetime = today_start_datetime.replace(
                hour=-0, minute=0, second=0, microsecond=0
            )

            forecast = forecast[forecast["target_time"] >= today_start_datetime]
            gsp_truths_in_day = gsp_truths_in_day[
                gsp_truths_in_day["datetime_utc"] >= today_start_datetime
            ]
            gsp_truths_day_after = gsp_truths_day_after[
                gsp_truths_day_after["datetime_utc"] >= today_start_datetime
            ]

            logger.debug("Done filtering data")
        else:
            logger.debug("showing yesterday results too")

        logger.debug(f"Making trace for in day with {len(gsp_truths_in_day)} data points")

        trace_in_day = go.Scatter(
            x=gsp_truths_in_day["datetime_utc"],
            y=gsp_truths_in_day["solar_generation_kw"] / 10**3,
            mode="lines",
            name="PV live: in-day",
            line={"dash": "dash", "color": "blue"},
        )

        logger.debug(f"Making trace for day after with {len(gsp_truths_day_after)} data points")

        trace_day_after = go.Scatter(
            x=gsp_truths_day_after["datetime_utc"],
            y=gsp_truths_day_after["solar_generation_kw"] / 10**3,
            mode="lines",
            name="PV live: Day-After",
            line={"dash": "solid", "color": "blue"},
        )

        logger.debug(f"Making trace for forecast with {len(forecast)} data points")

        trace_forecast = go.Scatter(
            x=forecast["target_time"],
            y=forecast["expected_power_generation_megawatts"],
            mode="lines",
            name="OCF: Forecast",
            line={"dash": "solid", "color": "green"},
        )

        if gsp_id == 0:
            title = "National"
        else:
            title = f"GSP {gsp_id}"

        fig = go.Figure(data=[trace_in_day, trace_day_after, trace_forecast])
        fig.update_layout(
            title=title,
            xaxis_title="Time [UTC]",
            yaxis_title="Solar generation [MW]",
        )
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        figs.append(fig)
        logger.debug(f"Done making plot {option}")

    logger.debug("Done making plot")
    if show_yesterday == "both":
        return figs
    else:
        return figs[0]


def gat_map_data(boundaries: Optional = None):
    """Makes a list of map plot of forecast"""

    # get all forecast
    route = "/v0/GB/solar/gsp/forecast/all"
    logger.debug(f"Get all gsp forecasts {route=}")
    r = requests.get(API_URL + route, params={"normalize": "true"})
    d = r.json()

    return d


def make_map_plot(boundaries: Optional = None, d: Optional[dict] = None):
    """Makes a list of map plot of forecast"""

    if d is None:
        d = gat_map_data(boundaries=boundaries)

    # get gsp boundaries
    if boundaries is None:
        boundaries = get_gsp_boundaries()

    if isinstance(boundaries, str):
        boundaries_dict = json.loads(boundaries)
        boundaries = gpd.GeoDataFrame.from_features(boundaries_dict["features"])

    forecasts = ManyForecasts(**d)

    # format predictions
    times = [
        forecast_value.target_time for forecast_value in forecasts.forecasts[1].forecast_values
    ]
    traces = []
    for normalize in [False, True]:
        for i in range(len(times)):
            predictions = {
                f.location.gsp_id: f.forecast_values[i].expected_power_generation_megawatts
                for f in forecasts.forecasts
            }
            predictions_normalized = {
                f.location.gsp_id: f.forecast_values[i].expected_power_generation_normalized
                for f in forecasts.forecasts
            }
            predictions_df = pd.DataFrame(list(predictions.items()), columns=["gsp_id", "value"])
            predictions_normalized_df = pd.DataFrame(
                list(predictions_normalized.items()), columns=["gsp_id", "value_normalized"]
            )
            predictions_normalized_df.fillna(0, inplace=True)

            predictions_df = predictions_df.join(
                predictions_normalized_df, on="gsp_id", rsuffix="_n"
            )

            boundaries_and_results = boundaries.join(predictions_df, on=["gsp_id"], rsuffix="_r")

            #  plot
            boundaries_and_results = boundaries_and_results[~boundaries_and_results.RegionID.isna()]
            boundaries_and_results.set_index("gsp_name", inplace=True)

            # make shape dict for plotting
            shapes_dict = json.loads(boundaries_and_results.to_json())

            # make label
            boundaries_and_results["label"] = " GSP id:" + boundaries_and_results["gsp_id"].astype(
                int
            ).astype(str)

            if normalize:
                zmax = 1
                z = boundaries_and_results.value_normalized
            else:
                zmax = 400
                z = boundaries_and_results.value.round(0)

            # plot it
            traces.append(
                go.Choroplethmapbox(
                    geojson=shapes_dict,
                    locations=boundaries_and_results.index,
                    z=z,
                    colorscale="YlOrRd",
                    # colorscale=[[0, 'rgb(255,255,255)'], [1,
                    # 'rgb(255,255,0)']],
                    # hoverinfo=trace,
                    hovertext=boundaries_and_results["label"].tolist(),
                    name=None,
                    zmax=zmax,
                    zmin=0,
                    # marker={"opacity": (boundaries_and_results.value_normalized).tolist()},
                    marker={"opacity": 0.5},
                )
            )

    figs = []
    for i in range(len(traces)):
        fig = go.Figure(data=traces[i])

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=4.5,
            mapbox_center={"lat": 56, "lon": -2},
        )
        fig.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 30},
            height=700,
        )
        fig.update_layout(title=f"Solar Generation [MW]: {times[i % len(times)].isoformat()}")

        figs.append(fig)

    # reshape in [normalize, times]
    logger.debug(f"Made {len(figs)} figures")
    figs = np.array([figs[0 : len(times)], figs[len(times) :]])

    logger.debug("Done making map plot")
    logger.debug(figs.shape)

    return figs


def make_pv_plot():
    """Make pv plot"""
    # get pv data
    # TODO

    fig = go.Figure()

    return fig
