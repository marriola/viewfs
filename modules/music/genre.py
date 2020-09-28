# TODO: enforce hierarchy in view, rather than blasting genres everywhere. maybe have to change links from list to an actual tree?

import os.path
from genres import subgenres
from view import view, sanitize

def get_genre_combinations(genres):
    out = []

    def inner(genres, path):
        if len(path) > 0:
            out.append(path)

        if len(genres) == 0:
            return

        for g in genres:
            inner(
                [h for h in genres
                 if h != g and
                    h not in subgenres],
                os.path.join(path, sanitize('!' + g)) if path else sanitize(g))

    inner(genres, '')
    return set(out)

def list_dir(catalog, path):
    entries = [x for x in catalog if x[0].startswith(path)]
    subdirs = set(os.path.split(x)[1] for x in entries)

def query(catalog, path):
    def inner(path, entries):
        print(path, len(entries))
    
        if len(path) == 0:
            return entries
    
        genre, rest = path[0], path[1:]
        entries = [x for x in entries if genre in x[1]]
        print(genre, len(entries))
    
        return inner(rest, entries)

    path_parts = list(filter(None, path.split('/')))
    entries = inner(path_parts, catalog.entries.values())

    subdirs = set()

    for _, genres, _, _, _, _, _, _ in entries:
        subdirs |= set(genres)

    subdirs -= set(path_parts)

    return list(subdirs) + [x[0] for x in entries]

@view('By genre')
def compute_tree(catalog): #, add_link):
    """Computes the symbolic links comprising the genre view"""
    links = set()

    for file_path, genres, artist, _, _, _, _, _ in catalog:
        _, file = os.path.split(file_path)
        
        genre_links = ((os.path.join(p, sanitize(artist), file), file_path)
                       for p in get_genre_combinations(genres))
        
        for l in genre_links:
            links.add(l)
            # add_link(link_path, file_path)

    return links
