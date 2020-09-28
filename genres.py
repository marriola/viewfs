import re

# Expand abbreviated genres and descriptors that cover multiple genres implicitly
# e.g. Brutal/Technical Death Metal => Brutal Death Metal, Technical Death Metal, Death Metal, Metal

substitutions = {
    # 'Dark Ambient': ['Dark Ambient', 'Ambient'],
    # 'Black Funeral Doom': ['Black Metal', 'Funeral Doom Metal', 'Doom Metal', 'Metal'],
    # 'Brutal': ['Death Metal', 'Brutal Death Metal'],
    # 'Crossover': ['Crossover Thrash', 'Punk Rock'],
    # 'D-Beat': ['D-Beat', 'Punk Rock'],
    # 'Dark Psytrance': ['Dark Psytrance', 'Psychedelic Trance', 'Trance'],
    # 'Deathcore': ['Deathcore', 'Metalcore', 'Metal', 'Punk Rock'],
    # 'Deathrock': ['Deathrock', 'Punk Rock'],
    # 'Fusion': ['Jazz Fusion'],
    # 'G-Funk': ['G-Funk', 'Hip Hop'],
    # 'Metalcore': ['Metal', 'Punk Rock', 'Metalcore'],
    # 'New York Hardcore': ['New York Hardcore', 'Hardcore Punk', 'Punk Rock'],
    # 'Psytrance': ['Psychedelic Trance', 'Trance'],
    # 'Punk': ['Punk Rock'],
    # 'Technical Death Metal': ['Death Metal', 'Technical Death Metal'],
    # 'Technical Thrash Metal': ['Thrash Metal', 'Technical Thrash Metal']
}

# Group descriptors that may be truncated when they fall under a larger genre
# e.g. Black/Death Metal => Black Metal, Death Metal, Metal

# Genre has a partial form which may or may not occur as part of the name of a genre belonging to a different parent, so it may not be expanded to its parent genre unconditionally.
# e.g., Jazz -> Jazz, despite Rock having Jazz as an abbreviation for Jazz Rock.
G_PARTIAL = 1

# Genre name is unique among all genre names (such as when the genre name has no partial form), and can be expanded to its parent genre as well.
# e.g. Coldwave -> Coldwave, Post-Punk
G_STANDALONE = 2

# (abbreviation, full name, partial or standalone)

subgenres = {
    'Ambient': {
        'Dark': ('Dark Ambient', G_PARTIAL)
    },

    'Hip Hop': {
        'G-Funk': ('G-Funk', G_STANDALONE)
    },
    
    'Metal': {
        'Avant-Garde': ('Avant-Garde Metal', G_PARTIAL),
        'Black': ('Black Metal', G_PARTIAL),
        'Black Funeral': ('Black Funeral Doom', G_PARTIAL),
        'Brutal Death': ('Brutal Death Metal', G_PARTIAL),
        'Crossover Thrash': ('Crossover Thrash', G_STANDALONE),
        'Death': ('Death Metal', G_PARTIAL),
        'Deathcore': ('Deathcore', G_STANDALONE),
        'Doom': ('Doom Metal', G_PARTIAL),
        'Drone': ('Drone Metal', G_PARTIAL),
        'Funeral Doom': ('Funeral Doom Metal', G_PARTIAL),
        'Gothic': ('Gothic Metal', G_PARTIAL),
        'Groove': ('Groove Metal', G_PARTIAL),
        'Heavy': ('Heavy Metal', G_PARTIAL),
        'Industrial': ('Industrial Metal', G_PARTIAL),
        'Melodic Death': ('Melodic Death Metal', G_PARTIAL),
        'Metalcore': ('Metalcore', G_STANDALONE),
        'Post-Thrash': ('Post-Thrash Metal', G_PARTIAL),
        'Power': ('Power Metal', G_PARTIAL),
        'Progressive': ('Progressive Metal', G_PARTIAL),
        'Sludge': ('Sludge Metal', G_PARTIAL),
        'Speed': ('Speed Metal', G_PARTIAL),
        'Stoner': ('Stoner Metal', G_PARTIAL),
        'Symphonic': ('Symphonic Metal', G_PARTIAL),
        'Technical Death': ('Technical Death Metal', G_PARTIAL),
        'Technical Thrash': ('Technical Thrash Metal', G_PARTIAL),
        'Thrash': ('Thrash Metal', G_PARTIAL)
    },

    'Post-Punk': {
        'Coldwave': ('Coldwave', G_STANDALONE),
        'Darkwave': ('Darkwave', G_STANDALONE),
        'Ethereal Wave': ('Ethereal Wave', G_STANDALONE),
        'Gothic Rock': ('Gothic Rock', G_STANDALONE),
        'Neue Deutsche Welle': ('Neue Deutsche Welle', G_STANDALONE),
        'New Wave': ('New Wave', G_STANDALONE),
        'No Wave': ('No Wave', G_STANDALONE)
    },

    'Punk': {
        'Anarcho': ('Anarcho Punk', G_PARTIAL),
        'Crust': ('Crust Punk', G_PARTIAL),
        'Deathrock': ('Deathrock', G_STANDALONE),
        'Hardcore': ('Hardcore Punk', G_PARTIAL),
        'New York Hardcore': ('New York Hardcore', G_STANDALONE),
        'Noise Rock': ('Noise Rock', G_STANDALONE)
    },

    'Rock': {
        'Alternative': ('Alternative Rock', G_PARTIAL),
        'Art': ('Art Rock', G_PARTIAL),
        'Blues': ('Blues Rock', G_PARTIAL),
        'Christian': ('Christian Rock', G_PARTIAL),
        'Experimental': ('Experimental Rock', G_PARTIAL),
        'Folk': ('Folk Rock', G_PARTIAL),
        'Garage': ('Garage Rock', G_PARTIAL),
        'Hard': ('Hard Rock', G_PARTIAL),
        'Indie': ('Indie Rock', G_PARTIAL),
        'Jazz': ('Jazz Rock', G_PARTIAL),
        'Fusion': ('Jazz Fusion', G_STANDALONE),
        'Neue Deutsche Härte': ('Neue Deutsche Härte', G_STANDALONE),
        'Post-Rock': ('Post-Rock', G_STANDALONE),
        'Progressive': ('Progressive Rock', G_PARTIAL),
        'Psychedelic': ('Psychedelic Rock', G_PARTIAL)
    },

    'Trance': {
        'Goa': ('Goa Trance', G_PARTIAL),
        'Psytrance': ('Psychedelic Trance', G_STANDALONE)
    }
}

def get_abbreviations(genres):
    def inner(genres, out):
        for key, value in genres.items():
            if isinstance(value, dict):
                inner(value, out)
            else:
                out.append(key)

    out = []
    inner(genres, out)
    return out

# def annotate_abbreviations(genres):
#     abbreviations = get_abbreviations(genres)
    
#     def inner(sublist):
#         out = dict()

#         for key, value in genres.items():
#             if isinstance(value, dict):
#                 out[key] = annotate_abbreviations(value)
#             else:
#                 count = len([x for x in ])
#                 out[key] = (value, 

#         return out

#     return inner(genres)

all_subgenres = [[full_name
                 for _, (full_name, _) in subs.items()]
                 for subs in subgenres.values()]

all_genres = sorted(list(subgenres.keys()) + sum(all_subgenres, []))

class Node:
    def __init__(self, name, alias):
        self.name = name
        self.alias = alias
        self.children = []

    def __repr__(self):
        return '%s%s%s' % (
            self.name,
            ' [%s]' % self.alias if self.alias else '',
            ' (%d children)' % len(self.children) if self.children else ''
        )

LEAF = (None, None, None, None)

def parse_genre_tree(lines, suffix='', level=0):
    first_level, first_name, first_alias = lines[0]
    next_suffix = ' ' + (first_alias or first_name)
    first_alias = first_alias or first_name.replace(suffix, '')
    
    if first_level != level:
        return lines, None

    # if not first_alias:
    #     first_alias = first_name.replace(prefix, '')
    # else:
    #     next_suffix = ' ' + first_alias
        
    children = [LEAF]
    tree = (level, first_name, first_alias, children)
    lines = lines[1:]
    
    while lines:
        lines, subtree = parse_genre_tree(lines, next_suffix, level + 1)
        if subtree:
            children.insert(0, subtree)
        else:
            break

    return lines, tree

RE_GENRE = re.compile(r'^(?P<level>-*)(?P<name>[^\[]+)(\[(?P<alias>[^\]]+)\])?')

def read_genre_tree():
    lines = []
    
    with open('genres.tree', 'r') as f:
        for line in f:
            match = RE_GENRE.match(line)
            level = len(match.group('level'))
            name = match.group('name').strip()
            alias = match.group('alias') if match.group('alias') else None
            lines.append((level, name, alias))

    tree = []

    while lines:
        lines, subtree = parse_genre_tree(lines)
        tree.append(subtree)
        
    return tree
    
tree = read_genre_tree()

def mark_match(trail):
    for i in range(0, len(trail)):
        _, name = trail[i]
        trail[i] = (True, name)

def expand_genre(segment, head_genre):
    '''Expands a subgenre to a list of higher level genres, including the subgenre itself.
    e.g. Death Metal > Metal, Death Metal'''
    
    stack = tree
    out = []
    # parent_stack = [None] * len(tree)
    genre_trail = [[] for _ in range(0, len(tree))]

    while stack:
        level, name, alias, children = stack[0]
        # parent = parent_stack[0]
        # parent_stack = parent_stack[1:]

        if stack[0] == LEAF:
            if not any(map(lambda x: x[0], genre_trail[0])):
                genre_trail = genre_trail[1:]
                
            stack = stack[1:]
            continue

        genre_trail[0].append((False, name))

        if name == head_genre or alias == segment:
            mark_match(genre_trail[0])

        # if name == head_genre:
            # out += list(set(x for x in [name] + parent_stack if x))

        #if alias == segment:
            # out += [name]

        # if children:
        #     parent_stack = ([name] * len(children)) + parent_stack

        if children:
            genre_trail = [list(genre_trail[0]) for _ in range(1, len(children))] + genre_trail

        stack = children + stack[1:]

    # out = [x for x in genre_trail if x]
    # out = [x for sublist in genre_trail for x in sublist]
    out = list(map(
        lambda x: x[1],
        filter(
            lambda x: x[0],
            genre_trail[0])))
        
    return out or [segment]

def expand_genre_2(genre, head_genre):
    stack = list(map(lambda node: ([], node), tree))
    out = []

    while stack:
        top = stasck[0]
        level, name, alias, children = top
        stack = stack[1:]

        

#print(expand_genre('Doom', 'Heavy Metal'))
