import yaml
from nose.tools.nontrivial import raises

from deployer.yml_creator import YmlCreator, YmlLocationError

CONFIGURATION = {"ENV": "test", "KUKU": "12345"}
APPEND_TEMPLATE = {"name": "{KUKU}"}


class TestYmlCreator(object):
    def __init__(self):
        pass

    def test_created_output_replaced_by_config(self):
        base_yml = {"deploy": "{ENV}"}
        created_yml = YmlCreator(self.__to_yml(base_yml)).config(CONFIGURATION).create()
        assert yaml.load(created_yml)['deploy'] == CONFIGURATION['ENV']

    def __to_yml(self, base_yml):
        return yaml.dump(base_yml, default_flow_style=False)

    def test_created_output_appended_replaced_by_config(self):
        base_yml = {"deploys": []}
        created = YmlCreator(self.__to_yml(base_yml)) \
            .append_node(self.__to_yml(APPEND_TEMPLATE), 'deploys') \
            .config(CONFIGURATION) \
            .create()
        assert yaml.load(created)['deploys'][0]['name'] == CONFIGURATION['KUKU']

    @raises(YmlLocationError)
    def test_fail_append_on_non_exist_node(self):
        YmlCreator('').append_node(self.__to_yml(APPEND_TEMPLATE), 'unknownNode').create()
