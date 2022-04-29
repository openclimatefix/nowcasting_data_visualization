""" Callbacks functions """

from dash import Input, Output

from .plots import plot_nwp_data


def nwp_make_callbacks(app):
    """Make callbacks"""

    # @app.callback(
    #     [Output("nwp-dropdown-init-time", "options"),
    #     Output("nwp-dropdown-variables", "options")],
    #     Input("store-nwp-data", "data"),
    # )
    # def make_nwp_drop_downs(nwp_xr):
    #     variables = nwp_xr["variable"].values
    #     init_times = nwp_xr.init_time.values
    #
    #     return init_times, variables

    @app.callback(
        Output("nwp-plot", "figure"),
        [Input("nwp-dropdown-init-time", "value"), Input("nwp-dropdown-variables", "value")],
    )
    def make_nwp_plot(init_time, variable):
        fig = plot_nwp_data(init_time, variable)

        return fig

    return app
