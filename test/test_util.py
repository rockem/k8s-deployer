from deployer.util import ImageNameParser

class TestImageNameParser:

    def test_image_name_without_repository(self):
        assert ImageNameParser('test:1').name() == 'test'
