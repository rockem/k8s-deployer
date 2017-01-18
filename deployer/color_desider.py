

class ColorDesider(object):

    COLORS = {
        'blue':'green',
        'green' : 'blue'
    }

    def invert_color(self, color):
        return self.COLORS[color]

    def defaut_color(self):
        return 'blue'
