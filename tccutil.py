#!/usr/bin/env python


##############################
######### IMPORTS ############

import sqlite3
import sys
import getopt
import os
from platform import mac_ver
from distutils.version import StrictVersion as version


##############################
######## VARIABLES ###########

# Utility Name
util_name = os.path.basename(sys.argv[0])

# Current OS X version
osx_version = version(mac_ver()[0])

# Database Path
tcc_db = '/Library/Application Support/com.apple.TCC/TCC.db'

# Set "sudo" to True if called with admin-privileges.
sudo = True if os.getuid() == 0 else False

# Default Verbosity
verbose = False


##############################
######## FUNCTIONS ###########

def usage(error_code=None):
  #------------------------
  print "Usage:"
  print "  %s [--help]" % (util_name)
  print "  sudo %s [--list]" % (util_name)
  print "  sudo %s [--insert | --remove | --enable | --disable] [<bundle_id | cli_path>] [--verbose]" % (util_name)
  print ""
  print "Options:"
  print "  -h | --help      Displays this Help Menu."
  print "  -l | --list      Lists all Entries in the Accessibility Database."
  print "  -i | --insert    Adds the given Bundle ID or Path to the Accessibility Database."
  print "  -r | --remove    Removes the given Bundle ID or Path from the Accessibility Database."
  print "  -e | --enable    Enables Accessibility Access for the given Bundle ID or Path."
  print "  -d | --disable   Disables Accessibility Access for the given Bundle ID or Path."
  print "  -v | --verbose   Outputs additional info for some commands."
  if error_code != None: sys.exit(error_code)


def sudo_required():
  #------------------------
  if not sudo:
    print "Error:"
    print "  When accessing the Accessibility Database, %s needs to be run with admin-privileges.\n" % (util_name)
    usage(1)


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




#------------------------
#------------------------
#------------------------
def main():
  #------------------------
  #------------------------
  #------------------------
  # If no arguments are specified, show help menu and exit.
  if not sys.argv[1:]:
    print "Error:"
    print "  No arguments.\n"
    usage(2)

  try:
    # First arguments are UNIX-style, single-letter arguments. Those requiring arguments are followed by an :.
    # Second list are long options. Those requiring arguments are followed by an =.
    opts, args = getopt.getopt(sys.argv[1:], "hlvi:r:e:d:", ['help', 'list', 'verbose', 'insert=', 'remove=', 'enable=', 'disable='])
  except getopt.GetoptError as option_error:
      # If unknown options are specified, show help menu and exit.
    print "Error:"
    print "  %s\n" % (option_error)
    usage(2)

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
      usage(0)
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
