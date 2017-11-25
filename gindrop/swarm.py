from __future__ import absolute_import, division, print_function
from exceptions import ValueError
import logging
import docker
import json
import yaml


class Manager(object):

    # CONFIGS ######
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = docker.from_env()
        self.logger.info("Registered docker client " + str(self.client))
        self.logger.debug("Docker version: " + str(self.client.version()))

    def get_configs(self):
        return self.client.configs.list()

    def get_config_by_name(self, name):
        cs = self.client.configs.list(filters={'name': name})
        self.logger.info("items found matching [" + name + "]:" + str(len(cs)))
        if len(cs) != 1:
            raise ValueError("Name not found or not unique!")
        return cs[0]

    def get_config_by_id(self, id):
        return self.client.configs.get(id)

    def set_config(self, name, data, labels):
        cid = self.client.configs.create(name=name, data=data)
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
        return self.client.secrets.list()

    def get_secret_by_name(self, name):
        s = self.client.secrets.list(filters={'name': name})
        self.logger.info("items found matching [" + name + "]:" + str(len(s)))
        if len(s) != 1:
            raise ValueError("Name not found or not unique!")
        return s[0]

    def get_secret_by_id(self, id):
        return self.client.secrets.get(id)

    def set_secret(self, name, data, labels):
        sid = self.client.secrets.create(name=name, data=data)
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

        # SECRETS ######

    def deploy(self, data):

        ydata = yaml.load(data)

        for service in ydata['services']:

            constraints = ydata['services'][service]['deploy'].get('placement', {}).get('constraints', [])
            image_name = ydata['services'][service]['image']
            service_labels = ydata['services'][service]['deploy'].get('labels', [])
            container_labels = ydata['services'][service].get('labels', [])
            env = ydata['services'][service].get('environment', [])

            mounts = []
            for volk in ydata['services'][service].get('volumes', []):
                mnt = volk['source']
                mnt += ":" + volk['target']
                mnt += ":rw"
                mounts.append(mnt)

            networks = ydata['services'][service].get('networks', [])

            secrets_list = ydata['services'][service].get('secrets', [])
            configs_list = ydata['services'][service].get('configs', [])

            secrets = []
            for skey in secrets_list:
                sec = self.get_secret_by_name(skey['source'])
                secrets.append(
                    docker.types.SecretReference(
                        sec.id,
                        skey,
                        skey['target']
                    )
                )

            configs = []
            for ckey in configs_list:
                cnf = self.get_secret_by_name(ckey['source'])
                secrets.append(
                    docker.types.ConfigReference(
                        cnf.id,
                        ckey,
                        ckey['target']
                    )
                )

            self.logger.info("name: " + service)
            self.logger.info("image: " + image_name)
            self.logger.info("constraints: " + ",".join(constraints))
            self.logger.info("labels: " + ",".join(service_labels))
            self.logger.info("container_labels: " + ",".join(container_labels))
            self.logger.info("env: " + ",".join(env))
            self.logger.info("mounts: " + ",".join(mounts))
            self.logger.info("networks: " + ",".join(networks))
            self.logger.info("secrets: " + ",".join([x['SecretID'] for x in secrets]))
            self.logger.info("configs: " + ",".join([x['ConfigID'] for x in configs]))

            try:
                service = self.client.services.create(
                    image_name,
                    command=None,
                  # constraints=constraints,
                  #  container_labels=container_labels,
                    env=env,
                  #  labels=service_labels,
                  # mounts=mounts,
                    name=service,
                  #  networks=networks,
                  #  secrets=secrets,
                  #  configs=configs
                )
            except docker.errors.APIError as e:
                self.logger.error("Unable to create service %s: %s", service, str(e))

            self.logger.info("CREATE:" + str(service))

        return json.dumps(service.attrs)
