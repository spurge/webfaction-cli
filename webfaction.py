#!/usr/bin/env python
# encoding: utf-8
"""
webfaction.py

This script will work as a command line interface for reaching
the Webfaction API.

Created by spurge on 2012-09-29.
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
from datetime import datetime

help_message = '''
\033[1;32mwebfaction.py \033[0;33m[options] \033[0;34musername:password[@machine] \033[0;35maction arguments [, action ...] ...\033[0m calls the Webfaction API with specified actions and arguments.

  * connects to Webfaction using SSL [https://api.webfaction.com/]
  * \033[0;34mmachine\033[0m is case-sensitive, so Web100 is Web100 and not web100.

Available actions are:

  \033[1;35mcreate_dns_override\033[0;33m domain[@ip-address]\033[0m
    * Creates a DNS override. The domain must be created first.
    * \033[0;33mip-address\033[0m is optional. If omitted your current external IP will be fetched.

Available options are:

  \033[0;33m-v\033[0m           Verbose. Prints almost everything that happens.

  \033[0;33m-h\033[0m | \033[0;33m--help\033[0m  Prints this help-text.
'''

class Usage( Exception ):
	def __init__( self, err ):
		self.err = err
		self.msg = help_message

class WError( Exception ):
	def __init__( self, err, expl ):
		self.err = '{1} :: {0}'.format( err, expl )

class Log():
	def __init__( self, verbose ):
		self.verbose = verbose

	def say( self, message ):
		if self.verbose:
			print >> sys.stdout, '{0} :: debug :: {1}'.format(
				datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ),
				message
			)
	
	def err( self, message ):
		print >> sys.stderr, '{0} :: error :: {1}'.format(
			datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ),
			message
		)


class Webfaction:
	def __init__( self ):
		self.account = None
		self.session_id = None

		try:
			self.server = xmlrpclib.Server( 'https://api.webfaction.com/' )
		except IOError, err:
			raise WError( err, 'Could not connect to Webfaction' )

	def get_external_ip( self ):
		try:
			ip = re.search( '((?:[0-9]{1,3}\.?){4})', urllib2.urlopen( 'http://checkip.dyndns.org' ).read() ).group( 1 )
		except urllib2.URLError, err:
			raise WError( err, 'Could not fetch your external ip-address' )
		except AttributeError, err:
			raise WError( err, 'Could not parse data from dyndns.org when fetching your ip-address' )

		return ip

	def login( self, username, password, machine = None ):
		try:
			if machine:
				self.session_id, self.account = self.server.login( username, password, machine )
			else:
				self.session_id, self.account = self.server.login( username, password )
		except xmlrpclib.Fault, err:
			raise WError( err, 'Could not login' )
	
	def create_dns_override( self, domain, ip = None ):
		if ip == None:
			ip = self.get_external_ip()

		try:
			self.server.create_dns_override( self.session_id, domain, ip )
		except xmlrpclib.Fault, err:
			raise WError( err, 'Could not create a dns override' )

		return domain, ip

def main( argv = None ):
	if argv is None:
		argv = sys.argv

	log = Log( False )

	try:
		try:
			opts, args = getopt.getopt( argv[ 1: ], "hv", [ "help" ] )
		except getopt.error, msg:
			raise Usage( msg )

		for option, value in opts:
			if option == "-v":
				log.verbose = True
			if option in ( "-h", "--help" ):
				raise Usage( '' )
			if option in ( "-o", "--output" ):
				output = value

		wf = Webfaction()

		try:
			login = re.match( '^([^\:]+)\:([^&@]+)(?:@([^&]+))?$', args[ 0 ] )
			wf.login( login.group( 1 ), login.group( 2 ), login.group( 3 ) )
			args = args[ 1: ]
		except IndexError, msg:
			raise Usage( 'Username and password are not specified correctly: username:password' )
		except AttributeError, msg:
			raise Usage( 'Username and password are not specified correctly: username:password' )

		log.say( 'Logged in as: {0}'.format( wf.account[ 'username' ] ) )

		if not len( args ):
			raise Usage( 'No actions specified' )

		current_action = ''
		for action in args:
			if action == 'create_dns_override':
				current_action = action
			elif current_action == 'create_dns_override':
				try:
					domain = re.match( '^([^$@]+)(?:@([^$]+))?$', action )
					domain, ip = wf.create_dns_override( domain.group( 1 ), domain.group( 2 ) )
					log.say( 'Created dns override for domain: {0} with ip: {1}'.format( domain, ip ) )
				except AttributeError, msg:
					raise Usage( 'Domain not specified correctly: domain[@ip]' )
			else:
				raise Usage( 'Unknown action: {0}'.format( action ) )

	except WError, err:
		log.err( err.err )
		print >> sys.stdout, "For help use --help"
		return 2
	except Usage, err:
		log.err( err.err )
		print >> sys.stdout, err.msg
		return 2

if __name__ == "__main__":
	sys.exit( main() )
