#!/usr/bin/env python

# ****************************************************************************
# tccutil.py, Utility to modify the macOS Accessibility Database (TCC.db)
#
# Copyright (C) 2020, @jacobsalmela
# Copyright (C) 2023, @tnarik
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
# *****************************************************************************

import argparse
import sqlite3
import sys
import os
import pwd
import hashlib
from platform import mac_ver
from packaging.version import Version as version

# Utility Name
util_name = os.path.basename(sys.argv[0])

# Utility Version
util_version = '1.4.0'

# Current OS X version
osx_version = version(mac_ver()[0])  # mac_ver() returns 10.16 for Big Sur instead 11.+

# Database Path (System by default)
tcc_db = '/Library/Application Support/com.apple.TCC/TCC.db'

# Set "sudo" to True if called with Admin-Privileges.
sudo = True if os.getuid() == 0 else False

# Default Verbosity
verbose = False

# TCC Service
default_service = "kTCCServiceAccessibility"

parser = argparse.ArgumentParser(description='Modify Accesibility Preferences')
parser.add_argument(
    'action',
    metavar='ACTION',
    type=str,
    nargs='?',
    help='This option is only used to perform a reset, using "/usr/bin/tccutil".\
        See `man tccutil` for additional syntax',
)
parser.add_argument(
    '--service', '-s',
    default=default_service,
    help="Set TCC service"
)

parser.add_argument(
    '--list', '-l', action='store_true',
    help="List all entries in the accessibility database"
)
parser.add_argument(
     '--digest', action='store_true',
     help="Print the digest hash of the accessibility database"
 )
parser.add_argument(
    '--insert', '-i', action='append', default=[],
    help="Adds the given bundle ID or path to the accessibility database",
)
parser.add_argument(
    "-v", "--verbose", action='store_true',
    help="Outputs additional info for some commands",
)
parser.add_argument(
    "-r", "--remove", action='append', default=[],
    help="Removes a given Bundle ID or Path from the Accessibility Database",
)
parser.add_argument(
    "-e", "--enable", action='append', default=[],
    help="Enables Accessibility Access for the given Bundle ID or Path",
)
parser.add_argument(
    "-d", "--disable", action='append', default=[],
    help="Disables Accessibility Access for the given Bundle ID or Path"
)
parser.add_argument(
    '--user', '-u',
    nargs="?",
    const='',
    default=None,
    help="Modify accessibility database for a given user (defaults to current, if no additional parameter is provided)",
)
parser.add_argument(
    '--version', action='store_true',
    help="Show the version of this script",
)

def display_version():
    """Print the version of this utility."""
    print(f"{util_name} {util_version}")
    sys.exit(0)


def sudo_required():
    """Check if user has root priveleges to access the database."""
    if not sudo:
        print("Error:", file=sys.stderr)
        print(f"  When accessing the Accessibility Database, {util_name} needs to be run with admin-privileges.\n", file=sys.stderr)
        display_help(1)


def digest_check(digest_to_check):
     """Validates that a digest for the table is one that can be used with tccutil."""
     # Do a sanity check that TCC access table has expected structure
     accessTableDigest = ""
     for row in digest_to_check.fetchall():
        accessTableDigest = hashlib.sha1(row[0].encode('utf-8')).hexdigest()[0:10]
        break

     return accessTableDigest


def open_database(digest=False):
    """Open the database for editing values."""
    sudo_required()
    global conn
    global c

    # Check if Datebase is already open, else open it.
    try:
        conn.execute("")
    except:
        verbose_output("Opening Database...")
    try:
        if not os.path.isfile(tcc_db):
            print("TCC Database has not been found.")
            sys.exit(1)
        conn = sqlite3.connect(tcc_db)
        c = conn.cursor()

        # Do a sanity check that TCC access table has expected structure
        accessTableDigest = digest_check(c.execute("SELECT sql FROM sqlite_master WHERE name='access' and type='table'"))

        if digest:
          print(accessTableDigest)
          sys.exit(0)

        # check if table in DB has expected structure:
        if not (accessTableDigest == "8e93d38f7c" or  # prior to El Capitan
                # El Capitan , Sierra, High Sierra
                (osx_version >= version('10.11') and
                    accessTableDigest in ["9b2ea61b30", "1072dc0e4b"]) or
                # Mojave and Catalina
                (osx_version >= version('10.14') and
                    accessTableDigest in ["ecc443615f", "80a4bb6912"]) or
                # Big Sur and later
                (osx_version >= version('10.16') and
                   accessTableDigest in ["3d1c2a0e97", "cef70648de"]) or
                # Sonoma
                (osx_version >= version('14.0') and
                   accessTableDigest in ["34abf99d20", "e3a2181c14"])
                ):
            print(f"TCC Database structure is unknown ({accessTableDigest})", file=sys.stderr)
            sys.exit(1)

        verbose_output("Database opened.\n")
    except TypeError:
        print("Error opening Database.  You probably need to disable SIP for this to work.", file=sys.stderr)
        sys.exit(1)


def display_help(error_code=None):
    """Display help an usage."""
    parser.print_help()
    if error_code is not None:
        sys.exit(error_code)
    print(f"{util_name} {util_version}")
    sys.exit(0)


def close_database():
    """Close the database."""
    try:
        conn.execute("")
        try:
            verbose_output("Closing Database...")
            conn.close()
            try:
                conn.execute("")
            except:
                verbose_output("Database closed.")
        except:
            print("Error closing Database.", file=sys.stderr)
        sys.exit(1)
    except:
        pass


def commit_changes():
    """Apply the changes and close the sqlite connection."""
    verbose_output("Committing Changes...\n")
    conn.commit()


def verbose_output(*args):
    """Show verbose output."""
    if verbose:
        try:
            for a in args:
                print(a)
        except:
            pass


def list_clients():
    """List items in the database."""
    open_database()
    c.execute(f"SELECT client from access WHERE service is '{service}'")
    verbose_output("Fetching Entries from Database...\n")
    for row in c.fetchall():
        # print each entry in the Accessibility pane.
        print(row[0])
    verbose_output("")


def cli_util_or_bundle_id(client):
    """Check if the item is a path or a bundle ID."""
    # If the app starts with a slash, it is a command line utility.
    # Setting the client_type to 1 will make the item visible in the
    # GUI so you can manually click the checkbox.
    if client[0] == '/':
        client_type = 1
        verbose_output(f'Detected "{client}" as Command Line Utility.')
    # Otherwise, the app will be a bundle ID, which starts
    # with a com., net., or org., etc.
    else:
        client_type = 0
        verbose_output(f'Detected "{client}" as Bundle ID.')
    return client_type


def insert_client(client):
    """Insert a client into the database."""
    open_database()
    # Check if it is a command line utility or a bundle ID
    # as the default value to enable it is different.
    client_type = cli_util_or_bundle_id(client)
    verbose_output(f'Inserting "{client}" into Database...')
    # Sonoma
    if osx_version >= version('14.0'):
        try:
          c.execute(f"INSERT or REPLACE INTO access VALUES('{service}','{client}',{client_type},2,4,1,NULL,NULL,0,'UNUSED',NULL,0, NULL, NULL, NULL,'UNUSED', NULL)")
        except sqlite3.OperationalError:
          print("Attempting to write a readonly database.  You probably need to disable SIP.", file=sys.stderr)
    # Big Sur and later
    elif osx_version >= version('10.16'):
        try:
          c.execute(f"INSERT or REPLACE INTO access VALUES('{service}','{client}',{client_type},2,4,1,NULL,NULL,0,'UNUSED',NULL,0,0)")
        except sqlite3.OperationalError:
          print("Attempting to write a readonly database.  You probably need to disable SIP.", file=sys.stderr)
    # Mojave through Big Sur
    elif osx_version >= version('10.14'):
        c.execute(f"INSERT or REPLACE INTO access VALUES('{service}','{client}',{client_type},1,1,NULL,NULL,NULL,'UNUSED',NULL,0,0)")
    # El Capitan through Mojave
    elif osx_version >= version('10.11'):
        c.execute(f"INSERT or REPLACE INTO access VALUES('{service}','{client}',{client_type},1,1,NULL,NULL)")
    # Yosemite or lower
    else:
        c.execute(f"INSERT or REPLACE INTO access VALUES('{service}','{client}',{client_type},1,1,NULL)")
    commit_changes()


def delete_client(client):
    """Remove a client from the database."""
    open_database()
    verbose_output(f'Removing "{client}" from Database...')
    try:
      c.execute(f"DELETE from access where client IS '{client}' AND service IS '{service}'")
    except sqlite3.OperationalError:
      print("Attempting to write a readonly database.  You probably need to disable SIP.", file=sys.stderr)
    commit_changes()


def enable(client):
    """Add a client from the database."""
    open_database()
    verbose_output(f'Enabling {client}...')
    # Setting typically appears in System Preferences
    # right away (without closing the window).
    # Set to 1 to enable the client.
    enable_mode_name = 'auth_value' if osx_version >= version('10.16') else 'allowed'
    try:
      c.execute(f"UPDATE access SET {enable_mode_name}='1' WHERE client='{client}' AND service IS '{service}'")
    except sqlite3.OperationalError:
      print("Attempting to write a readonly database.  You probably need to disable SIP.", file=sys.stderr)
    commit_changes()


def disable(client):
    """Disable a client in the database."""
    open_database()
    verbose_output(f"Disabling {client}...")
    # Setting typically appears in System Preferences
    # right away (without closing the window).
    # Set to 0 to disable the client.
    enable_mode_name = 'auth_value' if osx_version >= version('10.16') else 'allowed'
    try:
      c.execute(f"UPDATE access SET {enable_mode_name}='0' WHERE client='{client}' AND service IS '{service}'")
    except sqlite3.OperationalError:
      print("Attempting to write a readonly database.  You probably need to disable SIP.", file=sys.stderr)
    commit_changes()


def main():
    """Run the main function."""
    # If no arguments are specified, show help menu and exit.
    if not sys.argv[1:]:
        print("Error:")
        print("  No arguments.\n")
        display_help(2)

    args, rest = parser.parse_known_args()

    if args.version:
        display_version()
        return

    global tcc_db
    if args.user != None:
        try:
            if (len(args.user) > 0): pwd.getpwnam(args.user)
            tcc_db = os.path.abspath(os.path.expanduser(f'~{args.user}/{tcc_db}'))
        except KeyError:
            print(f'User "{args.user}" does not exist. Do you mean to use "{args.user}" as ACTION?', file=sys.stderr)
            sys.exit(1)

    if args.action:
        if args.action == 'reset':
            exit_status = os.system(f'/usr/bin/tccutil -v {" ".join(rest)}')
            sys.exit(exit_status / 256)
        else:
            print(f'Error\n  Unrecognized command "{args.action}"', file=sys.stderr)

    global service
    service = args.service

    if args.verbose:
        # If verbose option is set, set verbose to True and remove all verbose arguments.
        global verbose
        verbose = True

    if args.digest:
         open_database(digest=True)

    if args.list:
        list_clients()
        return

    for item_to_remove in args.remove:
        delete_client(item_to_remove)

    for item in args.insert:
        insert_client(item)

    for item in args.enable:
        enable(item)

    for item in args.disable:
        disable(item)

    close_database()
    sys.exit(0)


if __name__ == '__main__':
    main()
