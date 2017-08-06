import os

import yaml

from deployer.yml_creator import K8sYmlCreator, K8sYmlLocationError

CONFIGURATION = {"ENV": "test", "MY_ENV": "12345"}
CONFIGURATION_APPEND = {"ENV": "test", "MY_ENV": "12345", "append": "123"}
APPEND_CNTX = {"MY_ENV": "{MY_ENV}"}
SOURCE_DIR= "./orig/"
TARGET_DIR= "./out/"
TARGET= 'config'
APPEND= 'append'

class TestK8sYmlCreator(object):

    def __init__(self):
        if not os.path.exists(SOURCE_DIR):
            os.makedirs(SOURCE_DIR)

    def __setup_test(self, target_cntx,configuration,append_cntx=None,location=None):
        self.k8s_yml_creator = K8sYmlCreator(SOURCE_DIR, TARGET_DIR)
        self.__write_to_file(self.__get_file_path(SOURCE_DIR, TARGET), target_cntx)
        self.k8s_yml_creator.generate(configuration, TARGET)
        if append_cntx != None:
            self.__write_to_file(self.__get_file_path(SOURCE_DIR, APPEND), append_cntx)
            self.k8s_yml_creator.append_node(APPEND, location)

        return yaml.load(open(self.__get_file_path(TARGET_DIR, TARGET)))

    def __get_file_path(self, dir, element):
        return dir + element + ".yml"

    def __write_to_file(self, path, data):
        yaml.dump(data, open(path, 'w+'), default_flow_style=False)

    def test_created_output_replaced_by_config(self):
        target_cntx = {"deploy": "{ENV}"}
        generated=self.__setup_test(target_cntx, CONFIGURATION)
        assert cmp({"deploy":"test"},generated) == 0

    def test_created_output_appended_replaced_by_config(self):
        target_cntx = [{"deploy": "{ENV}"}]
        generated = self.__setup_test(target_cntx, CONFIGURATION_APPEND, APPEND_CNTX)
        assert cmp([{"deploy":"test"},{"MY_ENV":"12345"}],generated) == 0

    def test_appended_output_created_in_defined_location(self):
        target_cntx = {"root": [{"deploy": "{ENV}"}]}
        generated = self.__setup_test(target_cntx, CONFIGURATION_APPEND, APPEND_CNTX, "root")
        assert cmp({"root":[{"deploy":"test"},{"MY_ENV":"12345"}]},generated) == 0

    def test_fail_generating_yaml_on_non_exist_location(self):
        try:
            self.__setup_test({"root":"123"},{"append":"123"},{"dd":""}, "1.2.3")
        except K8sYmlLocationError:
            pass

    def test_will_not_append_to_yml(self):
        generated = self.__setup_test({"deploy":"123"},{"append":"NONE"},{"MY_ENV": "123"})
        assert cmp(generated,{"deploy":"123"}) == 0

    def tearDown(self):
        if os.path.isfile(self.__get_file_path(TARGET_DIR, APPEND)):
            os.remove(self.__get_file_path(TARGET_DIR, APPEND))
        if os.path.isfile(self.__get_file_path(SOURCE_DIR, APPEND)):
            os.remove(self.__get_file_path(SOURCE_DIR, APPEND))
        os.remove(self.__get_file_path(TARGET_DIR, TARGET))
        os.remove(self.__get_file_path(SOURCE_DIR, TARGET))