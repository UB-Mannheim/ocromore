from colorama import Fore, Style

# todo if coloring doesn't work on an os, just add WARNING or EXCEPTION tags in front of each stuff

class ConditionalPrint(object):

    def __init__(self, condition, exception_condition, warning_condition):
        # init(autoreset=True)  # reset color back to standard after each line print
        self._condition = condition
        self._exception_condition = exception_condition
        self._warning_condition = warning_condition

    def print(self, *args):
        if self._condition is True:
            print(*args)

    def printex(self, *args):
        if self._condition is True or self._exception_condition is True:
            print(Fore.RED, *args, Style.RESET_ALL)

    def printw(self, *args):
        if self._condition is True or self._warning_condition is True:
            print(Fore.YELLOW, *args, Style.RESET_ALL)