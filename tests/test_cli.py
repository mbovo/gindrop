import pytest


def test_success():
    assert True


def test_import():
    import gindrop.cli
    assert gindrop.cli.main


def test_sig_handler():
    from gindrop import cli
    import signal
    assert cli.sig_handler(signal.SIGUSR1, None) is None


@pytest.mark.xfail
def test_sig_handler_real():
    from gindrop import cli
    cli.sig_handler(15, None)


def test_set_sig_handler_fails():
    from gindrop import cli
    import signal

    def mock_sigh_handler(signum, frame):
        assert signum == signal.SIGUSR1

    cli.set_sig_handler(mock_sigh_handler, [])


def test_set_sigh_handler():
    from gindrop import cli
    import os
    import signal

    def mock_sigh_handler(signum, frame):
        assert signum == signal.SIGUSR1

    cli.set_sig_handler(mock_sigh_handler)
    os.kill(os.getpid(), signal.SIGUSR1)


def test_main():
    from gindrop import cli

    class mockWsgi:

        def serve_forever(self):
            assert True

    cli.http_server = mockWsgi()
    cli.main()
