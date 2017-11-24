from __future__ import absolute_import, division, print_function
from exceptions import ValueError
import logging
import docker
import json
import yaml
import os

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

            logger.info("name: " + service)
            logger.info("image: " + image_name)
            logger.info("constraints: " + ",".join(constraints))
            logger.info("labels: " + ",".join(service_labels))
            logger.info("container_labels: " + ",".join(container_labels))
            logger.info("env: " + ",".join(env))
            logger.info("mounts: " + ",".join(mounts))
            logger.info("networks: " + ",".join(networks))
            logger.info("secrets: " + ",".join([x['SecretID'] for x in secrets]))
            logger.info("configs: " + ",".join([x['ConfigID'] for x in configs]))

            resp = client.login(
                username="admindocker",
                password="F4c1l1t1!",
                registry="docker.facilitylive.int",
                reauth=True)

            logger.info("LOGIN:" + str(resp))

            service = client.services.create(
                image_name,
                image=image_name,
                constraints=constraints,
                container_labels=container_labels,
                env=env,
                labels=service_labels,
                mounts=mounts,
                name=service,
                networks=networks,
                secrets=secrets,
                configs=configs
            )
            logger.info("CREATE:" + str(service))

        return json.dumps(service.attrs)
