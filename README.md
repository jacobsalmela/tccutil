`tccutil.py`
==========


<p align="center"><img src='http://i2.wp.com/jacobsalmela.com/wp-content/uploads/2014/07/tccutilicon.png?resize=128%2C128' alt='tccutil.py logo'/></p>


## Modify OS X's Accessiblity Database from the Command Line

Apple has a utility in `/usr/bin` named `tccutil`, but it only supports one command, which is to `reset` the entire database.  I wanted a command-line utility that would be able to add, remove, list, and take other actions.


## How is `tccutil.py` Different?

+ `tccutil.py` can be installed without any additional software.

+ It can then be run **just like any other command line tool**. I also wanted the syntax to be easy to remember without having to look it up in the help menu.

+ There are other solutions out there, but there were some things I did not like about them:

  + [Privacy Manager Services](https://github.com/univ-of-utah-marriott-library-apple/privacy_services_manager) has other dependencies that need to be installed.

  + [tccmanager.py](https://github.com/timsutton/scripts/blob/master/tccmanager/tccmanager.py) uses a `.plist` to add items, which is inconvenient.


# Installation

+ Install using Homebrew, then run with `tccutil`:

      brew install tccutil

+ Download from here and
  
  + copy manually to `/usr/local/bin`, then run with `tccutil.py`, or

  + run from any directory with `python /path/to/tccutil.py`.


## Usage

**This utility needs super-user priveleges for most operations.** It is important that you either run this as root or use `sudo`, otherwise it won't work and you will end up with “permission denied” errors.

```
Usage:
  tccutil.py [--help | --version]
  sudo tccutil.py [--list] [--verbose]
  sudo tccutil.py [--insert | --remove | --enable | --disable] <bundle_id | cli_path> [--verbose]

Pass through reset command to built-in OS X utility:
  tccutil.py reset <Accessibility | AddressBook | Calendar | CoreLocationAgent | Facebook | Reminders | Twitter>

Options:
  -h | --help      Displays this Help Menu.
  -l | --list      Lists all Entries in the Accessibility Database.
  -i | --insert    Adds the given Bundle ID or Path to the Accessibility Database.
  -r | --remove    Removes the given Bundle ID or Path from the Accessibility Database.
  -e | --enable    Enables Accessibility Access for the given Bundle ID or Path.
  -d | --disable   Disables Accessibility Access for the given Bundle ID or Path.
  -v | --verbose   Outputs additional info for some commands.
       --version   Prints the current version of this utility.
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
