""" Download nwp data """
import logging
import os
from typing import Optional

import fsspec
from pathy import Pathy

logger = logging.getLogger(__name__)


def download_data(replace: bool = False, local_filename: Optional[str] = "nwp_latest.netcdf"):
    """Get download data"""

    logger.info(f"Downloading nwp data. {replace=} {local_filename=}")

    filename = os.getenv("NWP_AWS_FILENAME", "./nwp_latest.netcdf")

    # download file
    if not os.path.exists(local_filename) or replace:
        logger.debug(f"Downloading nwp data {filename}")
        fs = fsspec.open(filename).fs
        fs.get(filename, local_filename)
    else:
        logger.debug(f"Not downloading nwp data, as it already exists {local_filename=}")
