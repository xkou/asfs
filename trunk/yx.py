

from libyx import YX
from twisted.internet import reactor, defer

yx = YX()


def call_fight():
	r = yx.monster_fight( 17 )
	if 'success' not in r:
		print  r['script_text'],r['result']

	reactor.callLater( 5, call_fight )

def call_keep():
	yx.refresh_npc( )
	reactor.callLater( 15, call_fight )

call_fight ()


reactor.run( )

