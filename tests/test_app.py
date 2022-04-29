from app import make_app


def test_app(db_session, pv_yields_and_systems, input_data_last_updated, nwp_data_filename):

    _ = make_app()
