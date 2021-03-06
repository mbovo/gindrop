from __future__ import absolute_import, division, print_function
from exceptions import ValueError
import logging
import docker

client = docker.from_env()
logger = logging.getLogger(__name__)


class Manager(object):

    def get_configs(self):
        return client.configs.list()

    def get_config_by_name(self, config_name):
        cs = client.configs.list(filters={'name': config_name})
        logger.info("items found matching [" + config_name + "]:" + str(len(cs)))
        if len(cs) != 1:
            raise ValueError("Name is not unique!")
        return cs[0]

    def get_config_by_id(self, config_id):
        return client.configs.get(config_id)

    def set_config(self, name, data, labels):
        cid = client.configs.create(name, data, labels)
        return self.get_config_by_id(cid)
