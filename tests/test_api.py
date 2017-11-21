import json


def test_index():
    from gindrop import api
    j = json.loads(api.index())
    assert j['msg'] == "hallo world"
