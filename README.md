<p align="center">
    <a href="https://jacobsalmela.com/">
        <img src="https://user-images.githubusercontent.com/3843505/108144809-fea82a00-708f-11eb-9c99-884ce4702282.png" width="250" height="250" alt="tccutil">
    </a>
    <br>
    <strong>tccutil.py</strong><br>
    Modify macOS' <code>TCC.db</code> from the command line
</p>

## Modify macOS' Transparency, Consent, and Control (TCC) Framework from the Command Line

Apple has a utility in `/usr/bin` named `tccutil`, but it only supports one command, which is to `reset` the entire database.  It has been like this for many versions of macOS.   I wanted a command-line utility that would be able to add, remove, list, and take other actions.

## SIP Notice

This tool needs SIP disabled in order to function.  The risk of doing so is up to you.

Discussions on this topic can be found here: https://github.com/jacobsalmela/tccutil/discussions/44

## How is `tccutil.py` Different from other solutions?

- `tccutil.py` can be installed without any additional software.
- it has an easy to use syntax
- there are other solutions out there, but there were some things I did not like about them:

  + [Privacy Manager Services](https://github.com/univ-of-utah-marriott-library-apple/privacy_services_manager) has other dependencies that need to be installed (it has also gone over five years without any updates)

  + [tccmanager.py](https://github.com/timsutton/scripts/blob/master/tccmanager/tccmanager.py) uses a `.plist` to add items, which is inconvenient.

- these are also some other projects I found that do similar things

  + [go-tccutil](https://github.com/JesusTinoco/go-tccutil) I actually only recently found this

  + [tccplus](https://github.com/jslegendre/tccplus)

  + [DocSystem/tccutil](https://github.com/DocSystem/tccutil)



# Installation

## Homebrew

Install using Homebrew.

```
brew install tccutil
```

Depending how you have your `$PATH` variable setup, you can simply type `tccutil` (instead of the full path) and it will run this utility _instead_ of Apple's.


## Alternative Install

Clone this repo and manually copy `tccutil.py` to `/usr/local/bin` or run from any directory with `python /path/to/tccutil.py`.

## Usage

**This utility needs super-user priveleges for most operations.** It is important that you either run this as root or use `sudo`, otherwise it won't work and you will end up with “permission denied” errors.

```
usage: tccutil.py [-h] [--service SERVICE] [--list] [--insert INSERT] [-v]
                  [-r REMOVE] [-e ENABLE] [-d DISABLE] [--version]
                  [ACTION]

Modify Accesibility Preferences

positional arguments:
  ACTION                This option is only used to perform a reset.

optional arguments:
  -h, --help            show this help message and exit
  --service SERVICE, -s SERVICE
                        Set TCC service
  --list, -l            List all entries in the accessibility database.
  --insert INSERT, -i INSERT
                        Adds the given bundle ID or path to the accessibility
                        database.
  -v, --verbose         Outputs additional info for some commands.
  -r REMOVE, --remove REMOVE
                        Removes a given Bundle ID or Path from the
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

```bash
sudo tccutil.py --list
```

Add `/usr/bin/osascript` to the Accessibility Database (using UNIX-Style Option)

```bash
sudo tccutil.py -i /usr/bin/osascript
````

Add *Script Editor* to the Accessibility Database (using Long Option)

```bash
sudo tccutil.py --insert com.apple.ScriptEditor2
```

Remove *Terminal* from the Accessibility Database

```bash
sudo tccutil.py --remove com.apple.Terminal
```

Enable *Terminal* (must already exist in the Database)

```bash
sudo tccutil.py --enable com.apple.Terminal
```

Disable `/usr/bin/osascript` (must already exist in the Database)

```bash
sudo tccutil.py -d /usr/bin/osascript
```

## Contributing

Many people have contributed already, so feel free to make a PR and we'll get it merged in.
