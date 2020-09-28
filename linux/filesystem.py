from catalog import Catalog, Result
from config import root as config
from errno import ENODATA
import gc
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import os
import os.path
from stat import S_IFDIR, S_IFLNK, S_IFREG, S_IRWXU
from time import time
from transport import Server
from uuid import uuid4

# def fail_desktop_ini(func):
#     '''
#     Causes any operation on a file named desktop.ini to fail with ENOENT.
#     '''

#     def decorate(*args):
#         if args[1].endswith('desktop.ini'):
#             raise FuseOSError(ENOENT)
        
#         func(*args)

#     return decorate

class viewfs(LoggingMixIn, Operations):
    '''
    Provides the operations that implement viewfs.
    '''

    def __init__(self, logger, tree_view):
        self.logger = logger
        self.tree_view = tree_view
        self.control_file = str(uuid4())
        self.mount_time = time()

        if os.path.exists(config.view.socket_path):
            os.remove(config.view.socket_path)

        self.server = Server(config)
        self.server.connect()
        self.server.send(self.control_file)

    def _update(self):
        self.logger.debug('receiving updates...')
        updates = self.server.receive()

        self.logger.debug('reading...')
        catalog = Catalog.load(config.watch.catalog_path, config.watch.collection_root)

        self.logger.debug('updating...')

        for file_path in updates['writes']:
            info, result = catalog.add(file_path)

            if result == Result.Added:
                self.logger.info('added: ' + str(info))

            elif result == Result.Modified:
                self.logger.info('modified: ' + str(info))

            elif result == Result.Failed:
                self.logger.info('removed: %s' % file_path)

            elif result == Result.Ignored:
                self.logger.info('ignored: %s' % file_path)

        for file_path in updates['deletes']:
            catalog.remove(file_path)
            self.logger.info('deleted: %s' % file_path)

        for from_path, to_path in updates['renames']:
            catalog.remove(from_path)
            catalog.add(to_path)
            self.logger.info('renamed: %s to %s' % (
                os.path.relpath(from_path, start=config.watch.collection_root),
                os.path.relpath(to_path, start=config.watch.collection_root)))

        catalog.save(config.watch.catalog_path)
        self.logger.info('catalog updated')

        self.logger.debug('updating tree...')
        self.tree_view.update(catalog)

        # Free up memory
        catalog = None
        gc.collect()
        self.logger.info('tree updated')

    def getattr(self, path, fh=None):
        path = path[1:]

        if path == self.control_file:
            # This file is meant to be used by querying the extended attribute 'viewfs.update' to signal that the tree
            # needs to be refreshed. It needs no permissions.
            return dict(
                st_mode=(S_IFREG),
                st_nlink=1,
                st_size=0,
                st_ctime=self.mount_time,
                st_mtime=self.mount_time,
                st_atime=self.mount_time)

        elif self.tree_view.link_exists(path):
            return dict(
                st_mode=(S_IFLNK | 0o444),
                st_nlink=1,
                st_size=len(self.tree_view.resolve_link(path)),
                st_ctime=self.mount_time,
                st_mtime=self.mount_time,
                st_atime=self.mount_time)

        else:
            contents = self.tree_view.list_dir(path)

            return dict(
                st_mode=(S_IFDIR | 0o555),
                st_nlink=len(contents),
                st_ctime=self.mount_time,
                st_mtime=self.mount_time,
                st_atime=self.mount_time)

    def getxattr(self, path, name, position=0):
        if path[1:] == self.control_file and name == 'viewfs.update':
            self._update()
            return b'OK'

        raise FuseOSError(ENODATA)

    def readdir(self, path, fh):
        return self.tree_view.list_dir(path) 

    def readlink(self, path):
        return self.tree_view.resolve_link(path[1:])

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

class Filesystem:
    def __init__(self, logger, tree_view):
        self.operations = viewfs(logger, tree_view)

    def start(self):
        FUSE(self.operations, config.view.view_root, foreground=True, allow_other=True, nonempty=config.view.allow_non_empty)
