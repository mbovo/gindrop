import json
import pytest
import io
from gindrop import api

api.app.config['TESTING'] = True
client = api.app.test_client()
do_crypt = "?crypt=true"


def test_index():
    j = json.loads(api.index())
    assert j['msg'] == "This is Gindrop"


def test_configs():
    response = client.get('/configs')
    assert response.status == "200 OK"
    assert json.loads(response.data)['configs']


def test_secrets():
    response = client.get('/configs' + do_crypt)
    assert response.status == "200 OK"
    assert json.loads(response.data)['configs']


def test_config():
    with pytest.raises(ValueError):
        j = api.manager.get_config_by_name("TestNotExistingConfig")


def test_secret():
    with pytest.raises(ValueError):
        j = api.manager.get_secret_by_name("TestNotExistingConfig")


def test_write_config():

    # delete first if any zombie is left
    client.delete('/configs/config_pytest')

    data = dict(
        file=(io.BytesIO(b'Test config content'), "tmp.confg"),
    )
    response = client.put('/configs/config_pytest', content_type='multipart/form-data', data=data)
    assert response.status == "200 OK"

    # delete to cleanup
    client.delete('/configs/config_pytest')


def test_write_secrets():

    # delete first if any zombie is left
    client.delete('/configs/config_pytest' + do_crypt)

    data = dict(
        file=(io.BytesIO(b'Test config content'), "tmp.confg" + do_crypt),
    )
    response = client.put('/configs/config_pytest' + do_crypt, content_type='multipart/form-data', data=data)
    assert response.status == "200 OK"

    # delete to cleanup
    client.delete('/configs/config_pytest' + do_crypt)
