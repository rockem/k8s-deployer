from deployer.util import ImageNameParser
from deployer.util import EnvironmentParser


class TestImageNameParser:

    def test_image_name_without_repository(self):
        assert ImageNameParser('test:1').name() == 'test'


class TestEnvironmentParser:
    def test_env_with_namespace(self):
        env = EnvironmentParser('int:zvika')
        assert env.get_env_name() == 'int'
        assert env.get_env_namespace() == 'zvika'

    def test_env_without_namespace(self):
        env = EnvironmentParser('int')
        assert env.get_env_name() == 'int'
        assert env.get_env_namespace() == 'default'
