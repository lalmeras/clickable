
def test_example():
    """
    Initialize a module logger and try all outputs.

    Launch with '-s' argument to see test output.
    Beware that output is mixed with pytest output.

    No assertion, this test is here to provide a fast
    output example.
    """
    import sys
    import clickable_logging
    clog = clickable_logging.bootstrap(__name__)
    _log(clog)


def test_bootstrap(capsys):
    """
    Initialize a module logger and try all outputs.
    As output is captured, colors are deactivated.

    Launch with '-s' argument to see test output.
    """
    import sys
    import clickable_logging
    import logging
    clog = clickable_logging.bootstrap(__name__)
    # enable all levels
    clog.log.setLevel(logging.DEBUG)
    clog.stdout.setLevel(logging.DEBUG)
    clog.stderr.setLevel(logging.DEBUG)
    # check stream for all loggers and levels
    _log(clog, capsys=capsys)


def test_bootstrap_none(capsys):
    """
    Check behavior if name parameter is None
    """
    import sys
    import clickable_logging
    clog = clickable_logging.bootstrap(None)
    # for example
    clog.stderr.warn("test_bootstrap_none")
    captured = capsys.readouterr()
    # if name is None, ROOT is used as output name
    assert "ROOT" in captured.err
    assert "test_bootstrap_none" in captured.err


def _log(clog, capsys=None):
    import random
    log_levels = [
        'debug',
        'info',
        'warning',
        'error',
        'critical'
    ]
    for logger_name in ['stdout', 'stderr', 'log']:
        logger = getattr(clog, logger_name)
        for level in log_levels:
            # perform output check is capsys is provided
            if capsys is not None:
                capsys.readouterr()
            message = "message %d" % (random.randint(0, 1000),)
            getattr(logger, level)(message)
            if capsys is not None:
                captured = capsys.readouterr()
                stream_name = 'out' if 'out' in logger_name else 'err'
                stream = getattr(captured, stream_name)
                assert message in stream
                if logger_name in ['log', 'stderr']:
                    # log and sterr print log level
                    assert level.lower() in stream.lower()
                if logger_name in ['stderr']:
                    # stderr use output_name instead of name
                    assert clog.output_name in stream
                if logger_name in ['log']:
                    # log use technical name
                    assert clog.name in stream
                if logger_name in ['stdout']:
                    # stdout outputs raw data
                    assert level.lower() not in stream.lower()
                    assert clog.output_name not in stream
