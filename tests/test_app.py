import os

from app import make_app


def test_app():

    os.environ["DB_URL_PV"] = "sqlite:///test.db"
    _ = make_app()
