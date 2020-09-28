import ast
from catalog import read_adapter
from modules.music import genre
from modules.music import decade
from view import module

MODULE_NAME = 'music'

@module(MODULE_NAME)
def get_views():
    return [genre.compute_tree, decade.compute_tree]

def get_first_part(s):
    if not s:
        return s

    parts = s.split('/')
    
    if parts:
        return parts[0]
    else:
        return None

def parse_if_int(s):
    if s and s.isdigit():
        return int(s)
    else:
        return None

@read_adapter(MODULE_NAME)
def adapt_output(entry):
    path, genres, artist, year, album, disc, track, title = entry
    genres = genres if isinstance(genres, list) else ast.literal_eval(genres)
    year = parse_if_int(year)
    disc = parse_if_int(get_first_part(disc))
    track = parse_if_int(get_first_part(track))
    return path, genres, artist, year, album, disc, track, title
