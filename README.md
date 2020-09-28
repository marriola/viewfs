# Required packages

## Cross-platform

* mutagen
* unicodecsv

## Linux

* fusepy
* inotify
* sdnotify

## Windows

* TBD

# Configuration

## <root>

| Key      | Purpose                                                                     |
| -------- | --------------------------------------------------------------------------- |
| module   | Loads the properties from the specified module into the configuration root. |
| verbose  | Toggles verbose output                                                      |

## watch

| Key                  | Purpose                                                                              |
| -------------------- | ------------------------------------------------------------------------------------ |
| collectionRoot       | The path to the collection to watch.                                                 |
| catalogPath          | The path to the catalog for the collection.                                          |
| batchProcessingDelay | The time in seconds to wait after the last change to the collection before updating. |

## view

| Key           | Purpose                                                                                |
| ------------- | -------------------------------------------------------------------------------------- |
| viewRoot      | The mount point for the view filesystem.                                               |
| allowNonEmpty | If true, allows the filesystem to be mounted on a non-empty directory.                 |
| socketPath    | The path to the socket used for interprocess communication with the filesystem daemon. |
| socketPort    | The socket port, if not using a Unix socket.                                           |
