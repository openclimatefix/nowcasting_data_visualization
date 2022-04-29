from tabs.nwp.download import download_data


def test_download_data(nwp_data_filename):

    import os

    assert os.path.exists(nwp_data_filename)
    download_data(local_filename=nwp_data_filename)
