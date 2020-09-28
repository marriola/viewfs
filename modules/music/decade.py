import os
import os.path
from genres import subgenres
from view import view, sanitize

def get_decade(year):
    if not year or year == '(blank)':
        return '(none)'

    decade = year / 10
    return '%d0s' % decade

@view('By decade')
def compute_tree(catalog): #, add_link):
    links = set()

    for file_path, genres, artist, year, _, _, _, _ in catalog:
        path, file = os.path.split(file_path)
        decade = get_decade(year)
        link_path = os.path.join(
            decade,
            sanitize(artist),
            file if not year else '[%d] %s' % (year, file))

        links.add((link_path, file_path))
        # add_link(link_path, file_path)

    return links
