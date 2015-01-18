tccutil.py
==========

## Modify the OS X Accessiblity Database from the command line
Apple has a utility in `/usr/bin` named `tccutil`, but it only supports one command, which is to `reset` the entire database.  I wanted a command-line utility that would be able to add, remove, list, and take other actions.

![tccutil.py logo](http://i2.wp.com/jacobsalmela.com/wp-content/uploads/2014/07/tccutilicon.png?resize=300%2C300)

## How is tccutil.py Different?
**tccutil.py** can just be installed to `/usr/sbin` without any additional software. It can then be **run just like any other command line tool**.  I also wanted the syntax to be easy to remember without having to look it up in the usage line.  There are other solutions out there, but there were some things I did not like about them:

+ [Privacy Manager Services](https://github.com/univ-of-utah-marriott-library-apple/privacy_services_manager)--has other dependencies that need to be installed

+ [tccmanager.py](https://github.com/timsutton/scripts/blob/master/tccmanager/tccmanager.py)--uses a .plist to add items, which is inconvenient

## Usage

### This utility needs super-user priveleges.  Run this as root or use `sudo`.
It is important that you either run this as root or use `sudo`, otherwise, it will not work and you will end up with "permission denied" errors.

`sudo tccutil.py -h [--help]`

`sudo tccutil.py -l [--list]`

`sudo tccutil.py -i [--insert] <bundle id or path to command line utilty>`

`sudo tccutil.py -r [--remove] <bundle id or path to command line utilty>`

`sudo tccutil.py -e [--enable] <bundle id or path to command line utilty>`

`sudo tccutil.py -d [--disable] <bundle id or path to command line utilty>`

### Examples
List existing entries in the Accessibility database

`sudo tccutil.py -l`

Add `/usr/bin/osascript` into the Accessibility database (using UNIX-style options)

`sudo tccutil.py -i /usr/bin/osascript`

Add TextExpander into the Accessibility database (using long options)

`sudo tccutil.py --insert com.smileonmymac.textexpander`

`sudo tccutil.py --insert com.smileonmymac.textexpander.helper`

Remove Chrome from the Accessibility database

`sudo tccutil.py -r com.google.chrome`

Enable Chrome (must already exist in the list)

`sudo tccutil.py --enable com.google.chrome`

Disable /usr/sbin/jamfAgent (must already exist in the list)

`sudo tccutil.py -d /usr/sbin/jamfAgent`

## Current Feature Set

1. List existing entries in Accessibility database
2. Insert new item into Accessibility database (even command-line utilities)
3. Remove an existing item from the Accessibility database
4. Enable or disable an entry


## Planned Features

1. Verbosity
2. --Enable or disable an existing entry-- **COMPLETE**
3. Modify other parts of the TCC.db
