from __future__ import absolute_import, division, print_function
import logging
import json
from gindrop import core, swarm
from flask import Flask
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
    return json.dumps({'msg': 'hello world'})


@app.route('/configs')
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


@app.route('/configs/<path:config_name>')
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


class TodoSimple(Resource):

    def get(self, id):
        """
        This examples uses FlaskRESTful Resource
        It works also with swag_from, schemas and spec_dict
        ---
        parameters:
          - in: path
            name: id
            type: string
            required: true
        responses: {}
         """
        return {id: todos[id]}

    def put(self, id):
        """
        This examples uses FlaskRESTful Resource
        It works also with swag_from, schemas and spec_dict
        ---
        parameters:
          - in: path
            name: id
            type: string
            required: true
          - in: formData
            name: data
            type: string
            required: true
        consumes:
          - application/json
        responses: {}
         """
        logger.info(str(request))
        todos[id] = request.form['data']
        return {id: todos[id]}

api.add_resource(TodoSimple, '/<string:id>')
