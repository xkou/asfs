

from libyx import YX
from twisted.internet import reactor, defer

import  time
from traceback import print_exc
import functools

yx = YX()

import sys

argv = sys.argv

mid = 0
if len( argv ) ==2:
	mid = int(argv[1])

def call_fight():
	r = yx.monster_fight( mid )
	if 'success' not in r:
		print  r['script_text'],r['result']

	return 5

call_func_error_no = 0
def call_func( func,  *args, **awk ):
	global call_func_error_no
	try:
		r = func( *args, **awk )
		if r == -1: return
		call_func_error_no = 0
	except Exception, err:
		print func, args
		print_exc( )
		call_func_error_no += 1
		if call_func_error_no == 150 : reactor.stop()
		reactor.callLater( 10, call_func, func, *args, **awk )
		return
	reactor.callLater( r, call_func, func, *args, **awk )


def call_keep():
	yx.refresh_npc( )
	reactor.callLater( 15, call_fight )

def call_fight_people():
	us = yx.get_pk_user()
	u = us[0]
	if u[0] <= 15:
		r = yx.people_fight( u[1] )
		if "success" not in r:
			print r['result']
			return 60 
	return 30


#call_fight ()
#call_func( call_fight_people )
call_func( call_fight )


reactor.run( )

