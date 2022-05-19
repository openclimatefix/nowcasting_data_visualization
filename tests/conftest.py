""" Setup for pytests """
import os
import tempfile
from datetime import datetime, timedelta

import numpy as np
import pytest
import xarray as xr
import zarr
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.fake import make_fake_forecast, make_fake_national_forecast
from nowcasting_datamodel.models.base import Base_Forecast, Base_PV
from nowcasting_datamodel.models.models import InputDataLastUpdatedSQL
from nowcasting_datamodel.models.pv import PVSystem, PVSystemSQL, PVYield


@pytest.fixture
def db_connection():
    """Database connection"""
    url = os.environ["DB_URL"]

    connection = DatabaseConnection(url=url)
    Base_Forecast.metadata.create_all(connection.engine)
    Base_PV.metadata.create_all(connection.engine)

    yield connection

    Base_Forecast.metadata.drop_all(connection.engine)
    Base_PV.metadata.drop_all(connection.engine)


@pytest.fixture(scope="function", autouse=True)
def db_session(db_connection):
    """Creates a new database session for a test."""

    with db_connection.get_session() as s:
        s.begin()
        yield s
        s.rollback()


@pytest.fixture()
def input_data_last_updated(db_session):
    """Add InputDataLastUpdatedSQL to db"""
    input = InputDataLastUpdatedSQL(
        gsp=datetime(2022, 1, 1),
        nwp=datetime(2022, 1, 1),
        pv=datetime(2022, 1, 1),
        satellite=datetime(2022, 1, 1),
    )

    db_session.add(input)
    db_session.commit()


@pytest.fixture()
def forecast(db_session):
    """Add InputDataLastUpdatedSQL to db"""
    f1 = make_fake_forecast(session=db_session, gsp_id=1)
    f2 = make_fake_national_forecast(session=db_session)

    db_session.add_all([f1, f2])
    db_session.commit()


@pytest.fixture()
def pv_yields_and_systems(db_session):
    """Create pv yields and systems

    Pv systems: Two systems
    PV yields:
        FOr system 1, pv yields from 2 hours ago to 4 in the future at 5 minutes intervals
        For system 2: 1 pv yield at 16.00
    """

    # this pv systems has same coordiantes as the first gsp
    pv_system_sql_1: PVSystemSQL = PVSystem(
        pv_system_id=10003,
        provider="pvoutput.org",
        status_interval_minutes=5,
        longitude=-1.293,
        latitude=51.76,
    ).to_orm()
    pv_system_sql_2: PVSystemSQL = PVSystem(
        pv_system_id=10020,
        provider="pvoutput.org",
        status_interval_minutes=5,
        longitude=0,
        latitude=56,
    ).to_orm()

    t0_datetime_utc = datetime.utcnow() - timedelta(hours=2)

    pv_yield_sqls = []
    for hour in range(0, 6):
        for minute in range(0, 60, 5):
            datetime_utc = t0_datetime_utc + timedelta(hours=hour - 2, minutes=minute)
            pv_yield_1 = PVYield(
                datetime_utc=datetime_utc,
                solar_generation_kw=hour + minute / 100,
            ).to_orm()
            if datetime_utc.hour in [22, 23, 0, 1, 2]:
                pv_yield_1.solar_generation_kw = 0
            pv_yield_1.pv_system = pv_system_sql_1
            pv_yield_sqls.append(pv_yield_1)

    pv_yield_4 = PVYield(datetime_utc=datetime(2022, 1, 1, 4), solar_generation_kw=4).to_orm()
    pv_yield_4.pv_system = pv_system_sql_2
    pv_yield_sqls.append(pv_yield_4)

    # add to database
    db_session.add_all(pv_yield_sqls)
    db_session.add(pv_system_sql_1)
    db_session.add(pv_system_sql_2)

    db_session.commit()

    return {
        "pv_yields": pv_yield_sqls,
        "pv_systems": [pv_system_sql_1, pv_system_sql_2],
    }


@pytest.fixture
def nwp_data_filename():
    """Make fake nwp data"""
    with tempfile.NamedTemporaryFile(suffix=".netcdf") as t:
        os.environ["NWP_AWS_FILENAME"] = t.name

        # middle of the UK
        t0_datetime_utc = datetime(2022, 1, 1)
        image_size = 1000
        time_steps = 10

        ONE_KILOMETER = 10**3

        # 4 kilometer spacing seemed about right for real satellite images
        x = 2 * ONE_KILOMETER * np.array((range(0, image_size)))
        y = 2 * ONE_KILOMETER * np.array((range(image_size, 0, -1)))

        # time = pd.date_range(start=t0_datetime_utc, freq="30T", periods=10)
        step = [timedelta(minutes=60 * i) for i in range(0, time_steps)]

        coords = (
            ("init_time", [t0_datetime_utc]),
            ("variable", np.array(["dswrf"])),
            ("step", step),
            ("x", x),
            ("y", y),
        )

        nwp = xr.DataArray(
            abs(  # to make sure average is about 100
                np.random.uniform(
                    0,
                    200,
                    size=(1, 1, time_steps, image_size, image_size),
                )
            ),
            coords=coords,
            name="data",
        )  # Fake data for testing!
        nwp = nwp.to_dataset(name="UKV")

        nwp.to_netcdf(t.name, engine="h5netcdf", mode="w")

        yield t.name


@pytest.fixture
def satellite_data_filename():
    """Make fake satellite data"""
    with tempfile.NamedTemporaryFile(suffix=".zarr.zip") as t:
        os.environ["SATELLITE_AWS_FILENAME"] = t.name

        # middle of the UK
        t0_datetime_utc = datetime(2022, 1, 1)
        image_size = 1000
        time_steps = 10

        ONE_KILOMETER = 10**3

        # 4 kilometer spacing seemed about right for real satellite images
        x = 2 * ONE_KILOMETER * np.array((range(0, image_size)))
        y = 2 * ONE_KILOMETER * np.array((range(image_size, 0, -1)))

        # time = pd.date_range(start=t0_datetime_utc, freq="30T", periods=10)
        time = [t0_datetime_utc + timedelta(minutes=60 * i) for i in range(0, time_steps)]

        coords = (
            ("time", time),
            ("variable", np.array(["IR_016"])),
            ("x_geostationary", x),
            ("y_geostationary", y),
            # ("x_osgb", x),
            # ("y_osgb", y),
        )

        sat = xr.DataArray(
            abs(  # to make sure average is about 100
                np.random.uniform(
                    0,
                    200,
                    size=(time_steps, 1, image_size, image_size),
                )
            ),
            coords=coords,
            name="data",
        )  # Fake data for testing!
        sat = sat.to_dataset()

        with zarr.ZipStore(t.name) as store:
            sat.to_zarr(store, compute=True, mode="w")

        yield t.name
