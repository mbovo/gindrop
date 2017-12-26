import os


def test_Config():
    import gindrop.core
    assert gindrop.core
    assert gindrop.core.logger
    # Setting values
    os.environ['GINDROP_SERVER'] = 'localhost'
    os.environ['GINDROP_PORT'] = '8080'
    os.environ['GINDROP_LOG_LEVEL'] = 'DEBUG'
    os.environ['GINDROP_STOP_TIMEOUT'] = '20'

    # Load object
    conf = gindrop.core.Config()

    # Test for values (method #1)
    assert conf.port == '8080'
    assert conf.server == 'localhost'
    assert conf.log_level == 'DEBUG'
    assert conf.stop_timeout == '20'

    # Test for iterator
    for i in conf:
        assert conf[i]

    # Test for values (method #2)
    assert conf['port'] == '8080'

    # Test string
    assert "port" in str(conf)

    # Test for invalid values
    try:
        conf['invalid']
    except Exception as e:
        assert type(e) == KeyError


# def test_Orchestrator():#

#    class myWrap:
#        def method(self, str):
#            return str

#    import gindrop.core
#    o = gindrop.core.Orchestrator(myWrap())
#    assert o.method('hallo') == 'hallo'
