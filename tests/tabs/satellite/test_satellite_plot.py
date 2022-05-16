from tabs.satellite.plots import plot_satellite_data


def test_satellite_plot(satellite_data_filename):
    variable = "IR_016"
    plot_satellite_data(variable, filename=satellite_data_filename)
