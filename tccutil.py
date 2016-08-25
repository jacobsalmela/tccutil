#!/usr/bin/env python


##############################
######### IMPORTS ############

import sqlite3
import sys
import getopt
import os
import hashlib
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


##############################
######## FUNCTIONS ###########

def display_version():
  #------------------------
	print "%s %s" % (util_name, util_version)
	sys.exit(0)


def display_help(error_code=None):
  #------------------------
  print "Usage:"
  print "  %s [--help | --version]" % (util_name)
  print "  sudo %s [--list] [--verbose]" % (util_name)
  print "  sudo %s [--insert | --remove | --enable | --disable] <bundle_id | cli_path> [--verbose]" % (util_name)
  print ""
  print "Pass through reset command to built-in OS X utility:"
  print "  %s reset <Accessibility | AddressBook | Calendar | CoreLocationAgent | Facebook | Reminders | Twitter>" % (util_name)
  print ""
  print "Options:"
  print "  -h | --help      Displays this Help Menu."
  print "  -l | --list      Lists all Entries in the Accessibility Database."
  print "  -i | --insert    Adds the given Bundle ID or Path to the Accessibility Database."
  print "  -r | --remove    Removes the given Bundle ID or Path from the Accessibility Database."
  print "  -e | --enable    Enables Accessibility Access for the given Bundle ID or Path."
  print "  -d | --disable   Disables Accessibility Access for the given Bundle ID or Path."
  print "  -v | --verbose   Outputs additional info for some commands."
  print "       --version   Prints the current version of this utility."
  if error_code != None: sys.exit(error_code)


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
      if not os.path.isfile(tcc_db):
        print "TCC Database has not been found."
        sys.exit(1)
      conn = sqlite3.connect(tcc_db)
      c = conn.cursor()

      # Do a sanity check that TCC access table has expected structure
      c.execute("SELECT sql FROM sqlite_master WHERE name='access' and type='table'")
      accessTableDigest=""
      for row in c.fetchall():
        accessTableDigest=hashlib.sha1(row[0]).hexdigest()[0:10]
        break;
      # check if table in DB has expected structure:
      if not (
        accessTableDigest == "8e93d38f7c" #prior to El Capitan
        or
        (osx_version >= version('10.11') and accessTableDigest=="9b2ea61b30")
      ):
        print "TCC Database structure is unknown."
        sys.exit(1)

      verbose_output("Database opened.\n")
    except:
      print "Error opening Database."
      sys.exit(1)


def close_database():
  #------------------------
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

  # Pass reset option to OS X's built-in tccutil.
  if sys.argv[1] == "reset":
    args = ''
    for arg in sys.argv[1:]:
      args += " %s" % arg
    exit_status = os.system("tccutil %s" % args)
    sys.exit(exit_status/256)

  try:
    # First arguments are UNIX-style, single-letter arguments. Those requiring arguments are followed by an :.
    # Second list are long options. Those requiring arguments are followed by an =.
    opts, args = getopt.getopt(sys.argv[1:], "hlvi:r:e:d:", ['help', 'version', 'list', 'verbose', 'insert=', 'remove=', 'enable=', 'disable='])
  except getopt.GetoptError as option_error:
      # If unknown options are specified, show help menu and exit.
    print "Error:"
    print "  %s\n" % (option_error)
    display_help(2)

  # If verbose option is set, set verbose to True and remove all verbose arguments.
  global verbose
  delete_indexes = []
  for idx, (opt, arg) in enumerate(opts):
    if opt in ('-v', '--verbose'):
      verbose = True
      delete_indexes.insert(0,idx)
  for idx in delete_indexes:
    del opts[idx]

  # Parse arguments for options
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      display_help(0)
    elif opt in ('--version'):
      display_version()
    elif opt in ('-l', '--list'):
      list_clients()
    elif opt in ('-i', '--insert'):
      insert_client(arg)
    elif opt in ('-r', '--remove'):
      delete_client(arg)
    elif opt in ('-e', '--enable'):
      enable(arg)
    elif opt in ('-d', '--disable'):
      disable(arg)
    else:
      assert False, "unhandled option"

  close_database()
  sys.exit(0)




if __name__ == '__main__':
  main()
