from deployer.util import ImageNameParser, EnvironmentParser


class TestImageNameParser(object):
    def test_retrieve_name_from_image_with_numbered_version(self):
        assert ImageNameParser('image:1.0').name() == 'image'


class EnvironmentVariablesFetcherStub(object):
    def fetch(self, key):
        return 'int'


class TestEnvironmentParser(object):
    def test_default_namespace_return_when_None_given(self):
        assert self.__environment_parser_for(None).env() == 'int:default'

    def __environment_parser_for(self, target):
        parser = EnvironmentParser(target)
        parser.env_variable_fetcher = EnvironmentVariablesFetcherStub()
        return parser

    def test_given_namespace_return_same_namespace(self):
        assert self.__environment_parser_for('env').namespace() == 'env'

    def test_retrieve_target_env(self):
        assert self.__environment_parser_for('env').name() == 'int'
