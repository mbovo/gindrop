from __future__ import absolute_import, division, print_function
import json
import logging
from flask import Flask, Blueprint, request, redirect, url_for
from flasgger import Swagger
from . import core, swarm

# aliases:
logger = logging.getLogger(__name__)
config = core.config

logger.info('Init Flask ')
webapp = Flask(__name__)
webapp.config['SWAGGER'] = {"title": "Gindrop - API Wrapper", "uiversion": 2}
logger.debug(str(webapp.config))

logger.info('Init Swagger ')
swagger = Swagger(webapp, template={"info": {"title": "Gindrop - API Wrapper", "version": "1.0"}})
logger.debug(str(swagger.config))

logger.info('Init Orchestrator Backend')
manager = swarm.Manager()

v1 = Blueprint('v1', __name__)


@webapp.route('/')
def index():
    # return redirect(url_for('flasgger.apidocs'))
    return json.dumps({'msg': 'This is Gindrop'})


@webapp.route('/configs', methods=['GET'])
@v1.route('/configs', methods=['GET'])
def get_configs():
    """
    Retrieve all registerd configurations
    ---
    parameters:
      - in: query
        name: crypt
        required: true
        schema:
          type: boolean
        description: Configuration taken from encrypted ones
    responses: {}
     """
    sec = request.args.get('crypt', 'false')
    if sec == 'true':
        cs = manager.get_secrets()
    else:
        cs = manager.get_configs()
    data = {'configs': []}
    for c in cs:
        data["configs"].append(c.attrs)
    return webapp.response_class(response=json.dumps(data), status=200, mimetype='application/json')


@webapp.route('/configs/<string:config_name>')
@v1.route('/configs/<string:config_name>')
def get_config(config_name):
    """
    Retrieve a specific configuration by name
    ---
    parameters:
      - in: path
        name: config_name
        required: true
        description: "Name of the configuration to retrieve"
      - in: query
        name: crypt
        required: true
        schema:
          type: boolean
        description: Configuration taken from encrypted ones
    responses: {}
     """
    logger.info("Reading config: " + config_name)
    sec = request.args.get('crypt', 'false')
    if sec == 'true':
        c = manager.get_secret_by_name(config_name)
    else:
        c = manager.get_config_by_name(config_name)
    return webapp.response_class(response=json.dumps(c.attrs), status=200, mimetype='application/json')


@webapp.route('/configs/<string:config_name>', methods=['PUT'])
@v1.route('/configs/<string:config_name>', methods=['PUT'])
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
      - in: query
        name: crypt
        required: true
        schema:
          type: boolean
        description: Configuration stored as encrypted
    consumes:
      - application/json
    responses: {}
     """
    logger.info("Writing config: " + config_name)
    # labels = request.args.get('labels', False)
    # logger.info("Optional labels: " + labels)
    sec = request.args.get('crypt', 'false')
    if sec == 'true':
        c = manager.set_secret(config_name, request.files['file'].read(), "")
    else:
        c = manager.set_config(config_name, request.files['file'].read(), "")

    return webapp.response_class(response=json.dumps(c.attrs), status=200, mimetype='application/json')


@webapp.route('/configs/<string:config_name>', methods=['DELETE'])
@v1.route('/configs/<string:config_name>', methods=['DELETE'])
def rem_config(config_name):
    """
    Remove config with given name
    ---
    parameters:
      - in: path
        name: config_name
        type: string
        required: true
      - in: query
        name: crypt
        required: true
        schema:
          type: boolean
        description: Configuration deleted from encrypted ones
    consumes:
      - application/json
    responses: {}
     """
    logger.info("Delete config: " + config_name)
    sec = request.args.get('crypt', 'false')
    if sec == 'true':
        ret = manager.rem_secret(config_name)
    else:
        ret = manager.rem_config(config_name)

    return webapp.response_class(response=json.dumps(ret), status=200, mimetype='application/json')


@webapp.route('/service/<string:service_name>', methods=['DELETE'])
@v1.route('/service/<string:service_name>', methods=['DELETE'])
def do_remove_svc(service_name):
    try:
        jdata = manager.rem_service(service_name)
    except Exception as e:
        #raise e
        return webapp.response_class(response=json.dumps({'error': str(e)}), status=500, mimetype='application/json')

    return webapp.response_class(response=jdata, status=200, mimetype='application/json')


@webapp.route('/deploy/<string:service_name>', methods=['PUT'])
@v1.route('/deploy/<string:service_name>', methods=['PUT'])
def do_deploy(service_name):
    """
    Deploy a new service
    ---
    parameters:
      - in: path
        name: service_name
        type: string
        required: true
        description: name assigned to the deployed service
      - in: formData
        name: file
        type: file
        required: true
        description: file containing deployment parameters
      - in: query
        name: type
        required: true
        schema:
          type: string
          enum:
            - "DockerSwarm"
        description: type of deployment file
    consumes:
      - application/json
    responses: {}
     """
    data = request.files['file'].read()

    try:
        jdata = manager.deploy(data)
    except Exception as e:
        raise e
    #    return webapp.response_class(response=json.dumps({'error': repr(e)}), status=500, mimetype='application/json')

    return webapp.response_class(response=jdata, status=200, mimetype='application/json')


logger.info('Registering Blueprint v1')
webapp.register_blueprint(v1, url_prefix='/v1')
