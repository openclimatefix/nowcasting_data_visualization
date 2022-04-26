from dash import Output, Input, State

from typing import List

from plots import make_plot


def make_callbacks(app):

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
    def update_national_output(yesterday_value: List[str]):
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

    return app