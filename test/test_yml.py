import os

import yaml

from deployer.log import DeployerLogger
from deployer.yml import YmlCreator, NodeNotFoundError, ByPath, SwaggerFileCreator
from nose.tools.nontrivial import raises

from deployer.yml import YmlReader

CONFIGURATION = {"ENV": "test", "KUKU": "12345"}

logger = DeployerLogger('yml').getLogger()


class TestYmlCreator(object):
    def test_created_output_replaced_by_config(self):
        base_yml = {"deploy": "{ENV}"}
        created_yml = YmlCreator(self.__to_yml(base_yml)).config(CONFIGURATION).create()
        assert yaml.load(created_yml)['deploy'] == CONFIGURATION['ENV']

    def __to_yml(self, base_yml):
        return yaml.dump(base_yml, default_flow_style=False)

    def test_created_output_appended_replaced_by_config(self):
        base_yml = {"deploys": []}
        created = YmlCreator(self.__to_yml(base_yml)) \
            .append(self.__to_yml({"name": "{KUKU}"}), 'deploys') \
            .config(CONFIGURATION) \
            .create()
        assert yaml.load(created)['deploys'][0]['name'] == CONFIGURATION['KUKU']

    @raises(NodeNotFoundError)
    def test_fail_append_on_non_exist_node(self):
        YmlCreator('').append(self.__to_yml({}), 'unknownNode').create()

    def test_add_multiple_entries_of_the_same_type(self):
        base_yml = {"kukus": []}
        created = YmlCreator(self.__to_yml(base_yml)) \
            .append_many(self.__to_yml({'name': '{name}'}),
                         ByPath('kukus'),
                         [{'name': 'popov'}, {'name': 'rozman'}]).create()

        kukus = yaml.load(created)['kukus']
        assert kukus[0]['name'] == 'popov'
        assert kukus[1]['name'] == 'rozman'

class SwaggerFileReaderDump(object):
    def read(self):
        return "aaa:111"

class TestSwaggerFileCreator(object):
    def test_create_yml_with_content(self):
        file_creator = SwaggerFileCreator("")
        file_creator.sw_file_reader = SwaggerFileReaderDump()
        assert yaml.load( file_creator.create()) == SwaggerFileReaderDump().read()

class TestYmlReader(object):
    def test_read_content_from_raw_string(self):
        yml_reader = YmlReader("expose: false\nlogging: none")
        dictionary = yml_reader.read()
        assert dictionary['expose'] is False
        assert dictionary['logging'] == 'none'

    def test_read_content_from_empty_string(self):
        assert YmlReader("").read() == {}
