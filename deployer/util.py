import re

class ImageNameParser(object):

    SERVICE_NAME_PATTERN = r'^(.*/)?(.+):'

    def __init__(self, image_name):
        self.image_name = image_name

    def name(self):
        return re.search(self.SERVICE_NAME_PATTERN, self.image_name).group(2)