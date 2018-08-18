
def test_configuration():
    import clickable_bootstrap
    import clickable_logging
    import logging
    import os.path
    clickable_logging.bootstrap(clickable_bootstrap.__name__).log.setLevel(logging.DEBUG)
    print(clickable_bootstrap._search_configuration(os.path.dirname(__file__)))
