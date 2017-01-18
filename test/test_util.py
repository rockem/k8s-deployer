from deployer.util import EnvironmentParser
from deployer.util import ImageNameParser


class TestImageNameParser:
    def test_image_name_without_repository(self):
        assert ImageNameParser('test:1').name() == 'test'


class TestEnvironmentParser:
    def test_extract_env_name(self):
        assert EnvironmentParser('int:zvika').env_name() == 'int'

    def test_extract_namespace(self):
        assert EnvironmentParser('int:zvika').namespace() == 'zvika'

    def test_extract_default_when_no_namespace(self):
        env = EnvironmentParser('int')
        assert env.env_name() == 'int'
        assert env.namespace() == 'default'
