import pytest
from gindrop import me


def test_success():
    assert True


def test_import():
    import gindrop.me
    assert gindrop.me.Gindrop


def test_config():
    g = me.Gindrop
    assert g.config


def test_http_server():
    g = me.Gindrop
    assert g.http_server
