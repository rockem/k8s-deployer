from deployer.file import YamlReader
from deployer.recipe import EXPOSE_LABEL, LOGGING_LABEL


class TestYamlReader():

    def test_return_empty_result_on_empty_string(self):
        yaml_reader = YamlReader("")
        assert len(yaml_reader.read()) == 0

    def test_read_content_from_raw_string(self):
        yaml_reader = YamlReader("expose:false;logging:none")
        dictionary = yaml_reader.read()
        assert dictionary[EXPOSE_LABEL] is False
        assert dictionary[LOGGING_LABEL] == 'none'

    def test_empty_content_when_wrong_format(self):
        yaml_reader = YamlReader("this?string?is?in?wrong?format")
        dictionary = yaml_reader.read()
        assert len(dictionary) == 0

