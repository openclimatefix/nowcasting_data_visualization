from tabs.nwp.plots import plot_nwp_data


def test_nwp_plot():
    init_time = "2022-04-18T12:00:00"
    variable = "dswrf"
    plot_nwp_data(init_time, variable)
