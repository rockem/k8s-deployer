import os
import yaml
from nose.tools import raises
from deployer.configuration_generator import ConfigGenerator, TemplateCorruptedError

CONFIGURATION = './configuration.yml'
TARGET = './generated_deployment.yml'
SOURCE = './test_deployment.yml'


class TestConfigurationGenerator(object):
    cg = None

    def setupTest(self, configurationDic, templateDic):
        self.generate_file(CONFIGURATION, configurationDic)
        self.generate_file(SOURCE, templateDic)
        self.cg = ConfigGenerator(self.fetch_configuration())

    def fetch_configuration(self):
        try:
            return dict(map(str, x.split(':')) for x in open('./configuration.yml').readlines())
        except Exception:
            return dict()

    def generate_file(self, path, data):
        with open(path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def test_generate_configuration_with_one_param(self):
        self.setupTest(dict(first="firstProp"), dict(name="{first}"))
        self.cg.generate(TARGET).by_template(SOURCE)
        assert self.assert_generated_configuration(open(TARGET).readlines(), dict(firstProp="{first}"))

    def test_generate_configuration_with_more_than_one_param(self):
        self.setupTest(dict(first="firstProp", second="secondProp"), dict(name="{first}", label="{second}"))
        self.cg.generate(TARGET).by_template(SOURCE)
        assert self.assert_generated_configuration(open(TARGET).readlines(), dict(firstProp ="{first}",
                                                                                  secondProp="{second}"))

    def test_generate_configuration_with_params_not_in_order(self):
        self.setupTest(dict(first="first-prop", second="second-prop"), dict(name="{second}", label="{first}"))
        self.cg.generate(TARGET).by_template(SOURCE)

    @raises(TemplateCorruptedError)
    def test_throw_exception_given_prop_not_match_in_template(self):
        self.setupTest(dict(first="first-prop", second="second-prop"), dict(name="{first}", label="{label}"))
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