#!/usr/bin/env python3

import argparse
import config

parser = config.ChildArgumentParser()
parser.add_argument('--rebuild', '-r', nargs='?', action='store', const=1, help='Rescans the collection and rebuilds the catalog.')

config = config.init(parser)
args = parser.parse_args()

from catalog import Catalog
from errno import ENOENT
import gc
import logging
import os.path    
import subprocess
import sys
from treeview import TreeView

if sys.platform.startswith('win32'):
    from win32.notify import SystemNotifier
    from win32.filesystem import Filesystem
else:
    from linux.notify import SystemNotifier
    from linux.filesystem import Filesystem

logger = logging.getLogger('viewfs')

def start_viewfs():
    if args.rebuild or not os.path.exists(config.watch.catalog_path):
        logger.info('building catalog...')
        catalog = Catalog.build(config.watch.collection_root)
        catalog.save(config.watch.catalog_path)
        catalog = None
        gc.collect()

    if args.rebuild:
        sys.exit(0)

    logging.basicConfig(level=logging.DEBUG if config.verbose else logging.INFO)

    watch_process = subprocess.Popen(['python3', 'watch.py'])

    logger.info('building tree...')
    catalog = Catalog.load(config.watch.catalog_path, config.watch.collection_root)
    tree_view = TreeView.from_catalog(catalog)
    catalog = None
    gc.collect()

    notifier = SystemNotifier()

    if watch_process.poll() != None:
        # watch crashed
        notifier.stopping()
        sys.exit(2)

    logger.info('mounting filesystem on ' + config.view.view_root)
    filesystem = Filesystem(logger, tree_view)
    notifier.ready()
    filesystem.start()

if __name__ == '__main__':
    start_viewfs()
