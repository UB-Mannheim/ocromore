import importlib
import configargparse


class ConfigurationHandler(object):

    def __init__(self, first_init = False, fill_unkown_args = False, coded_configuration_path=None):

        self._initialized = False
        self._options = None

        if first_init is True:
            self._initialized = True
            parser = configargparse.get_argument_parser(default_config_files=[coded_configuration_path])
            options = self.add_all_args(parser, fill_unkown_args)

        else:
            p = configargparse.get_argument_parser()
            options, junk = p.parse_known_args()

        self._options = options

    def add_all_args(self, parser, fill_unkown_args):

        # parse.add for specific type and name description
        parser.add('-ne', '--number_example', type=int) #testing argument



        if fill_unkown_args is True:
            options, unknown_args = parser.parse_known_args()

            key = ""
            for option_index, option in enumerate(unknown_args):
                if "--" in option[0:2]:
                    key = option

                else:
                    value = option
                    if value == "True" or value == "False":
                        parser.add(key, type=bool)
                    elif value.isdigit():
                        parser.add(key, type=int)
                    else:
                        parser.add(key)

        options, unknown_args = parser.parse_known_args()
        return options



    def get_config(self):
        return self._options