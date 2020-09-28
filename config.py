import argparse
import functools
import json
import os
import os.path
import re
import sys
from types import SimpleNamespace

root_argument_parser = argparse.ArgumentParser(description="Catalog a music collection")
root_argument_parser.add_argument('--profile', '-p', metavar='FILE', help='Specifies the view profile to load.')
root_argument_parser.add_argument('--module', '-m', metavar='MODULE', help='Specifies the view module to load. Overrides the module property in the view profile.')

ChildArgumentParser = functools.partial(argparse.ArgumentParser, add_help=False, parents=[root_argument_parser])

root = None

RE_CAPITALS = re.compile('(.*?)(?P<cap>[A-Z])')

def snake(camel_str):
    indices = [(m.start(), m.start('cap')) for m in RE_CAPITALS.finditer(camel_str)]

    if not indices:
        return camel_str
    
    snaked = ''.join(camel_str[start:end] + '_' + camel_str[end].lower() for start, end in indices)
    _, last_capital = indices[-1]
    rest = camel_str[last_capital + 1:]

    return snaked + rest

def snakify_dict(snake_dict):
    new_dict = {}
    for key, value in snake_dict.items():
        new_key = snake(key)
        if isinstance(value, list):
            new_dict[new_key] = list(map(snakify_dict, value))
        elif isinstance(value, dict):
            new_dict[new_key] = snakify_dict(value)
        else:
            new_dict[new_key] = value
    return new_dict

def validate(config):
    # TODO
    pass

class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)
        for key, value in adict.items():
            if isinstance(value, dict):
                self.__dict__[key] = Bunch(value)

def init(argument_parser=root_argument_parser):
    global root
    
    if root:
        return

    args = argument_parser.parse_args()
    config_path = args.profile or 'watch.json'

    with open(config_path, 'r') as f:
        config_dict = json.load(f, object_hook=lambda d: snakify_dict(d))

    module = args.module or config_dict['module']
    
    for key, value in config_dict[module].items():
        config_dict[key] = value
        
    root = Bunch(config_dict)
    return root
