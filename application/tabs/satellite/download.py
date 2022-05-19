""" Download nwp data """
import os
from typing import Optional

import fsspec
from log import logger


def download_satellite_data(
    replace: bool = False, local_filename: Optional[str] = "satellite_latest.zarr.zip"
):
    """Get download data"""

    logger.info(f"Downloading satellite data. {replace=} {local_filename=}")

    filename = os.getenv("SATELLITE_AWS_FILENAME", "./satellite_latest.zarr.zip")

    # download file
    if not os.path.exists(local_filename) or replace:
        logger.debug(f"Downloading satellite data {filename}")
        print(f"Downloading satellite data {filename}")
        fs = fsspec.open(filename).fs
        fs.get(filename, local_filename)
        logger.debug(f"Downloading satellite data {filename}: done")
    else:
        logger.debug(f"Not downloading satellite data, as it already exists {local_filename=}")
