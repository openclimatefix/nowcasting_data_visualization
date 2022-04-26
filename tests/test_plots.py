from plots import make_plot, make_map_plot


def test_make_plot():
    make_plot(gsp_id=1, show_yesterday=False)


def test_make_map_plot():
    make_map_plot()
