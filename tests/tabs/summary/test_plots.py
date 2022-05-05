from tabs.summary.plots import make_map_plot, make_plots


def test_make_plot():
    plots = make_plots(gsp_id=1)
    assert len(plots) == 2


def test_make_map_plot():
    make_map_plot()
