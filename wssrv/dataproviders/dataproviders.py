from wssrv.dataproviders.memory import Memory


class Dataproviders:
    def __init__(self, type_, options_):
        self.type = type_
        self.options = options_

    def make(self):
        if self.type == 'memory':
            return Memory.make(self.options)
        else:
            return None
