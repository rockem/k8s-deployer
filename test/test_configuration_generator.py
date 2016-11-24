import os

import yaml
from nose.tools import raises

from deployer.configuration_generator import ConfigurationGenerator, TemplateCorruptedError

CONFIGURATION = './resources/configuration.yml'
TARGET = './resources/generated_deployment.yml'
SOURCE = './resources/test_deployment.yml'

class TestConfigurationGenerator(object):

    cg = None

    def setupTest(self, configurationDic, templateDic):
        self.generate_file(CONFIGURATION, configurationDic)
        self.generate_file(SOURCE, templateDic)
        self.cg = ConfigurationGenerator(self.fetch_configuration())

    def fetch_configuration(self):
        try:
            return dict(map(str, x.split(':')) for x in open('./resources/configuration.yml').readlines())
        except Exception:
            return dict()

    def generate_file(self, path, data):
        with open(path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def test_generate_configuration_with_one_param(self):
        self.setupTest(dict(first ="firstProp"), dict(name = "{first}"))
        self.cg.generate(TARGET).by_template(SOURCE)
        assert self.assert_generated_configuration(open(TARGET).readlines(), dict(firstProp = "{first}"))

    def test_generate_configuration_with_more_than_one_param(self):
        self.setupTest(dict(first ="firstProp", second = "secondProp"), dict(name = "{first}", lable="{second}"))
        self.cg.generate(TARGET).by_template(SOURCE)
        assert self.assert_generated_configuration(open(TARGET).readlines(), dict(firstProp ="{first}",  secondProp = "{second}"))

    @raises(TemplateCorruptedError)
    def test_throw_exception_given_prop_not_match_in_template(self):
        self.setupTest(dict(first ="first-prop", second = "second-prop"), dict(name = "{first}", lable = "{lable}"))
        self.cg.generate(TARGET).by_template(SOURCE)

    def assert_generated_configuration(self, content, toAssert):
        for k,v in toAssert.iteritems():
            if k not in str(content) and v in str(content):
                return False
            return True

    def tearDown(self):
        os.remove(TARGET)
        os.remove(SOURCE)
        os.remove(CONFIGURATION)