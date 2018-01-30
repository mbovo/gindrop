import json
import pytest
import io
import os
from gindrop import api

api.webapp.config['TESTING'] = True
appclient = api.webapp.test_client()
do_crypt = "?crypt=true"


def test_index():
    resp = appclient.get('/')
    assert resp.status == "200 OK"
    assert json.loads(resp.data)['msg'] == "This is Gindrop"


def test_configs():
    response = appclient.get('/configs')
    assert response.status == "200 OK"
    assert 'configs' in json.loads(response.data)


def test_secrets():
    response = appclient.get('/configs' + do_crypt)
    assert response.status == "200 OK"
    assert 'configs' in json.loads(response.data)


def test_failed_config():
    with pytest.raises(ValueError):
        j = api.manager.get_config_by_name("TestNotExistingConfig")


def test_failed_secret():
    with pytest.raises(ValueError):
        j = api.manager.get_secret_by_name("TestNotExistingConfig")


def test_write_config():

    # delete first if any zombie is left
    appclient.delete('/configs/config_pytest')

    data = dict(
        file=(io.BytesIO(b'Test config content'), "tmp.confg"),
    )
    response = appclient.put('/configs/config_pytest', content_type='multipart/form-data', data=data)
    assert response.status == "200 OK"


def test_write_secrets():

    # delete first if any zombie is left
    appclient.delete('/configs/config_pytest' + do_crypt)

    data = dict(
        file=(io.BytesIO(b'Test config content'), "tmp.cfg"),
    )
    response = appclient.put('/configs/config_pytest' + do_crypt, content_type='multipart/form-data', data=data)
    assert response.status == "200 OK"


def test_config():
    response = appclient.get('/configs/config_pytest')
    assert response.status == "200 OK"


def test_secret():
    response = appclient.get('/configs/config_pytest' + do_crypt)
    assert response.status == "200 OK"


def test_delete_secret():
    appclient.delete('/configs/config_pytest' + do_crypt)


def test_delete_config():
    appclient.delete('/configs/config_pytest')


def test_deploy():

    filename = os.path.join(os.path.dirname(__file__), 'files', 'deploy.yml')
    with open(filename, 'rb') as f:
        deploy = f.read()
    data = dict(
        file=(io.BytesIO(deploy), "deploy.yml"),
    )
    response = appclient.put('/deploy/deploy_pytest', content_type='multipart/form-data', data=data)

    assert response.status == "200 OK"

    appclient.delete('/service/redis')


def test_networks():
    response = appclient.get('/network')
    assert response.status == "200 OK"


def test_network():
    with pytest.raises(ValueError):
        j = api.manager.get_network(name="TestNotExisting")


def test_rem_network():
    response = appclient.delete('/network/mynet')
    assert response.status == "200 OK"
