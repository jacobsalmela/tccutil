tccutil.py
==========

## Modify the OS X Accessiblity Database from the command line
Apple has a utility in `/usr/bin` named `tccutil`, but it only supports one command, which is to `reset` the entire database.  I wanted a command-line utility that would be able to add, remove, list, and take other actions.

![tccutil.py logo](http://i2.wp.com/jacobsalmela.com/wp-content/uploads/2014/07/tccutilicon.png?resize=300%2C300)

## Usage

tccutil.py -h [--help]
tccutil.py -l [--list]
tccutil.py -i [--insert] <bundle id or path to command line utilty>
tccutil.py -r [--remove] <bundle id or path to command line utilty>

### Examples
List existing entries in the Accessibility database

`tccutil.py -l`

Add `/usr/bin/osascript` into the Accessibility database (using UNIX-style options)

`tccutil.py -i /usr/bin/osascript`

Add TextExpander into the Accessibility database (using long options)

`tccutil.py --insert com.smileonmymac.textexpander`
`tccutil.py --insert com.smileonmymac.textexpander.helper`

Remove Chrome from the Accessibility database

`tccutil.py -r com.google.chrome`

## Current Feature Set

1. List existing entries in Accessibility database
2. Insert new item into Accessibility database (even command-line utilities)
3. Remove an existing item from the Accessibility database


## Planned Features

1. Verbosity
2. Enable or disable an existing entry
3. Modify other parts of the TCC.db
