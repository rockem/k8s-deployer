import os

import yaml

from deployer.k8s import DeployDescriptorFactory


class TestDeployDescriptorFactory:
    def __init__(self):
        pass

    TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'orig')

    def test_add_fluentd_definition(self):
        factory = DeployDescriptorFactory(self.TEMPLATE_PATH, {'logging': 'log4j'})
        with open(factory.deployment(), 'r') as f:
            assert self.is_fluentd_exists_in(yaml.load(f))

    def is_fluentd_exists_in(self, y):
        for c in y['spec']['template']['spec']['containers']:
            if c.has_key('fluentd') and c['fluentd']['image'] == 'fluentd':
                return True
        return False

