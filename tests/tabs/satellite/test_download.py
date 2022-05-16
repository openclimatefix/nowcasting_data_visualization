from tabs.satellite.download import download_satellite_data


def test_download_data(satellite_data_filename):

    import os

    satellite_data_filename = "latest.zarr.zip"
    download_satellite_data(local_filename=satellite_data_filename)
