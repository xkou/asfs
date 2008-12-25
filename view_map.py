from libsg import SG
import math

sg = SG()

# 1619809, 1619808  y: +1 
# 1618496 x: +1

# 1621139 x:240 y:-578
#for x  in range(-2, 3 ):
#	for y in range( -2, 3 ):
#		print x,y, sg.calc_mid(x,y), sg.calc_xy(sg.calc_mid(x,y))


n = 70




print  "end"
		
def refresh_map():
	for x  in range(-n, n, 8 ):
		for y in range( -n, n, 8 ):
			npcs = sg.lookup_xy( x, y)['npc_tent']
			for npc in npcs:
				a,b = sg.calc_xy(npc[2])
				print npc, a, b ,"distans:" ,math.sqrt(a**2 + b**2)

import sqlite3 
def create_db():
	conn = sqlite3.connect("map.sqlite")
	c = conn.cursor()
	c.execute("create table npc ( type int, pos int, x int, y int, distance real, status int)")


if __name__ == "__main__":
	refresh_map()

