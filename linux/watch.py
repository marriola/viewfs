import inotify
import inotify.adapters
import logging
import os.path
from watch_event import WatchEvent

# Disable annoying individual event type logs from inotify, since we log the relevant ones
inotify_logger = logging.getLogger('inotify.adapters')
inotify_logger.addFilter(lambda _: 0)

class Watch:
    def __init__(self, path):
        self.watch = inotify.adapters.InotifyTree(path)

    def event_gen(self, yield_nones=False):
        moved_from = {}
        moved_to = {}
        
        for e in self.watch.event_gen(yield_nones):
            if e == None:
                yield None
            else:
                event, event_types, path, filename = e
            
                file_path = os.path.join(path, filename)

                if 'IN_CREATE' in event_types:
                    yield (WatchEvent.CREATE, file_path)
                
                elif 'IN_CLOSE_WRITE' in event_types:
                    yield (WatchEvent.WRITE, file_path)

                elif 'IN_DELETE' in event_types:
                    yield (watchEvent.DELETE, file_path)

                elif 'IN_MOVED_FROM' in event_types:
                    if event.cookie in moved_to:
                        desT_path = moved_to[event.cookie]
                        del moved_to[event.cookie]
                        yield (WatchEvent.MOVE, (file_path, dest_path))
                    else:
                        moved_from[event.cookie] = file_path

                elif 'IN_MOVED_TO' in event_types:
                    if event.cookie in moved_from:
                        src_path = moved_from[event.cookie]
                        del moved_from[event.cookie]
                        yield (WatchEvent.MOVE, (src_path, file_path))
                    else:
                        moved_to[event.cookie] = file_path
