import configargparse


class SomeClassConfigTest(object):

    def __init__(self):
        print("a s d")
        p = configargparse.get_argument_parser()
        options, junk = p.parse_known_args()

        print("options.SOMETHINGNEW in Some other class:", options.SOMETHINGNEW)

        p.add_argument("--SomethingFromSomeOtherClass", help="Config-file-settable option for utils")