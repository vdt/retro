#!/usr/bin/env python
# Encoding: iso-8859-1
# vim: tw=80 ts=4 sw=4 noet
# -----------------------------------------------------------------------------
# Project   : Railways - Declarative Python Web Framework
# -----------------------------------------------------------------------------
# Author    : Sebastien Pierre                               <sebastien@ivy.fr>
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Creation  : 12-Apr-2006
# Last mod  : 21-Feb-2008
# -----------------------------------------------------------------------------

import os, sys, time, webbrowser
from os.path import abspath, dirname, join
from railways import *
from railways.wsgi import SERVER_ERROR_CSS

# ------------------------------------------------------------------------------
#
# PROXY COMPONENT
#
# ------------------------------------------------------------------------------

class Proxy(Component):
	"""This is the main component of the Proxy. It basically provided a wrapper
	around the 'curl' command line application that allows basic proxying of
	requests, and serving of local files."""

	def __init__( self, proxyTo, prefix="/" ):
		# TODO: Add headers processing here
		"""Creates a new proxy that will proxy to the URL indicated by
		'proxyTo'."""
		Component.__init__(self, name="Proxy")
		self._proxyTo = proxyTo
		self.PREFIX   = prefix

	def start( self ):
		"""Starts the component, checking if the 'curl' utility is available."""
		if not self.hasCurl():
			raise Exception("Curl is required.")

	@on(GET="/{rest:rest}?{parameters}", priority="10")
	def proxyGet( self, request, rest, parameters ):
		uri = request.uri() ; i = uri.find(rest) ; assert i >= 0 ; uri = uri[i:]
		result, ctype, code = self._curl(self._proxyTo, "GET", uri)
		# TODO: Add headers processing here
		return request.respond(content=result,headers=[("Content-Type",ctype)],status=code)

	@on(POST="/{rest:rest}", priority="10")
	def proxyPost( self, request, rest ):
		uri = request.uri() ; i = uri.find(rest) ; assert i >= 0 ; uri = uri[i:]
		result, ctype, code = self._curl(self._proxyTo, "POST", uri, body=request.body())
		# TODO: Add headers processing here
		return request.respond(content=result,headers=[("Content-Type",ctype)],status=code)

	# CURL WRAPPER
	# ____________________________________________________________________________

	def hasCurl( self ):
		"""Tells if the 'curl' command-line utility is avialable."""
		result = os.popen("curl --version").read() or ""
		return result.startswith("curl") and result.find("http") != -1

	def _curl( self, server, method, url, body="" ):
		"""This function uses os.popen to communicate with the 'curl'
		command-line client and to GET or POST requests to the given server."""
		if method == "GET":
			command = "curl -s -w '\n\n%{content_type}\n\n%{http_code}'" + " '%s/%s'" % (server, url)
			result = os.popen(command).read()
		else:
			command = "curl -s -w '\n\n%{content_type}\n\n%{http_code}'" + " '%s/%s' -d '%s'" % (server, url, body)
			result = os.popen(command).read()
		code_start  = result.rfind("\n\n")
		code        = result[code_start+2:]
		result      = result[:code_start]
		ctype_start = result.rfind("\n\n")
		ctype       = result[ctype_start+2:]
		result      = result[:ctype_start]
		return result, ctype, code

# ------------------------------------------------------------------------------
#
# MAIN
#
# ------------------------------------------------------------------------------


def run( args ):
	if type(args) not in (type([]), type(())): args = [args]
	from optparse import OptionParser
	# We create the parse and register the options
	oparser = OptionParser(version="Railways[+proxy]")
	oparser.add_option("-p", "--port", action="store", dest="port",
		help=OPT_PORT, default="8000")
	oparser.add_option("-f", "--files", action="store_true", dest="files",
		help="Server local files", default=None)
	# We parse the options and arguments
	options, args = oparser.parse_args(args=args)
	print options, args
	if len(args) == 0:
		print "The URL to proxy is expected as first argument"
		return False
	if len(args) == 2:
		prefix = args[1]
	else:
		prefix = "/"
	components = [Proxy(args[0], prefix)]
	if options.files:
		import railways.contrib.localfiles
		components.append(railways.contrib.localfiles.LocalFiles())
	app    = Application(components=components)
	import railways
	return railways.run(app=app,sessions=False,port=int(options.port))

# -----------------------------------------------------------------------------
#
# Main
#
# -----------------------------------------------------------------------------

if __name__ == "__main__":
	run(sys.argv[1:])

# EOF
