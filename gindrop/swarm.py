from __future__ import absolute_import, division, print_function
from exceptions import ValueError
import logging
import docker

client = docker.from_env()
logger = logging.getLogger(__name__)


class Manager(object):

    # CONFIGS ######

    def get_configs(self):
        return client.configs.list()

    def get_config_by_name(self, name):
        cs = client.configs.list(filters={'name': name})
        logger.info("items found matching [" + name + "]:" + str(len(cs)))
        if len(cs) != 1:
            raise ValueError("Name not found or not unique!")
        return cs[0]

    def get_config_by_id(self, id):
        return client.configs.get(id)

    def set_config(self, name, data, labels):
        cid = client.configs.create(name=name, data=data)
        new_c = self.get_config_by_id(cid.id)
        return new_c

    def rem_config(self, name):
        ret = True
        try:
            c = self.get_config_by_name(name)
            c.remove()
        except ValueError, docker.errors.APIError:
            ret = False
        return ret


        # SECRETS ######

    def get_secrets(self):
        return client.secrets.list()

    def get_secret_by_name(self, name):
        s = client.secrets.list(filters={'name': name})
        logger.info("items found matching [" + name + "]:" + str(len(s)))
        if len(s) != 1:
            raise ValueError("Name not found or not unique!")
        return s[0]

    def get_secret_by_id(self, id):
        return client.secrets.get(id)

    def set_secret(self, name, data, labels):
        sid = client.secrets.create(name=name, data=data)
        new_s = self.get_secret_by_id(sid.id)
        return new_s

    def rem_secret(self, name):
        ret = True
        try:
            s = self.get_secret_by_name(name)
            s.remove()
        except ValueError, docker.errors.APIError:
            ret = False
        return ret
