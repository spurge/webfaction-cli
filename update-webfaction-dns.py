#!/usr/bin/env python
# encoding: utf-8
"""
update-webfaction-dns.py

This script will update your Webfaction DNS override records with
specified ip-adresses or your dynamic external ip.

Created by spurge on 2012-09-27.
Copyright (c) 2012 Klandestino AB. All rights reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import sys
import getopt
import re
import xmlrpclib
import urllib2

help_message = '''
\033[1;32mupdate-webfaction-dns.py \033[0;33m[options] \033[0;34musername:password[@machine] \033[0;35mdomain[@ip-adress] [, domain ...] ...\033[0m updates your DNS override records at Webfaction.

* \033[0;34mmachine\033[0m is case-sensitive, so Web100 is Web100 and not web100.
* \033[0;35mip-address\033[0m is optional. If omitted your current external IP will be fetched.

Available options are:

  \033[0;33m-v\033[0m           Verbose. Prints almost everything that
                   happens.

  \033[0;33m-h\033[0m | \033[0;33m--help\033[0m  Prints this help-text.
'''

class Usage( Exception ):
	def __init__( self, msg ):
		self.msg = msg

def main( argv = None ):
	if argv is None:
		argv = sys.argv

	try:
		try:
			opts, args = getopt.getopt( argv[ 1: ], "hv", [ "help" ] )
		except getopt.error, msg:
			raise Usage( msg )

		verbose = False

		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ( "-h", "--help" ):
				raise Usage( help_message )
			if option in ( "-o", "--output" ):
				output = value

		try:
			login = re.match( '^([^\:]+)\:([^&@]+)(?:@([^&]+))?$', args[ 0 ] )
			args = args[ 1: ]
			if verbose:
				print >> sys.stdout, 'Using login: {0}:[password]@{1}'.format( login.group( 1 ), login.group( 3 ) )
		except AttributeError, msg:
			raise Usage( 'Username and password are not specified correctly' )

		try:
			domains = []
			for domain in args:
				domain = re.match( '^([^$@]+)(?:@([^$]+))?$', domain )
				domains.append( domain )
				if verbose:
					print >> sys.stdout, 'With domain: {0}@{1}'.format( domain.group( 1 ), domain.group( 2 ) )
		except AttributeError, msg:
			raise Usage( msg )

		if not len( domains ):
			raise Usage( 'No domains are specified' )

		try:
			server = xmlrpclib.Server( 'https://api.webfaction.com/' )
		except IOError, msg:
			raise Usage( msg )

		try:
			if login.group( 3 ):
				session_id, account = server.login( login.group( 1 ), login.group( 2 ), login.group( 3 ) )
			else:
				session_id, account = server.login( login.group( 1 ), login.group( 2 ) )
		except xmlrpclib.Fault, msg:
			raise Usage( 'Could not login' )

		if verbose:
			print >> sys.stdout, 'Logged in'

		for domain in domains:
			if domain.group( 2 ):
				ip = domain.group( 2 )
			else:
				try:
					ip = re.search( '((?:[0-9]{1,3}\.?){4})', urllib2.urlopen( 'http://checkip.dyndns.org' ).read() ).group( 1 )
					if verbose:
						print >> sys.stdout, 'Fetched your external IP: {0}'.format( ip )
				except urllib2.URLError, msg:
					raise Usage( msg )
				except AttributeError, msg:
					raise Usage( msg )

			try:
				server.create_dns_override( session_id, domain.group( 1 ), ip )
			except xmlrpclib.Fault, msg:
				raise Usage( msg )

			if verbose:
				print >> sys.stdout, 'Updated domain: {0} with IP: {1}'.format( domain.group( 1 ), ip )

	except Usage, err:
		print >> sys.stderr, str( err.msg )
		print >> sys.stderr, "For help use --help"
		return 2

if __name__ == "__main__":
	sys.exit( main() )
