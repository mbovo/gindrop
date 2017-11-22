import json
from gindrop import api


def test_index():
    j = json.loads(api.index())
    assert j['msg'] == "This is Gindrop"


def test_configs():
    j = api.get_configs()
    print j
    assert j['configs']
