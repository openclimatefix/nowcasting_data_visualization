from app import make_app


def test_app(db_session, pv_yields_and_systems):

    _ = make_app()
