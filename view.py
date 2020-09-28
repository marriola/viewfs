import functools
import os.path
import re

import config

modules = []
view_mappers = []

def view(name):
    '''
    Adds the name of the view to the mapper function. It will be used to form the
    base path of all links in this view.
    '''
    
    def decorate(func):
        func.view_name = name
        return func

    return decorate

def module(name):
    '''
    Registers the module's view mappers if it is selected in the configuration (watch.json, module property).
    '''
    
    def decorate(func):
        global view_mappers
        if name == config.root.module:
            view_mappers += func()
        return func

    return decorate

RE_TRAILING_PERIOD = re.compile('\\.+$')
RE_INVALID_CHARS = re.compile('[/\\<>:"|?*]')

def sanitize(link_path):
    '''
    Removes invalid characters and trailing periods, for Samba.
    '''

    removed_trailing_periods = RE_TRAILING_PERIOD.sub('', link_path)
    removed_invalid_chars = RE_INVALID_CHARS.sub('_', removed_trailing_periods)
    
    return removed_invalid_chars

import modules.music

def recompute(entries): #, tree_view):
    '''
    Maps a list of catalog entries to view entries.
    '''
    
    views = set()

    for map_view in view_mappers:
        views |= set((os.path.join(map_view.view_name, link_path), file_path)
                     for link_path, file_path
                     in map_view(entries))

        # add_link = functools.partial(tree_view.add, map_view.view_name)
        # map_view(entries, add_link)

    return views
