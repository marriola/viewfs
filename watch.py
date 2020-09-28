#!/usr/bin/env python3

# Note: Since NTFS makes no guarantees of filename encoding, in order for this
# to work, line 57 of inotify.adapters had to be changed from
#
# path_bytes = path_unicode.encode('utf8')
#
# to
#
# path_bytes = path_unicode.encode('utf-8', 'surrogateescape')

import config
config = config.init()

from catalog import Catalog
import gc
import logging
import os
import os.path
import sys
import time
from transport import Client
from watch_event import WatchEvent

if sys.platform.startswith('win'):
    from win32.watch import Watch
else:
    from linux.watch import Watch

logging.basicConfig(level=logging.DEBUG if config.verbose else logging.INFO)
logger = logging.getLogger('watch')

# Start up viewfs in the background while we set up inotify for our collection
logger.info('setting up watch...')
watch = Watch(config.watch.collection_root)
logger.debug('done')

# Receive a randomly generated UUID from viewfs. This will be the name of the
# pseudo-file we query in order to trigger viewfs to update.

client = Client(config)
client.connect()
uuid = client.receive()
control_file = os.path.join(config.view.view_root, uuid)

writes = []
deletes = []
renames = []
last_update = None

for e in watch.event_gen(yield_nones=True):
    if not e:
        # No events. If any have been logged, send them to viewfs.
        
        if last_update and (time.time() - last_update) >= config.watch.batch_processing_delay:
            # For some reason Winamp writes to a file before deleting it
            writes = [w for w in writes if w not in deletes]
            
            logger.info('processing %d updates' % (len(writes) + len(deletes) + len(renames)))
            client.send({ 'writes': writes, 'deletes': deletes, 'renames': renames })
            response = os.getxattr(control_file, 'viewfs.update')
            logger.debug('server: ' + str(response))

            last_update = None
            writes = []
            deletes = []
            moved_from = {}
            moved_to = {}

        continue
    
    event_type, file_path = e

    logger.debug('%s %s' % (event_type, file_path))

    if not file_path.endswith('.tmp'):
        # Ignore temp files while Winamp retags files
        
        if event_type == WatchEvent.WRITE:
            writes.append(file_path)
            last_update = time.time()
        
        elif event_type == WatchEvent.DELETE:
            deletes.append(file_path)
            last_update = time.time()

        elif event_type == WatchEvent.MOVE:
            renames.append(file_path)
            last_update = time.time()
