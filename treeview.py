from config import root as config
from errno import ENOENT
from fuse import FuseOSError
import lzma
import os.path
import pickle
import view

class DirectoryTree:
    '''
    Stores a tree representation of the views passed into the constructor. Subdirectories are stored using the
    name as the key, and any files in a subdirectory are in a list under the key '*files'
    '''
    
    def __init__(self, views=None):
        self.tree = {
            '*dirs': [],
            '*files': []
        }
        
        if not views:
            return

        for link_path, _ in views:
            link_path = link_path.replace(config.view.view_root, '')
            link_dir, _ = os.path.split(link_path)
            subtree = self._walk(link_dir, create_missing=True)
        
            parts = link_path.split('/')
            subtree['*files'].append(parts[-1])

    def add(self, link_path):
        path, link = os.path.split(link_path)
        subtree = self._walk(path, create_missing=True)

        if link not in subtree['*files']:
            subtree['*files'].append(link)

    def delete(self, link_path):
        # what went wrong here???
        path, link = os.path.split(link_path)
        subtree = self._walk(path)
        subtree['*files'].remove(link)

        if len(subtree['*files']) == 0:
            self._prune(subtree)

    def _prune(self, subtree):
        '''
        Walks up the directory tree starting at the given path, removing empty directories along the way.
        '''

        while '*parent' in subtree:
            parent = subtree['*parent']
            name = subtree['*name']

            if len(subtree['*files']) + len(subtree['*dirs']) == 0:
                parent['*dirs'].remove(name)
                del parent[name]

            subtree = parent

    def list_dir(self, path):
        subtree = self._walk(path)
        return ['.', '..'] + subtree['*dirs'] + subtree['*files']

    def _mkdir(self, subtree, name):
        subtree['*dirs'].append(name)
        
        subtree[name] = {
            '*name': name,
            '*parent': subtree,
            '*dirs': [],
            '*files': []
        }

    def _walk(self, path, create_missing=False):
        subtree = self.tree
        parts = path.split('/')

        for part in parts:
            if not part:
                continue

            if part not in subtree:
                if create_missing:
                    self._mkdir(subtree, part)
                else:
                    raise FuseOSError(ENOENT)
                
            subtree = subtree[part]

        return subtree

    def __getitem__(self, key):
        return self.tree[key]

class TreeView:
    '''
    Provides a directory tree and resolves link paths.
    '''
    
    def __init__(self, views=None):
        if views:
            self.recompute(views)
        else:
            self.links = dict()
            self.tree = DirectoryTree()

    def link_exists(self, link_path):
        return link_path.endswith('desktop.ini') or link_path in self.links

    def list_dir(self, path):
        return self.tree.list_dir(path)

    def resolve_link(self, link_path):
        if link_path.endswith('desktop.ini'):
            base, _ = os.path.split(link_path)
            return os.path.join('/home/linux/music-watch/desktop.ini', base.replace('/', '-'))
        elif link_path in self.links:
            return os.path.join(config.watch.collection_root, self.links[link_path])
        else:
            raise FuseOSError(ENOENT)

    def recompute(self, views):
        '''
        Recompute the TreeView from a list of links.
        '''

        self.links = dict((link_path, file_path)
                          for link_path, file_path in views)
        self.tree = DirectoryTree(views)

    def update(self, catalog):
        # Compute links for modified files and diff with old links

        new_links = set(view.recompute(catalog.entries.values()))
        old_links = set(self.links.items())
        
        add_links = new_links - old_links
        remove_links = old_links - new_links

        # Update the directory tree

        for link_path, file_path in add_links:
            self._add(link_path, file_path)

        for link_path, _ in remove_links:
            self._delete(link_path)

    @staticmethod
    def save(self, filepath='tree.xz'):
        with lzma.open(filepath, 'wb') as f:
            f.write(pickle.dumps(self))

    @staticmethod
    def load(filepath='tree.xz'):
        with lzma.open(filepath, 'rb') as f:
            return pickle.loads(f.read())

    @staticmethod
    def from_catalog(catalog):
        return TreeView(view.recompute(catalog.entries.values()))

    def _add(self, link_path, file_path):
        self.links[link_path] = file_path
        self.tree.add(link_path)

    def _delete(self, link_path):
        del self.links[link_path]
        self.tree.delete(link_path)

    def __getitem__(self, key):
        return self.links[key]
