class ConditionalPrint(object):

    def __init__(self, condition):
        self._condition = condition

    def print(self,*args):
        if self._condition:
            print(*args)