from colorama import Fore, Style

class ConditionalPrint(object):

    def __init__(self, condition, exception_condition):
        # init(autoreset=True)  # reset color back to standard after each line print
        self._condition = condition
        self._exception_condition = exception_condition

    def print(self, *args):
        if self._condition is True:
            print(*args)

    def printex(self, *args):
        if self._condition is True or self._exception_condition is True:
            print(Fore.RED, *args, Style.RESET_ALL)