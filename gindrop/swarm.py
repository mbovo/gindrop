from __future__ import absolute_import, division, print_function
import logging
import docker
import json
import yaml
from docker import errors as docker_errors


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
        except (ValueError, docker_errors.APIError):
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

    def get_network(self, name=None, id=None):
        n = []
        if name:
            n = self.client.networks.list(filters={'name': name})
            self.logger.info("Found {} networks matching name={}".format(len(n), name))
        if id:
            n = self.client.networks.list(filters={'id': id})
            self.logger.info("Found {} networks matching name={}".format(len(n), name))
        if len(n) != 1:
            raise ValueError("Name not found or not unique!")
        return n[0]

    def get_networks(self):
        nl = self.client.networks.list()
        l = {}
        for net in nl:
            l[net.short_id] = net.attrs
        return l

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
        except (ValueError, docker_errors.APIError):
            ret = False
        return ret

        # SECRETS ######

    def rem_service(self, name):
        ret = True
        try:
            s = self.client.services.get(name)
            s.remove()
        except (ValueError, docker_errors.APIError):
            ret = False
        return ret

    def add_service(self, service_name, ydata):

        constraints = ydata['deploy'].get('placement', {}).get('constraints', [])
        image_name = ydata['image']
        service_labels = ydata['deploy'].get('labels', None)
        container_labels = ydata.get('labels', None)
        env = ydata.get('environment', None)

        mounts = []
        for volk in ydata.get('volumes', []):
            mnt = volk['source']
            mnt += ":" + volk['target']
            mnt += ":rw"
            mounts.append(mnt)

        networks = ydata.get('networks', None)

        secrets_list = ydata.get('secrets', [])
        configs_list = ydata.get('configs', [])

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

        logstr = "Creating Service with data:\n" \
                 "\tname: {}\n" \
                 "\timage: {}\n" \
                 "\tconstraints: {}\n" \
                 "\tlabels: {}\n" \
                 "\tcontainer_labels: {}\n" \
                 "\tenv: {}\n" \
                 "\tmounts: {}\n" \
                 "\tnetworks: {}\n" \
                 "\tsecrets: {}\n" \
                 "\tconfigs: {}" \
                 "".format(service_name, image_name, constraints, service_labels,
                           container_labels, env, mounts, networks,
                           ",".join([x['SecretID'] for x in secrets]),
                           ",".join([x['ConfigID'] for x in configs]))
        self.logger.info(logstr)
        try:
            service = self.client.services.create(
                image_name,
                command=None,
                constraints=constraints,
                container_labels=container_labels,
                env=env,
                labels=service_labels,
                mounts=mounts,
                name=service_name,
                networks=networks,
                secrets=secrets,
                configs=configs
            )
        except docker_errors.APIError as e:
            self.logger.error(e)
            raise e
        except Exception as e:
            raise e

        self.logger.info("CREATED:" + str(service))
        return service

    def rem_network(self, name):
        try:
            net = self.get_network(name)
            self.logger.info("Deleting network {}".format(net.short_id))
            net.remove()
        except docker_errors.APIError as e:
            self.logger.error(e)
            return False
        return True

    def add_network(self, net_name, ydata):
        if ('external' in ydata) and (ydata['external'] is True):
            return None
        try:
            net = self.client.networks.create(net_name, driver='overlay')
        except docker_errors.APIError as e:
            self.logger.error(e)
            raise e
        except Exception as e:
            raise e

        return net

    def deploy(self, data):
        ydata = yaml.load(data)

        for network in ydata['networks']:
            net_obj = self.add_network(network, ydata['networks'][network])

        for service in ydata['services']:
            srv_obj = self.add_service(service, ydata['services'][service])

        return json.dumps(srv_obj.attrs)

    def list_services(self):
        ret = {}
        for s in self.client.services.list():
            ret[s.id] = {
                # 'attrs': s.attrs,
                'name': s.attrs['Spec']['Name'],
                'replicas': s.attrs['Spec']['Mode']['Replicated']['Replicas'],
                'image': s.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
            }

        return ret

    def get_service(self, sid=None, name=None, label=None):
        ret = {}
        services = None
        if sid:
            self.logger.info('Filtering for sid {}'.format(sid))
            services = self.client.services.list(filters={'id': sid})
        elif name:
            self.logger.info('Filtering for name {}'.format(name))
            services = self.client.services.list(filters={'name': name})
        elif label:
            self.logger.info('Filtering for label {}'.format(label))
            services = self.client.services.list(filters={'label': label})
        else:
            self.logger.info('No filtering')
            services = self.client.services.list()

        if len(services) == 0:
            self.logger.warning("No match found")
            raise Exception('No match found')

        self.logger.info("Found {} services, getting info".format(str(len(services))))
        for s in services:
            s_id = s.id
            sname = s.attrs['Spec']['Name']
            containers_ok = []
            containers_fail = []
            current = 0
            failed = 0

            if 'Replicated' not in s.attrs['Spec']['Mode']:
                self.logger.warning('Key not found "Replicated" is a global service')
                replicas = 'global'
            else:
                replicas = s.attrs['Spec']['Mode']['Replicated']['Replicas']

            self.logger.info("Service ID [{}] [{}] with {} tasks".format(s_id, sname, replicas))

            for t in s.tasks():
                if 'ContainerID' not in t['Status']['ContainerStatus']:
                    t_id = ""
                else:
                    t_id = t['Status']['ContainerStatus']['ContainerID']

                try:
                    node_host = self.client.nodes.get(t['NodeID']).attrs['Description']['Hostname']
                except Exception as e:
                    self.logger.error("Unable to load Node info: {}".format(repr(e)))
                    node_host = 'unknown'

                if t['Status']['State'] == 'failed':
                    containers_fail.append({'id': t_id,
                                            'state': t['Status']['State'],
                                            'desidered': t['DesiredState'],
                                            'node': node_host
                                            })
                    failed += 1
                    self.logger.debug("Failed task {} on node {}".format(t_id, node_host))
                else:
                    containers_ok.append({'id': t_id,
                                          'state': t['Status']['State'],
                                          'desidered': t['DesiredState'],
                                          'node': node_host
                                          })
                    self.logger.debug("{} task {} on node {}".format(t['Status']['State'], t_id, node_host))

                if t['Status']['State'] == 'running':
                    current += 1
            ret[s_id] = {
                'name': sname,
                'replicas': replicas,
                'running': current,
                'failed': failed,
                'running_list': containers_ok,
                'failed_list': containers_fail
            }

        return ret
