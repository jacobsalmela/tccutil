#!/usr/bin/env python


##############################
######### IMPORTS ############

import sqlite3
import sys
import getopt
import os
from platform import mac_ver


##############################
######## VARIABLES ###########

# Utility Name
name = os.path.basename(sys.argv[0])

# OS X version in format of 10.x
v, _, _ = mac_ver()
v = float('.'.join(v.split('.')[:2]))

# Database Path
tcc_db = '/Library/Application Support/com.apple.TCC/TCC.db'

sudo = False
if os.getuid() == 0:
    sudo = True
    conn = sqlite3.connect(tcc_db)
    c = conn.cursor()


##############################
######## FUNCTIONS ###########

def usage(e=None):
	#------------------------
    print "Usage:"
    print "  %s [--help]" % (name,)
    print "  sudo %s [--list]" % (name,)
    print "  sudo %s [--insert | --remove | --enable | --disable] [<bundle_id | cli_path>] [--verbose]" % (name,)
    print ""
    print "Options:"
    print "  -h | --help      Displays this Help Menu."
    print "  -l | --list      Lists all Entries in the Accessibility Database."
    print "  -i | --insert    Adds the given Bundle ID or Path to the Accessibility Database."
    print "  -r | --remove    Removes the given Bundle ID or Path from the Accessibility Database."
    print "  -e | --enable    Enables Accessibility Access for the given Bundle ID or Path."
    print "  -d | --disable   Disables Accessibility Access for the given Bundle ID or Path."
    print "  -v | --verbose   Outputs additional info for some commands."
    print ""


def sudo_required():
	#------------------------
	if sudo == False:
		print "Error:"
		print "  When accessing the Accessibility Database,"
		print "  %s needs to be run with admin-privileges." % (name,)
		print ""
		usage()
		sys.exit(1)

def commit_changes():
	#------------------------
	# Apply the changes and close the sqlite connection
	conn.commit()
	conn.close()


def verboseOutput(*args):
	#------------------------
	if verbose:
		try:
			print "Verbose:", args
		except:
			pass


def list_clients():
	#------------------------
	sudo_required()
	print c.execute("SELECT client from access")
	for row in c.fetchall():
		# Print each entry in the Accessibility pane
		print row[0]


def cli_util_or_bundle_id(client):
	#------------------------
	global client_type
	# If the app starts with a slash, it is a command line utility
	# Setting the client_type to 1 will make the item visible in the GUI so you can manually click the checkbox
	if (client[0] == '/'):
		#print 'Command line utility detected'
		client_type = 1
	# Otherwise, the app will be a bundle ID, which starts with a com., net., or org., etc.
	else:
		client_type = 0


def insert_client(client):
	#------------------------
	sudo_required()
	# Check if it is a command line utility or a bundle ID as the default value to enable it is different
	cli_util_or_bundle_id(client)
	if v > 10.10: # El Capitan or higher.
		c.execute("INSERT or REPLACE INTO access VALUES('kTCCServiceAccessibility','%s',%s,1,1,NULL,NULL)" % (client,client_type))
	else: # Yosemite or lower.
		c.execute("INSERT or REPLACE INTO access VALUES('kTCCServiceAccessibility','%s',%s,1,1,NULL)" % (client,client_type))
	commit_changes()


def delete_client(client):
	#------------------------
	sudo_required()
	c.execute("DELETE from access where client IS '%s'" % (client))
	commit_changes()


def enable(client):
	#------------------------
	sudo_required()
	# Setting typically appears in System Preferences right away (without closing the window)
	# Set to 1 to enable the client
	c.execute("UPDATE access SET allowed='1' WHERE client='%s'" % (client))
	commit_changes()


def disable(client):
	#------------------------
	sudo_required()
	# Setting typically appears in System Preferences right away (without closing the window)
	# Set to 0 to disable the client
	c.execute("UPDATE access SET allowed='0' WHERE client='%s'" % (client))
	commit_changes()



#------------------------
#------------------------
#------------------------
def main():
	#------------------------
	#------------------------
	#------------------------
	try:
		# First arguments are UNIX-style, single-letter arguments
		# Second list are long options.  Those requiring arguments are followed by an =
		opts, args = getopt.getopt(sys.argv[1:], "hlvi:r:e:d:", ["help", "list", "verbose", "insert=", "remove=", "enable=", "disable="])
	except getopt.GetoptError as err:
		# Print help information and exit:
		usage()
		sys.exit(2)
	# Verbosity off by default
	verbose = False

	# Parse arguments for options
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-l", "--list"):
			list_clients()
		elif o in ("-v", "--verbose"):
			verbose = True
			print "Verbose feature to be added at a later date."
		elif o in ("-i", "--insert"):
			insert_client(a)
		elif o in ("-r", "--remove"):
			delete_client(a)
		elif o in ("-e", "--enable"):
			enable(a)
		elif o in ("-d", "--disable"):
			disable(a)
		else:
			assert False, "unhandled option"





if __name__ == "__main__":
	main()
