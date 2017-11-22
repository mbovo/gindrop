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

    api.app.config['TESTING'] = True
    client = api.app.test_client()

    # delete first if any zombie is left
    client.delete('/configs/config_pytest')

    data = dict(
        file=(io.BytesIO(b'Test config content'), "tmp.confg"),
    )
    response = client.put('/configs/config_pytest', content_type='multipart/form-data', data=data)
    assert response.status == "200 OK"

    # delete to cleanup
    client.delete('/configs/config_pytest')
