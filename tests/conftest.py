""" Setup for pytests """
import os
from datetime import datetime, timedelta

import pytest
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_Forecast, Base_PV
from nowcasting_datamodel.models.models import InputDataLastUpdatedSQL
from nowcasting_datamodel.models.pv import PVSystem, PVSystemSQL, PVYield


@pytest.fixture
def db_connection():
    """Database connection"""
    url = "sqlite:///test.db"
    os.environ["DB_URL_PV"] = url
    os.environ["DB_URL"] = url

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
    input = InputDataLastUpdatedSQL(
        gsp=datetime(2022, 1, 1),
        nwp=datetime(2022, 1, 1),
        pv=datetime(2022, 1, 1),
        satellite=datetime(2022, 1, 1),
    )

    db_session.add(input)
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
