import json
import pytest
import io
from gindrop import api


def test_index():
    j = json.loads(api.index())
    assert j['msg'] == "This is Gindrop"


def test_configs():
    j = api.get_configs()
    assert json.loads(j.get_data())['configs']


def test_config():
    with pytest.raises(ValueError):
        j = api.get_config("TestNotExistingConfig")


def test_write_config():

    data = dict(
        file=(io.BytesIO(b'Test config content'), "tmp.confg"),
    )
    response = api.app.put('/configs/config_pytest', content_type='multipart/form-data', data=data)
    assert response.status == 200
