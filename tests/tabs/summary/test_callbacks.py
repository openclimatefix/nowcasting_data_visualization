from tabs.summary.callbacks import toggle_modal_function


def test_toggle_modal_function_open():

    click_data = {"points": [{"pointNumber": 111}]}
    close_button = None
    is_open = False
    fig = None

    is_open, fig = toggle_modal_function(
        click_data=click_data, close_button=close_button, is_open=is_open, fig=fig
    )

    assert is_open
    assert fig is not None


def test_toggle_modal_function_close():

    click_data = None
    close_button = 1
    is_open = True
    fig = None

    is_open, fig = toggle_modal_function(
        click_data=click_data, close_button=close_button, is_open=is_open, fig=fig
    )

    assert not is_open


def test_toggle_modal_function_dummy():
    """The callbacks seems to get called after fig is made"""
    click_data = None
    close_button = None
    is_open = True
    fig = {}

    is_open, fig = toggle_modal_function(
        click_data=click_data, close_button=close_button, is_open=is_open, fig=fig
    )

    assert is_open
    assert fig is not None
