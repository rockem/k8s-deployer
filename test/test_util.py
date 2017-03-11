from deployer.util import ImageNameParser


class TestImageNameParser(object):
    def test_retrieve_name_from_image_with_numbered_version(self):
        assert ImageNameParser('image:1.0').name() == 'image'
