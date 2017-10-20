`tccutil.py`
==========


<p align="center"><img src='http://i2.wp.com/jacobsalmela.com/wp-content/uploads/2014/07/tccutilicon.png?resize=128%2C128' alt='tccutil.py logo'/></p>


## Modify OS X's Accessibility Database from the Command Line

Apple has a utility in `/usr/bin` named `tccutil`, but it only supports one command, which is to `reset` the entire database.  I wanted a command-line utility that would be able to add, remove, list, and take other actions.

## macOS Sierra Support

Due to SIP, this utility will no longer work to modify the database (see [#18](https://github.com/jacobsalmela/tccutil/issues/18))

## How is `tccutil.py` Different?

+ `tccutil.py` can be installed without any additional software.

+ It can then be run **just like any other command line tool**. I also wanted the syntax to be easy to remember without having to look it up in the help menu.

+ There are other solutions out there, but there were some things I did not like about them:

  + [Privacy Manager Services](https://github.com/univ-of-utah-marriott-library-apple/privacy_services_manager) has other dependencies that need to be installed.

  + [tccmanager.py](https://github.com/timsutton/scripts/blob/master/tccmanager/tccmanager.py) uses a `.plist` to add items, which is inconvenient.


# Installation

+ Install using Homebrew, then run with `tccutil`:

```
      brew install tccutil
```

Depending how you have your `$PATH` variable setup, you can simply type `tccutil` (instead of the full path) and it will run this utility instead of Apple's.

+ Download from here and

  + copy manually to `/usr/local/bin`, then run with `tccutil.py`, or

  + run from any directory with `python /path/to/tccutil.py`.


## Usage

**This utility needs super-user priveleges for most operations.** It is important that you either run this as root or use `sudo`, otherwise it won't work and you will end up with “permission denied” errors.

```
usage: tccutil.py [-h] [--list] [--insert INSERT] [-v] [-r REMOVE] [-e ENABLE]
                  [-d DISABLE] [--version]
                  [ACTION]

Modify Accessibility Preferences

positional arguments:
  ACTION                Reset using Apple's /usr/bin/tccutil

optional arguments:
  -h, --help            show this help message and exit
  --list, -l            List all entries in the accessibility database.
  --insert INSERT, -i INSERT
                        Adds the given bundle ID or path to the accessibility
                        database.
  -v, --verbose         Outputs additional info for some commands.
  -r REMOVE, --remove REMOVE
                        Removes the given Bundle ID or Path from the
                        Accessibility Database.
  -e ENABLE, --enable ENABLE
                        Enables Accessibility Access for the given Bundle ID
                        or Path.
  -d DISABLE, --disable DISABLE
                        Disables Accessibility Access for the given Bundle ID
                        or Path.
  --version             Show the version of this script
```


### Examples

List existing Entries in the Accessibility Database

    sudo tccutil.py --list

Add `/usr/bin/osascript` to the Accessibility Database (using UNIX-Style Option)

    sudo tccutil.py -i /usr/bin/osascript

Add *Script Editor* to the Accessibility Database (using Long Option)

    sudo tccutil.py --insert com.apple.ScriptEditor2

Remove *Terminal* from the Accessibility Database

    sudo tccutil.py --remove com.apple.Terminal

Enable *Terminal* (must already exist in the Database)

    sudo tccutil.py --enable com.apple.Terminal

Disable `/usr/bin/osascript` (must already exist in the Database)

    sudo tccutil.py -d /usr/bin/osascript


## Current Feature Set

+ List existing Entries in Accessibility Database
+ Insert new Item into Accessibility Database (even Command-Line Utilities)
+ Remove an existing Item from the Accessibility Database
+ Enable or disable an Entry


## Planned Features

+ Modify other parts of the `TCC.db`.
