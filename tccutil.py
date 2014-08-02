#!/usr/bin/python
##############################
######### IMPORTS ############
import sqlite3
import sys
import getopt
import os
from platform import mac_ver

##############################
######## VARIABLES ###########
# Store OS X version in format of 10.x
v, _, _ = mac_ver()
v = float('.'.join(v.split('.')[:2]))
tcc_db = '/Library/Application Support/com.apple.TCC/TCC.db'
conn = sqlite3.connect(tcc_db)
c = conn.cursor()

##############################
######## FUNCTIONS ###########
def usage(e=None):
	#------------------------
    name = os.path.basename(sys.argv[0])
    print "  _                 _   _  _ "
    print " | |_ ___ ___ _   _| |_( )| |"
    print " | __/ __/ __| | | | __| || |"
    print " | || (_| (__| |_| | |_| || |"
    print "  \__\___\___|\__,_|\__|_||_|"
    print "                                     "
    print "Copyright 2014. Jacob Salmela.  http://jacobsalmela.com"
    print "                                     "
    print "USAGE:--------------------"
    print "                                     "
    print "	%s -h [--help]" % (name,)
    print "	%s -v [--verbose]" % (name,)
    print "	%s -l [--list]" % (name,)
    print "	%s -i [--insert] <bundle id or path to command line utilty>" % (name,)
    print "	%s -r [--remove] <bundle id or path to command line utilty>" % (name,)
    print "	%s -e [--enable] <bundle id or path to command line utilty>" % (name,)
    print "	%s -d [--disable] <bundle id or path to command line utilty>" % (name,)
    print ""

	
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
		#print 'Bundle ID detected'
		client_type = 0	
		

def insert_client(client):
	#------------------------
	# Check if it is a command line utility or a bundle ID as the default value to enable it is different
	cli_util_or_bundle_id(client)
	#print "Client type: " + str(client_type)
	#print "INSERT or REPLACE INTO access VALUES('kTCCServiceAccessibility','%s',%s,1,1,NULL)" % (client,client_type)
	c.execute("INSERT or REPLACE INTO access VALUES('kTCCServiceAccessibility','%s',%s,1,1,NULL)" % (client,client_type))
	commit_changes()
	
	
def delete_client(client):
	#------------------------
	#print "DELETE from access where client IS %s" % (client)	
	c.execute("DELETE from access where client IS '%s'" % (client))
	commit_changes()
	

def enable(client):
	#------------------------
	# Setting typically appears in System Preferences right away (without closing the window)
	# Set to 1 to enable the client
	c.execute("UPDATE access SET allowed='1' WHERE client='%s'" % (client))
	commit_changes()
		
	
def disable(client):
	#------------------------
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
