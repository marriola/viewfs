from config import root as config
import lzma
import os
import os.path
import sys
from tagutil import *
import traceback
import unicodecsv as csv

read_adapter_func = lambda x: x

def read_adapter(module_name):
    def decorate(func):
        global read_adapter_func

        if module_name == config.module:
            read_adapter_func = func
            
        return func
    
    return decorate

class Result:
    # Add succeeded.
    Added = 1
    
    # Modify existing file succeeded.
    Modified = 2

    # Failed to read tags; existing entry removed.
    Failed = 3

    # Failed to read tags; ignored.
    Ignored = 4

class Catalog:
    def __init__(self, entries, collection_root):
        self.entries = dict((e[0], e) for e in entries)
        self.collection_root = collection_root

    @staticmethod
    def load(path, collection_root):
        with lzma.open(path, 'rb') as f:
            reader = csv.reader(f, delimiter=' ', quotechar='|')
            entries = [read_adapter_func(x) for x in list(reader)]
            return Catalog(entries, collection_root)

    @staticmethod
    def build(collection_root):               
        def catalog_dir(dir, start=0, indent=0, branch_continues=[]):
            def print_indent(final):
                for i in range(0, indent):
                    print('│ ' if branch_continues[i] else '  ', end='')

                print('└─' if final else '├─', end='')

            branch_continues.append(True)
            print(dir[start:])

            contents = [os.path.join(dir, x) for x in os.listdir(dir)]
            files = sorted(x for x in contents if not os.path.isdir(x))
            subdirs = sorted(x for x in contents if os.path.isdir(x))

            branch_continues[indent] = False
            file_count = 0
            has_no_subdirs = len(subdirs) == 0
                
            for i in range(0, len(files)):
                _, result = catalog.add(files[i])
                
                if result == Result.Added:
                    file_count += 1
                    print_indent(has_no_subdirs)
                    print('<%d files>\r' % file_count, end='')

            if file_count > 0:
                print()

            for i in range(0, len(subdirs)):
                more = i < len(subdirs) - 1
                branch_continues[indent] = more
                print_indent(not more)
                catalog_dir(
                    subdirs[i],
                    len(dir) + 1,
                    indent + 1,
                    branch_continues)

            branch_continues = branch_continues[:-1]

        catalog = Catalog([], collection_root)
        catalog_dir(collection_root)
        return catalog
        
    def save(self, path):
        with lzma.open(path, 'wb') as f:
            writer = csv.writer(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            for entry in sorted(self.entries.values(), key=lambda x: x[0]):
                writer.writerow(entry)

    def add(self, file_path):
        relpath = os.path.relpath(file_path, start=self.collection_root)
        info = self._get_file_info(file_path)
        
        if not info:
            if relpath in self.entries:
                del self.entries[relpath]
                return None, Result.Failed
            else:
                return None, Result.Ignored
        
        is_new = relpath not in self.entries
        self.entries[relpath] = read_adapter_func(info)

        return info, (Result.Added if is_new else Result.Modified)

    def remove(self, file_path):
        relpath = os.path.relpath(file_path, start=self.collection_root)
        if relpath in self.entries:
            del self.entries[relpath]

    def rename(self, from_path, to_path):
        from_path = os.path.relpath(from_path, start=self.collection_root)
        to_path = os.path.relpath(to_path, start=self.collection_root)

        if from_path in self.entries:
            self.remove(from_path)
            self.add(to_path)

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.entries.values())[key]
        else:
            return self.entries[key]

    def _get_file_info(self, filepath):
        f = None

        try:
            f = mutagen.File(filepath)
            if not f:
                # print('File format not recognized')
                return
        except:
            # info = sys.exc_info()
            # traceback.print_exception(*info)
            return

        tags = map_tags(f)
        
        relative_path = os.path.relpath(
            filepath.encode('utf-8', 'surrogateescape').decode('utf-8'),
            start=self.collection_root)
        
        entry = (
            relative_path,
            get_genre_groups(tags['genre']),
            tags['artist'],
            tags['year'] if 'year' in tags else None,
            tags['album'],
            tags['disc'],
            tags['track'],
            tags['title']
        ) 

        return entry
