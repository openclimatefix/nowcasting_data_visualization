from tabs.nwp.plots import plot_nwp_data


def test_nwp_plot(nwp_data_filename):
    init_time = "2022-01-01T00:00:00"
    variable = "dswrf"
    plot_nwp_data(init_time, variable, filename=nwp_data_filename)
