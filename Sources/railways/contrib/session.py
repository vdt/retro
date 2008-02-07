#!/usr/bin/env python
# Encoding: iso-8859-1
# vim: tw=80 ts=4 sw=4 noet
# -----------------------------------------------------------------------------
# Project   : Railways - Declarative Python Web Framework
# -----------------------------------------------------------------------------
# Author    : Sebastien Pierre                               <sebastien@ivy.fr>
# License   : Revised BSD License
# -----------------------------------------------------------------------------
# Creation  : 19-Dec-2007
# Last mod  : 19-Dec-2007
# -----------------------------------------------------------------------------

from railways import predicate

# ------------------------------------------------------------------------------
#
# AUTHENTICATED ASPECT
#
# ------------------------------------------------------------------------------

class Authenticated:
	"""Defines an 'isAuthenticated' method that can be used as a '@predicate' in
	Railways components.
	
	Authentification works with an integer that qualifies the user rights."""

	NOT_AUTHENTICATED = 0
	LOGGED_IN         = 1
	ADMIN             = 65000
	@predicate
	def isAuthenticated( self, request, level=1 ):
		return request.session("authenticated") 

	def setAuthentication( self, request, state=1 ):
		request.session("authenticated", state)

# EOF
