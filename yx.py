

from libyx import YX
from twisted.internet import reactor, defer

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

	reactor.callLater( 5, call_fight )

def call_keep():
	yx.refresh_npc( )
	reactor.callLater( 15, call_fight )
def call_fight_people():
	r = yx.people_fight(22749)
	if "success" not in r:
		print r['result']
	reactor.callLater( 30, call_fight )


call_fight ()
call_fight_people()



reactor.run( )

