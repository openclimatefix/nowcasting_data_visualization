from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import json
import requests
import plotly.graph_objects as go
from datetime import datetime, timezone
from typing import List

import logging

from dash.dependencies import Input, Output, State
from nowcasting_datamodel.models import Forecast, GSPYield, ManyForecasts, ForecastValue

logger = logging.getLogger(__name__)
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


URL = "http://nowcasting-api-development.eu-west-1.elasticbeanstalk.com"

app = Dash(__name__, external_stylesheets=external_stylesheets +[dbc.themes.BOOTSTRAP] )


def make_pv_plot():
    # get pv data
    # TODO

    fig = go.Figure()

    return fig


def make_plot(gsp_id: int = 0, show_yesterday: bool = True):
    print(f"Making plot for gsp {gsp_id}, {show_yesterday=}")
    print("API request: day after")
    response = requests.get(f"{URL}/v0/GB/solar/gsp/truth/one_gsp/{gsp_id}/?regime=day-after")
    r = response.json()
    gsp_truths_day_after = pd.DataFrame([GSPYield(**i).__dict__ for i in r])

    print("API request: in day")
    response = requests.get(f"{URL}/v0/GB/solar/gsp/truth/one_gsp/{gsp_id}/?regime=in-day")
    r = response.json()
    gsp_truths_in_day = pd.DataFrame([GSPYield(**i).__dict__ for i in r])

    print(f"API request: forecast {gsp_id=}")
    response = requests.get(f"{URL}/v0/GB/solar/gsp/forecast/latest/{gsp_id}")
    r = response.json()
    forecast = pd.DataFrame([ForecastValue(**i).__dict__ for i in r])

    if not show_yesterday:
        print("Only showing todays results")
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

        print("Done filtering data")

    print("Making trace for in day")

    trace_in_day = go.Scatter(
        x=gsp_truths_in_day["datetime_utc"],
        y=gsp_truths_in_day["solar_generation_kw"] / 10 ** 3,
        mode="lines",
        name="PV live Truth: in-day",
        line={"dash": "dash", "color": "blue"},
    )

    print("Making trace for day after")

    trace_day_after = go.Scatter(
        x=gsp_truths_day_after["datetime_utc"],
        y=gsp_truths_day_after["solar_generation_kw"] / 10 ** 3,
        mode="lines",
        name="PV live Truth: Day-After",
        line={"dash": "solid", "color": "blue"},
    )

    print("Making trace for forecast")

    trace_forecast = go.Scatter(
        x=forecast["target_time"],
        y=forecast["expected_power_generation_megawatts"],
        mode="lines",
        name="OCF: Forecast",
        line={"dash": "solid", "color": "green"},
    )

    if gsp_id == 0:
        title = f"National - Forecast and Truths"
    else:
        title = f"GSP {gsp_id} - Forecast and Truths"

    fig = go.Figure(data=[trace_in_day, trace_day_after, trace_forecast])
    fig.update_layout(
        title=title,
        xaxis_title="Time [UTC]",
        yaxis_title="Solar generation [MW]",
    )

    print("Done making plot")
    return fig


def make_map_plot():

    # get gsp boundaries
    print("Get gsp boundaries")
    r = requests.get(URL + "/v0/GB/solar/gsp/gsp_boundaries/")
    d = r.json()
    boundaries = gpd.GeoDataFrame.from_features(d["features"])

    # get all forecast
    print("Get all gsp forecasts")
    r = requests.get(URL + "/v0/GB/solar/gsp/forecast/all/")
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
    boundaries_and_results.set_index('gsp_name', inplace=True)

    # make shape dict for plotting
    shapes_dict = json.loads(boundaries_and_results.to_json())

    # make label
    boundaries_and_results["label"] = (" GSP id:"
        + boundaries_and_results["gsp_id"].astype(int).astype(str)
    )

    # plot it
    fig = go.Figure(data=
        go.Choroplethmapbox(
            geojson=shapes_dict,
            locations=boundaries_and_results.index,
            z=boundaries_and_results.value.round(0),
            colorscale="solar",
            # hoverinfo=trace,
            hovertext=boundaries_and_results['label'].tolist(),
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
        mapbox_bearing=90,
    )
    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 30})
    fig.update_layout(title=f"Solar Generation [MW]: {time.isoformat()}")

    print("Done making map plot")
    return fig


modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("GSP plot"),
                dbc.ModalBody([
                    html.H4(id='hover_info'),
                    dcc.Graph(
                        id='plot-modal',
                        figure=make_plot(gsp_id=1, show_yesterday=False)
                    )
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            ],
            id="modal",
            style={"width": "50%"}
        ),
    ]
)

tab1 = html.Div(
    [
        html.H3("Summary"),
        dcc.RadioItems(
            id="radio-gsp-pv",
            options=[
                {"label": "GSP Forecast", "value": "Forecast"},
                {"label": "PVLive", "value": "PVLive"},
            ],
            value="Forecast",
        ),
        dbc.Row([
        dcc.Graph(id="plot-uk", figure=make_map_plot(), style={"width": "90%"}),
            modal]),
        dcc.Checklist(["Yesterday"], [""], id="tick-show-yesterday"),
        dcc.Graph(id="plot-national", figure=make_plot(gsp_id=0, show_yesterday=False)),
    ]
)

tab2 = html.Div(
    [
        html.H3("Summary"),
        dcc.Dropdown(list(range(0, 399)), "0", id="gsp-dropdown"),
        html.Div(id="gsp-output-container"),
        dcc.Graph(id="plot-gsp", figure=make_plot(gsp_id=0)),
    ]
)


app.layout = html.Div(
    children=[
        html.H1(children="Data visualization dashboard"),
        dcc.Tabs(
            id="tabs-example-graph",
            value="tab-1-example-graph",
            children=[
                dcc.Tab(tab1, label="Summary", value="tab-1-example-graph"),
                dcc.Tab(tab2, label="GSP", value="tab-2-example-graph"),
                # dcc.Tab(label='NWP', value='tab-3-example-graph'),
                # dcc.Tab(label='Satellite', value='tab-4-example-graph'),
            ],
        ),
        # html.Div(id="tabs-content-example-graph"),
    ]
)


@app.callback(
    Output("tabs-content-example-graph", "children"), Input("tabs-example-graph", "value")
)
def render_content(tab):
    if tab == "tab-1-example-graph":
        return tab1
    elif tab == "tab-2-example-graph":
        return tab2


# @app.callback(Output("plot-uk", "figure"), Input("radio-gsp-pv", "value"))
# def update_national_plot(value):
#     print(f"Updating national plot with {value}")
#     if value == "Forecast":
#         fig = make_map_plot()
#     else:
#         fig = make_pv_plot()
#     return fig


@app.callback(
    [Output("gsp-output-container", "children"), Output("plot-gsp", "figure")],
    [Input("gsp-dropdown", "value")],
)
def update_output(gsp_value: str):
    print(f"Updating GSP value {gsp_value}")
    fig = make_plot(gsp_id=int(gsp_value), show_yesterday=True)
    return f"You have selected {gsp_value}", fig


@app.callback(
    Output("plot-national", "figure"),
    Input("tick-show-yesterday", "value"),
)
def update_output(yesterday_value: List[str]):
    print(f"Updating National plot, {yesterday_value=}")
    show_yesterday = True if "Yesterday" in yesterday_value else False
    fig = make_plot(gsp_id=0, show_yesterday=show_yesterday)
    return fig


@app.callback(
    Output("modal", "is_open"),
    Output("hover_info","children"),
    Output("plot-modal", "figure"),
    [Input("plot-uk", "clickData"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(hover_data, close_button, is_open):

    print(f'{hover_data=} {close_button=} {is_open=}')

    if hover_data:
        print(hover_data)
        print(hover_data['points'][0]['pointNumber'])
        hovertext = hover_data['points'][0]['location'] + hover_data['points'][0]['hovertext']
        gsp_id = int(hover_data['points'][0]['pointNumber'] + 1)
        text = hovertext
        fig = make_plot(gsp_id=gsp_id, show_yesterday=False)
        return not is_open,text, fig
    return is_open, None, None


if __name__ == "__main__":
    app.run_server(debug=True)
