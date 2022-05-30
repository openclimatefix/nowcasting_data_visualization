from tabs.pv.plots import make_pv_plot


def test_make_pv_plot(pv_yields_and_systems):

    _ = make_pv_plot(pv_systems_ids=[1, 2], normalize=False)
    _ = make_pv_plot(pv_systems_ids=[1, 2], normalize=True)
