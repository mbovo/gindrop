from __future__ import absolute_import, division, print_function
import logging
import json
from gindrop import core, swarm
from flask import Flask, request
from flask_restful import Api, Resource
from flasgger import Swagger

logger = logging.getLogger(__name__)
config = core.Config()

app = Flask(__name__)
logger.info('Init flask ')

api = Api(app)
logger.info('Init API ')

swagger = Swagger(app)
logger.info('Init Swagger ')


todos = {}
manager = swarm.Manager()


@app.route('/')
def index():
    return json.dumps({'msg': 'This is Gindrop'})


@app.route('/configs', methods=['GET'])
def get_configs():
    """
    Retrieve all registerd configurations
    ---
    parameters: []
    responses: {}
     """
    cs = manager.get_configs()
    data = {'configs': []}
    for c in cs:
        data["configs"].append(c.attrs)
    return app.response_class(response=json.dumps(data), status=200, mimetype='application/json')


@app.route('/configs/<string:config_name>')
def get_config(config_name):
    """
    Retrieve a specific configuration by name
    ---
    parameters:
      - in: path
        name: config_name
        required: true
    responses: {}
     """
    logger.info("Reading config: " + config_name)
    c = manager.get_config_by_name(config_name)
    return app.response_class(response=json.dumps(c.attrs), status=200, mimetype='application/json')


@app.route('/configs/<string:config_name>', methods=['PUT'])
def set_config(config_name):
    """
    Save a new config with given name
    ---
    parameters:
      - in: path
        name: config_name
        type: string
        required: true
      - in: formData
        name: file
        type: file
        required: true
    consumes:
      - application/json
    responses: {}
     """
    logger.info("Writing config: " + config_name)
    #labels = request.args.get('labels', False)
    #logger.info("Optional labels: " + labels)
    c = manager.set_config(config_name, request.files['file'].read(), "")
    return app.response_class(response=json.dumps(c.attrs), status=200, mimetype='application/json')


@app.route('/configs/<string:config_name>', methods=['DELETE'])
def rem_config(config_name):
    """
    Remove config with given name
    ---
    parameters:
      - in: path
        name: config_name
        type: string
        required: true
    consumes:
      - application/json
    responses: {}
     """
    logger.info("Delete config: " + config_name)
    ret = manager.rem_config(config_name)
    return app.response_class(response=json.dumps(ret), status=200, mimetype='application/json')
