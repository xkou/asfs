from libsg import SG
import math

sg = None
if __name__ == "__main__": sg = SG()
import sqlite3 

class MapInfo:
	
	def __init__(self):
		self.conn = sqlite3.connect("map.sqlite")
		self.cursor = self.conn.cursor()
	
	def insert(self, type, pos, x, y, distance ):
		row = self.getinfo(pos)
		if row :
			if row[0]!= type:
				print "update", pos, type
				self.cursor.execute("update npc set type = %d where pos=%d" % (type, pos) )
			return
		self.cursor.execute("insert into npc ( type, pos, x,y, distance, status ) values (%d,%d,%d,%d,%f,%d)" % (type, pos, x,y, distance, 0 ))
		self.conn.commit()
	
	def getinfo(self, pos ):
		self.cursor.execute("select type,distance from  npc where pos = %d " % pos )
		row = self.cursor.fetchone()
		return row
	
	def getbest(self):
		self.cursor.execute("select type, pos , distance from npc where type in (1,2) order by distance limit 10" )
		rows = self.cursor.fetchall()
		return rows
	
	def remove( self, pos ):
		self.cursor.execute("delete from npc where pos = %d " % pos )
		self.conn.commit()
	
	def findall(self, ts = [1,2] ):
		n = 80
		for x  in range(-n, n, 8 ):
			for y in range( -n, n, 8 ):
				npcs = sg.lookup_xy( x, y)['npc_tent']
				for npc in npcs:
					a,b = sg.calc_xy(npc[2])
					if  npc[1] in ts:
						self.insert( npc[1], npc[2], a, b, math.sqrt(a**2 + b**2) )
					print npc, a, b ,"distans:" ,math.sqrt(a**2 + b**2)

import os,time
def getmapinfo(s = None):
	global sg
	if sg == None: sg = s
	fn = "lasttime"
	print "start get map info "
	if not os.path.exists(fn): 
		open(fn,"wb").write("0")
	lasttime = int(open(fn).read())
	if time.time() - lasttime > 600:
		m = MapInfo()
		print m.findall( )
	
		open(fn,"wb").write(str(time.time()))
	print "end get map info."
if __name__ == "__main__":
	getmapinfo()