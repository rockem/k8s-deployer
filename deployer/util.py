import re

class ImageNameParser(object):
    def __init__(self, image_name):
        self.image_name = image_name

    def name(self):
        name = self.__match_pattern(r'/(.+):')
        if(name is None):
            name = self.__match_pattern(r'(.+):') #test mode
        return name.group(1)

    def __match_pattern(self, pattern):
        return re.search(pattern, self.image_name)