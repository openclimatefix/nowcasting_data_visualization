"""Main plots function """
import json
import logging
import os
from datetime import datetime, timezone

import geopandas as gpd
import pandas as pd
import requests
from nowcasting_datamodel.models import ForecastValue, GSPYield, ManyForecasts
from plotly import graph_objects as go

API_URL = os.getenv("API_URL")
assert API_URL is not None, "API_URL has not been set"

logger = logging.getLogger(__name__)


def make_plot(gsp_id: int = 0, show_yesterday: bool = True):
    """Make true and forecast plots"""
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

    if not show_yesterday:
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

    logger.debug(f"Making trace for in day with {len(gsp_truths_in_day)} data points")

    trace_in_day = go.Scatter(
        x=gsp_truths_in_day["datetime_utc"],
        y=gsp_truths_in_day["solar_generation_kw"] / 10**3,
        mode="lines",
        name="PV live Truth: in-day",
        line={"dash": "dash", "color": "blue"},
    )

    logger.debug(f"Making trace for day after with {len(gsp_truths_day_after)} data points")

    trace_day_after = go.Scatter(
        x=gsp_truths_day_after["datetime_utc"],
        y=gsp_truths_day_after["solar_generation_kw"] / 10**3,
        mode="lines",
        name="PV live Truth: Day-After",
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
        title = "National - Forecast and Truths"
    else:
        title = f"GSP {gsp_id} - Forecast and Truths"

    fig = go.Figure(data=[trace_in_day, trace_day_after, trace_forecast])
    fig.update_layout(
        title=title,
        xaxis_title="Time [UTC]",
        yaxis_title="Solar generation [MW]",
    )

    logger.debug("Done making plot")
    return fig


def make_map_plot():
    """Make map plot of forecast"""

    # get gsp boundaries
    logger.debug("Get gsp boundaries")
    r = requests.get(API_URL + "/v0/GB/solar/gsp/gsp_boundaries/")
    d = r.json()
    boundaries = gpd.GeoDataFrame.from_features(d["features"])

    # get all forecast
    logger.debug("Get all gsp forecasts")
    r = requests.get(API_URL + "/v0/GB/solar/gsp/forecast/all/")
    d = r.json()
    forecasts = ManyForecasts(**d)

    # format predictions
    time = forecasts.forecasts[1].forecast_values[0].target_time
    predictions = {
        f.location.gsp_id: f.forecast_values[0].expected_power_generation_megawatts
        for f in forecasts.forecasts
    }
    predictions_df = pd.DataFrame(list(predictions.items()), columns=["gsp_id", "value"])

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

    # plot it
    fig = go.Figure(
        data=go.Choroplethmapbox(
            geojson=shapes_dict,
            locations=boundaries_and_results.index,
            z=boundaries_and_results.value.round(0),
            colorscale="solar",
            # hoverinfo=trace,
            hovertext=boundaries_and_results["label"].tolist(),
            name=None,
            zmax=500,
            zmin=0,
            marker={"opacity": 0.5},
        )
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=4.5,
        mapbox_center={"lat": 56, "lon": -2},
    )
    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 30},
        height=700,
    )
    fig.update_layout(title=f"Solar Generation [MW]: {time.isoformat()}")

    logger.debug("Done making map plot")
    return fig


def make_pv_plot():
    """Make pv plot"""
    # get pv data
    # TODO

    fig = go.Figure()

    return fig
