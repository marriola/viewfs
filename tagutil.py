from genres import substitutions, subgenres, G_STANDALONE
import mutagen
import mutagen.id3
import mutagen.mp3
import mutagen.mp4
import mutagen.flac
import mutagen.oggvorbis
import mutagen.asf

# Map uniform names to tag fields for different formats

def extract_item(key, index, func=None):
    '''
    Extract a single item from a tag containing a tuple or list.
    '''
    return lambda f: (func(f[key][0][index]) if func else f[key][0][index]) if key in f else None

def extract_many(*keys):
    '''
    Extract values from multiple tags.
    '''
    return lambda f: [f[k][0] for k in keys if k in f]

tag_mappings = {
    mutagen.mp3.MP3: {
        'genre': 'TCON',
        'artist': 'TPE1',
        'year': extract_many('TYER', 'TDRC', 'TORY', 'TDOR'),
        'album': 'TALB',
        'disc': 'TPOS',
        'track': 'TRCK',
        'title': 'TIT2',
    },

    mutagen.mp4.MP4: {
        'genre': '\xa9gen',
        'artist': '\xa9ART',
        'year': '\xa9day',
        'album': '\xa9alb',
        'disc': extract_item('disk', 0),
        'track': extract_item('trkn', 0),
        'title': '\xa9nam',
    },

    mutagen.flac.FLAC: {
        'genre': 'genre',
        'artist': 'artist',
        'year': 'date',
        'album': 'album',
        'disc': 'discnumber',
        'track': 'tracknumber',
        'title': 'title',
    },

    mutagen.oggvorbis.OggVorbis: {
        'genre': 'genre',
        'artist': 'artist',
        'year': 'date',
        'album': 'album',
        'disc': 'discnumber',
        'track': 'tracknumber',
        'title': 'title'
    },

    mutagen.asf.ASF: {
        'genre': 'WM/Genre',
        'artist': 'Author',
        'year': 'WM/Year',
        'album': 'WM/AlbumTitle',
        'disc': 'WM/PartOfSet',
        'track': 'WM/TrackNumber',
        'title': 'Title'
    },
}

def get_head_genre(genre):
    head_genre = genre.split(' ')[-1]

    for head in subgenres:
        if genre in subgenres[head] and subgenres[head][genre][1] == G_STANDALONE:
            return head, subgenres[head]
    
    if head_genre in subgenres:
        return head_genre, subgenres[head_genre]

    return None, None

def has_lowercase(s):
    for c in s:
        if c.islower():
            return True

    return False
    
def get_genre_groups(genre_tag):
    groupings = [set()]
    current = groupings[0]
    
    for g in genre_tag.split('/'):
        current.add(g)
        head_genre, subs = get_head_genre(g)
        
        if subs:
            groupings[-1] = set(subs[g][0] if g in subs else g for g in current)
            groupings[-1].add(head_genre)

            groupings.append(set())
            current = groupings[-1]

    return list(set(g if has_lowercase(g) else g.title()
                    for sublist in groupings
                    for g in sublist
                    if g))

def get_genre_counts(files):
    artist_genre_counts = {}

    for path, genres, artist, _, _ in files:
        if artist not in artist_genre_counts:
            artist_genre_counts[artist] = {}
    
            for g in genres:
                if g not in artist_genre_counts[artist]:
                    artist_genre_counts[artist][g] = 1
                else:
                    artist_genre_counts[artist][g] += 1

    return artist_genre_counts

def sanitize_tag(value):
    # ID3 multiple genres are contained in one tag
    if isinstance(value, mutagen.id3.TCON):
        value = '/'.join(value)

    # WMA module uses list of ASFUnicodeAttributes
    if isinstance(value, list):
        value = '/'.join(map(str, value))

    return str(value)

def sanitize_singular_tag(value):
    if value.__getitem__:
        return str(value[0])

    return str(value)

def min_int_or_none(x):
    return 9999 if not x else int(x)

def sanitize_year_tag(value):
    def min_year(years):
        return None if not years else min(years, key=lambda x: int(x or 9999))

    if not isinstance(value, list):
        value = [value]

    for i in range(0, len(value)):
        v = str(value[i]).strip()

        # Split dates with month and/or day included
        for delim in ['-', '/']:
            if delim in v:
                parts = [x.strip() for x in v.split(delim) if ':' not in x]
                v = max(parts, key=len)

        if ',' in v:
            # Split multiple years and take the earliest
            v = min_year([int(x) for x in v.split(',')])

        value[i] = v

    return min_year(value)

transforms = {
    'artist': sanitize_tag,
    'genre': sanitize_tag,
    'album': sanitize_singular_tag,
    'year': sanitize_year_tag,
    'title': sanitize_singular_tag
}

def map_tags(f):
    mapping = tag_mappings[type(f)]
    out = {}

    for target, source in mapping.items():
        value = None

        if callable(source):
            value = source(f)
        elif source in f:
            value = f[source]        
        
        if value == None:
            out[target] = '(blank)'
            continue

        out[target] = transforms[target](value) if target in transforms else str(value)

    return out
