""" Download nwp data """
import os
from typing import Optional

import fsspec
from pathy import Pathy


def download_data(replace: bool = False, local_filename: Optional[str] = "nwp_latest.netcdf"):
    """Get download data"""

    print(f"Downloading nwp data. {replace=} {local_filename=}")

    path = Pathy(os.getenv("NWP_AWS_PATH", "."))
    filename = f"{path}/latest.netcdf"

    # download file
    if not os.path.exists(local_filename) or replace:
        print(f"Downloading nwp data {filename}")
        fs = fsspec.open(filename).fs
        fs.get(filename, local_filename)
    else:
        print(f"Not downloading nwp data, as it already exists {local_filename=}")
