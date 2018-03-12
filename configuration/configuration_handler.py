import importlib
import configargparse


class ConfigurationHandler(object):

    def __init__(self, first_init = False, fill_unkown_args = False, coded_configuration_paths=None):

        self._initialized = False
        self._options = None

        if first_init is True:
            self._initialized = True
            parser = configargparse.get_argument_parser(default_config_files=coded_configuration_paths)
            options = self.add_all_args(parser, fill_unkown_args)

        else:
            parser = configargparse.get_argument_parser()
            options, junk = parser.parse_known_args()

        self._parser = parser
        self._options = options

    def add_all_args(self, parser, fill_unkown_args):

        # parse.add for specific type and name description
        # parser.add('-ne', '--number_example', type=int) #testing argument



        if fill_unkown_args is True:
            options, unknown_args = parser.parse_known_args()

            key = ""
            prev_key = ""

            list_keys = [] # keys which classify a list item
            for option in unknown_args:
                if "--" in option[0:2]:
                    key = option
                    if key == prev_key:
                        list_keys.append(key)

                prev_key = key

            key = " "
            list_appended_keys = [] # notation that this list with that key already was added
            boolean_keys = []
            for option_index, option in enumerate(unknown_args):
                if "--" in option[0:2]:
                    key = option

                elif key not in list_appended_keys:
                    value = option
                    if value == "True" or value == "False":
                        boolean_keys.append(key)
                        parser.add(key)
                    elif value.isdigit():
                        parser.add(key, type=int)
                    elif key in list_keys:
                        print("list")
                        parser.add(key, nargs='+')
                        list_keys.remove(key)
                        list_appended_keys.append(key) # note key this list a
                    else:
                        parser.add(key)


        options, unknown_args = parser.parse_known_args()

        # solves that boolean is always set to 'True', https://github.com/bw2/ConfigArgParse/issues/35
        ol = vars(options)
        for option in ol:
            value = getattr(options, option)
            value_bool = None
            if not isinstance(value, str):
                continue
            if value.lower() == "false":
                value_bool = False
            if value.lower() == "true":
                value_bool = True
            if value_bool is not None:
                setattr(options,option,value_bool)


        return options



    def get_config(self):
        return self._options