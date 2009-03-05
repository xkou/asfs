#! coding:utf-8
import urllib2, time, random, urllib, re
import httplib as httplib
import json
import socket, math


class YX:
	
	def __init__(self, name = "yx" ):
		socket.setdefaulttimeout(20)
		self.conn = None
		self.get_new_http()
		self.headers = {}
		self.cookie=open("cookie-" + name,"rb").read()
		self.headers['Content-Type']="application/x-www-form-urlencoded; charset=UTF-8"
		self.headers['Referer'] = "http://yingxiongsvr23.webgame.xunlei.com"
		self.headers['X-Requested-With'] = "XMLHttpRequest"
		self.headers['X-Prototype-Version'] = "1.5.0"
		self.headers['User-Agent']="Mozilla/5.0 (Windows; U; Windows NT 5.2; zh-CN; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"
		self.headers['Cookie'] = self.cookie

	def get_new_http(self):
		if self.conn:
			self.conn.close()
			del self.conn
		self.conn = httplib.HTTPConnection("yingxiongsvr23.webgame.xunlei.com:80")
	
	def geturl(self, url ):
		return "http://yingxiongsvr23.webgame.xunlei.com" + url + "&timeStamp=1236233710689&callback_func_name=callbackFnChkDetail"
	
	def send(self, url, m ="GET", data ="" ):
		self.conn.request(m, self.geturl(url), headers= self.headers, body = data)
		try:
			response = self.conn.getresponse()
		except:
			self.get_new_http()
		
		ret = response.read()
		try:
			ret = json.read(ret)
		except:
			print "Json error:", ret
		return ret
	
	def post(self, url, data ):
		return send( url, "POST", data )
	
	def refresh_npc(self):
		return self.send("/modules/refresh_npc_barrier.php?instance=0&time=10")
	
	def monster_fight(self, mid ):
		return self.send("/modules/monster_fight.php?mid=%d" % mid)
	
	def buy( self, url , t = 1, num = 100000 ):
		return self.post("mirror_money_type=%d&select_life_pool=%d&select_mana_pool=%d" % ( t, num, num ) )

if __name__ == "__main__":
	yx = YX()
	r = yx.refresh_npc()
	
	for e  in  r['s_monster']:
		print e['type_name']

	r = yx.monster_fight()
	print r
		