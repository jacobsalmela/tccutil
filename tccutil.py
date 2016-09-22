#!/usr/bin/env python
import argparse
import sqlite3
import sys
import os
from platform import mac_ver
from distutils.version import StrictVersion as version


##############################
######## VARIABLES ###########

# Utility Name
util_name = os.path.basename(sys.argv[0])

# Utility Version
util_version = '1.2.1'

# Current OS X version
osx_version = version(mac_ver()[0])

# Database Path
tcc_db = '/Library/Application Support/com.apple.TCC/TCC.db'

# Set "sudo" to True if called with Admin-Privileges.
sudo = True if os.getuid() == 0 else False

# Default Verbosity
verbose = False


parser = argparse.ArgumentParser(description='Modify Accesibility Preferences')
parser.add_argument(
  'action',
  metavar='ACTION',
  type=str,
  nargs='?',
  help='This option is only used to perform a reset.',
)
parser.add_argument(
  '--list', '-l', action='store_true',
  help="List all entries in the accessibility database."
)
parser.add_argument(
  '--insert', '-i', action='append', default=[],
  help="Adds the given bundle ID or path to the accessibility database.",
)
parser.add_argument(
  "-v", "--verbose", action='store_true',
  help="Outputs additional info for some commands.",
)
parser.add_argument(
  "-r", "--remove", action='append', default=[],
  help="Removes the given Bundle ID or Path from the Accessibility Database.",
)
parser.add_argument(
  "-e", "--enable", action='append', default=[],
  help="Enables Accessibility Access for the given Bundle ID or Path.",
)
parser.add_argument(
  "-d", "--disable", action='append', default=[],
  help="Disables Accessibility Access for the given Bundle ID or Path."
)
parser.add_argument(
  '--version', action='store_true',
  help="Show the version of this script",
)


##############################
######## FUNCTIONS ###########

def display_version():
  #------------------------
	print "%s %s" % (util_name, util_version)
	sys.exit(0)


def sudo_required():
  #------------------------
  if not sudo:
    print "Error:"
    print "  When accessing the Accessibility Database, %s needs to be run with admin-privileges.\n" % (util_name)
    display_help(1)


def open_database():
  #------------------------
  sudo_required()
  global conn
  global c

  # Check if Datebase is already open, else open it.
  try: conn.execute("")
  except:
    verbose_output("Opening Database...")
    try:
      conn = sqlite3.connect(tcc_db)
      c = conn.cursor()
      verbose_output("Database opened.\n")
    except:
      print "Error opening Database."
      sys.exit(1)


def display_version(error_code=None):
  print "%s %s" % (util_name, util_version)
  sys.exit(0)


def sudo_required():
  if not sudo:
    print "Error:"
    print "  When accessing the Accessibility Database, %s needs to be run with admin-privileges.\n" % (util_name)
    display_help(1)


def display_help(error_code=None):
  parser.print_help()
  if error_code != None: sys.exit(error_code)
  #------------------------
  print "%s %s" % (util_name, util_version)
  sys.exit(0)


def close_database():
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
      print "Error closing Database."
      sys.exit(1)
  except:
    pass


def commit_changes():
  #------------------------
  # Apply the changes and close the sqlite connection.
  verbose_output("Committing Changes...\n")
  conn.commit()


def verbose_output(*args):
  #------------------------
  if verbose:
    try:
      for a in args:
        print a
    except:
      pass


def list_clients():
  #------------------------
  open_database()
  c.execute("SELECT client from access")
  verbose_output("Fetching Entries from Database...\n")
  for row in c.fetchall():
    # Print each entry in the Accessibility pane.
    print row[0]
  verbose_output("")


def cli_util_or_bundle_id(client):
  #------------------------
  global client_type
  # If the app starts with a slash, it is a command line utility.
  # Setting the client_type to 1 will make the item visible in the GUI so you can manually click the checkbox.
  if (client[0] == '/'):
    client_type = 1
    verbose_output("Detected \"%s\" as Command Line Utility." % (client))
  # Otherwise, the app will be a bundle ID, which starts with a com., net., or org., etc.
  else:
    client_type = 0
    verbose_output("Detected \"%s\" as Bundle ID." % (client))


def insert_client(client):
  #------------------------
  open_database()
  # Check if it is a command line utility or a bundle ID as the default value to enable it is different.
  cli_util_or_bundle_id(client)
  verbose_output("Inserting \"%s\" into Database..." % (client))
  if osx_version >= version('10.11'): # El Capitan or higher.
    c.execute("INSERT or REPLACE INTO access VALUES('kTCCServiceAccessibility','%s',%s,1,1,NULL,NULL)" % (client, client_type))
  else: # Yosemite or lower.
    c.execute("INSERT or REPLACE INTO access VALUES('kTCCServiceAccessibility','%s',%s,1,1,NULL)" % (client, client_type))
  commit_changes()


def delete_client(client):
  #------------------------
  open_database()
  verbose_output("Removing \"%s\" from Database..." % (client))
  c.execute("DELETE from access where client IS '%s'" % (client))
  commit_changes()


def enable(client):
  #------------------------
  open_database()
  verbose_output("Enabling %s..." % (client,))
  # Setting typically appears in System Preferences right away (without closing the window).
  # Set to 1 to enable the client.
  c.execute("UPDATE access SET allowed='1' WHERE client='%s'" % (client))
  commit_changes()


def disable(client):
  #------------------------
  open_database()
  verbose_output("Disabling %s..." % (client,))
  # Setting typically appears in System Preferences right away (without closing the window).
  # Set to 0 to disable the client.
  c.execute("UPDATE access SET allowed='0' WHERE client='%s'" % (client))
  commit_changes()


def main():
  #------------------------

  # If no arguments are specified, show help menu and exit.
  if not sys.argv[1:]:
    print "Error:"
    print "  No arguments.\n"
    display_help(2)

  args = parser.parse_args()

  if args.action:
    if args.action == 'reset':
      exit_status = os.system("tccutil {}".format(' '.join(sys.argv[1:])))
      sys.exit(exit_status/256)
    else:
      print "Error\n  Unrecognized command {}".format(args.action)

  if args.verbose:
    # If verbose option is set, set verbose to True and remove all verbose arguments.
    global verbose
    verbose = True

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
