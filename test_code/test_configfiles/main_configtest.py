import configargparse
from test_code.test_configfiles.some_class_configtest import SomeClassConfigTest
#p = configargparse.ArgParser(default_config_files=['configtest.conf'])


p = configargparse.get_argument_parser(default_config_files=['configtest.conf']) # this is nearly the same as constructor, but with default name for singleton usage
#p.add('-c', '--my-config', required=True, is_config_file=True, help='config file path')

#p.add('--genome', required=True, help='path to genome file')  # this option can be set in a config file because it starts with '--'
#p.add('-v', help='verbose', action='store_true')
#p.add('-d', '--dbsnp', help='known variants .vcf', env_var='DBSNP_PATH')  # this option can be set in a config file because it starts with '--'



p.add('--number_example', type=int)


options, unknown_args = p.parse_known_args()

key = ""
for option_index, option in enumerate(unknown_args):
    if "--" in option:
        key = option
        p.add(key)



options, unknown_args = p.parse_known_args()


print("options.SOMETHINGNEW:", options.SOMETHINGNEW)
sct = SomeClassConfigTest()


options, junk = p.parse_known_args()  # call this to refresh args

print("options.SOMECLASSCONFIGTEST" )
