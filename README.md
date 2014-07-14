tccutil.py
==========

## Modify the OS X Accessiblity Database from the command line
Apple has a utility in `/usr/bin` named `tccutil`, but it only supports one command, which is to `reset` the entire database.  I wanted a command-line utility that would be able to add, remove, list, and take other actions.

## Current Feature Set

1. List existing entries in Accessibility database
2. Insert new item into Accessibility database (even command-line utilities)
3. Remove an existing item from the Accessibility database


## Planned Features

1. Verbosity
2. Enable or disable an existing entry
3. Modify other parts of the TCC.db
