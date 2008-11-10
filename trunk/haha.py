#! coding:utf-8
from twisted.internet import reactor, defer
from twisted.internet import threads
from libsg import SG, tostr
import random, time
import functools
from smtplib import SMTP
from email.mime.text import MIMEText
import random


cities = [116399,125463,145742]

def sendemail( content ):
	f = '"三国" <hk888@163.com>'
	t = 'netmud@gmail.com'
	smtp = SMTP()
	smtp.connect('smtp.163.com')
	smtp.login("hk888","3281044")

	msg = MIMEText(content)
	msg['subject']='三国之兵临城下'
	msg['Content-Type']= 'text/plain; charset="gbk"'
	msg['From'] = f

	smtp.sendmail( f,t, msg.as_string( ) )
	

sg = SG(116399)
sg._speed = 2
print sg.change_city( 116399 )
def call_make_weapon():
	global sg
	num = 2
	reactor.callLater( 10,call_make_weapon)
	
	def check(wtype, gid, pid, tab ):
		if len(sg.get_build(gid, pid, tab)) <= 1:
			r = sg.make(num, wtype)
			if r['ret']:
				print "制造失败",wtype
	
	# 野行马
	check(406,15,19,1)
	
	# 明光战甲
	check(306,14,24,1)
	
	# 宝雕弓
	check(206,13,12,1)
	
def call_sell_weapon( ws =(206,306,406) ):
	
	num = 4
	rest = 1
	info = sg.get_market_info()
	for e in info:
		e = info[e]
		if e[0] not in ws:continue
		if e[2] > num:
			sellcount = e[2]-rest
			if sg.sell(sellcount, e[0] , e[3] )['ret'] != 0:
				print "卖出",tostr(e[1]), sellcount,"件, 失败"

	
	return 20

def call_buy_resource( num = 3):
	res = sg.get_resouce_number()
	low = 30000
	def check( name, id ):
		if res[name]< low:
			print sg.cname, "买入", name
			sg.buy(num, id)

	check("stone", SG._stone )
	check("food", SG._food )
	check("iron", SG._iron )
	check("wood", SG._wood )
	
	tasklist = sg.get_current_update()
	print  time.asctime(), sg.cname, ", 铜钱:", sg.get_money_number(),"当前任务数:",len(tasklist)

	return random.randint(30, 60)



top_level = 20

def call_update_tech():
	global top_level
	
	ret = sg.get_current_update_tech()
	if ret:
		print "当前研究:", tostr(ret[1]), "级别:", ret[2], "剩余时间:", ret[4]
		return ret[4]
	techlist=range(16,30) #,13,12,15 #,1,4,3,2,
	alltech = sg.get_all_tech()['list']
	alltech = filter( lambda x: x[0] in techlist, alltech)
	alltech = filter( lambda x: x[2] < top_level, alltech)
	alltech.sort( cmp = lambda x,y: cmp( x[2] , y[2] ) )
	for tech in alltech:
		r = sg.update_tech( tech[0] )['ret']
		print "升级科技", tostr(tech[1]), r == 0
		if r==0:
			return 5
	else:
		print "所有科技升级完成"
	return 611


def call_update_building( gid ):
	tasklist = sg.get_current_update()
	bs = sg.get_all_building()

	if len(tasklist) >= 3:
		ts = tasklist.values()
		m = min(ts)
		print sg.cname
		for e in tasklist:print "\t", sg.get_building_name( e ),"级别:", filter( lambda x:x[1] == e , bs )[0][3], "剩余时间:", tasklist[e]
		print sg.cname, m, "秒后重试"
		return m
	
	bs = filter( lambda x: x[0] != 5, bs )
	if gid : bs = filter( lambda x: x[0]==gid, bs )
	bs = filter( lambda x: x[1] not in tasklist.keys(), bs )
	
	bs.sort( cmp = lambda x,y : cmp(x[3], y[3]) )
	for obj in bs:
		ret = sg.force_update_building( obj[1] )
		print sg.cname, "升级", tostr(obj[2]), obj[1], "级别:", obj[3], ret['ret'] == 0
		if ret['ret'] == 0:
			break
	else:
		print "无法升级成功任何建筑"
		return 600
	
	return 5
	

call_update_hourse = functools.partial( call_update_building, gid = 3)
call_update_store = functools.partial( call_update_building, gid = 4)
call_update_rest =  functools.partial( call_update_building, gid = 8)
call_update_base =  functools.partial( call_update_building, gid = 1)	
call_update_wall =  functools.partial( call_update_building, gid = 2)
call_update_all =  functools.partial( call_update_building, gid = 0)

def call_func( func, cid,  *args ):
	try:
		sg.change_city( cid )
		r = func( *args )
	except Exception , err:
		print func, sg.cid, args ,err
		reactor.callLater( 10, call_func, func, cid, *args )
		return
	reactor.callLater( r, call_func, func, cid, *args )
	

def call_make_new_weapon( btype, wtype, wtype2 ):
	n = 6
	c = sg.get_build( btype )
	if len(c) == 2:
		ts = [ x[3] for x in c ]
		return min(ts)
	if len(c) == 1:
		if( c[0][0] == wtype ):
			sg.make( n, wtype2 )
		else:
			sg.make( n, wtype )
		return c[0][3]
	
	sg.make( n, wtype )
	return 5

def check_minxin():
	v = sg.get_minyuan()
	if v:
		r = sg.pre_anfu()
		if r['left']:
			print sg.cname, "需要安抚",r['left'],"秒后重试"
			return r['left']
		else:
			sg.buy( r['population'] * 3 /1000, SG._food )
			sg.anfu()
	return 315
	
def call_get_newb_general( tid ):# 7,8
	global sg
	r = sg.find_gen( tid )
	if r['look_for']:
		pass
		#return 100
		#return r['look_for'][0][6]
	w = r['rumor']
	if len(w) == 0:
		ls = sg.get_wen_infos()
		ls = filter( lambda x:x[4] == 0, ls )
		ls.sort( cmp = lambda x,y: cmp( y[11],x[11] ) )
		gen = ls[0]
		if gen[3] != 1:
			print sg.cname, "任命", tostr(gen[1]) ,"为太守"
			sg.give_job( gen[0], 1 )
	else:
		threads.deferToThread( sendemail, "找到名将 " + tostr(`w`) )
		sg.dofind(w[0])
	return 125

def call_build_wall( ):
	i = sg.get_wall_info()
	c = i['current']
	if len(c) >=2:
		ts = [ x[3] for x in c ]
		return min(ts)
	
	ls = i['list']
	nums = [ x[2] for x in ls ]
	ls = filter( lambda x:x[2] == min(nums), ls )
	if sg.make_wall(2, ls[0][0])['ret'] == 0:
		return 10
	else:
		v = sg.get_wall_value()
		if  v[3] >= v[4] : return 600
		return 30

def check_general():
	all = filter( lambda x:x[6] < 60 , sg.get_wu_infos() +  sg.get_wen_infos() )
	for g in all:
		print sg.cname, "犒赏", tostr(g[1]) , sg.give_money( g[0], g[12] *10)['ret'] == 0
	
	return 1200
	

def call_many( fun, ls , *args ):
	for l in  ls:
		call_func( fun, cities[l], * args )


def call_do_task( tid, gs ):
	tinfo = sg.task_info()
	s = tinfo['status']
	t = tinfo['current'][1]
	if s == 1:
		print "任务正在进行中", t,"秒后重试"
	elif s == 2:
		print "任务正在战斗", t,"秒后重试"
	elif s == 3:
		print "任务完成，正在返回", t,"秒后重试"
	
	if s != 0:
		return t+1
	
	infos = sg.get_soldier_info()
	infos = filter( lambda x:x[1] in gs, infos )
	infos = filter( lambda x:x[7] < 100, infos )
	ns = filter( lambda x:x[8] != -1 and x[7] > 89, infos )
	if len(ns) == len(infos) and len(ns)!=0:
		infos.sort( cmp = lambda x,y : cmp(y[8], x[8]) )
		if infos[0][8] < 899:
			sg.do_task( tid, gs )
			return 5
	if len(infos) == 0 :
		sg.do_task( tid, gs )
		return 5
	
	n = call_up_shiqi( gs )
	return n

def call_up_shiqi( gs ):
	t = 898
	infos = sg.get_soldier_info()
	infos = filter( lambda x:x[1] in gs, infos )
	infos = filter( lambda x:x[7] < 100, infos )
	if len(infos) == 0:
		return 100
	
	ls = filter( lambda x:x[8] == -1, infos )
	for inf in ls:
		sg.buy( sum(inf[3:6])*5/1000+3, SG._food )
		r = sg.update_shiqi( inf[1], 100-inf[7] )
		print sg.cname, "提升土气", tostr(inf[2]),r['ret'] == 0
	if len(ls) == 0:
		if len( filter( lambda x:x[7] < 90 , infos ) ) == 0:
			infos.sort( cmp = lambda x,y : cmp(y[8],x[8]))
			return 5 if infos[0][8]< t else infos[0][8]-t
				
		infos.sort( cmp = lambda x,y : cmp(x[8],y[8]))
		return infos[0][8]
	return 5


def main():
	

	#call_make_weapon()
	
	call_func( call_get_newb_general, cities[0], 7 )
	call_func( call_get_newb_general, cities[0], 8 )


	call_many( check_general, (0,1,2) )
	call_func( call_update_tech, cities[0] )
	call_func( call_buy_resource, cities[0], 15 )
#	call_func( call_build_wall, cities[0] )
	call_func( call_update_hourse, cities[0] )
	call_func( call_make_new_weapon, cities[0], 13,  205, 105 )#
	call_func( call_make_new_weapon, cities[0], 14,  305, 305 )
	call_func( call_make_new_weapon, cities[0], 15,  405, 405 )
	call_func( check_minxin, cities[0] )
	call_func( call_do_task, cities[0], 1, [363930,364214,326572] )


	call_func( call_buy_resource, cities[1], 10 )
	call_func( call_make_new_weapon, cities[1], 13,  205, 105 )
	call_func( call_make_new_weapon, cities[1], 14,  305, 305 )
	call_func( call_make_new_weapon, cities[1], 15,  405, 405 )
	call_func( call_update_hourse, cities[1] )
#	call_func( call_build_wall, cities[1] )
	call_func( check_minxin, cities[1] )

#	call_func( call_sell_weapon,  cities[1], (205,305,405) )
#	call_func( call_sell_weapon,  cities[0], (206,306,406) )
	
	
#	call_func( call_update_all, cities[2] )
#	call_func( call_make_new_weapon, cities[2], 13,  103, 103 )
#	call_func( call_sell_weapon,  cities[2], (103,) )
	call_func( call_buy_resource, cities[2] )
#	call_func( call_build_wall, cities[2] )
	call_func( check_minxin, cities[2] )

#	call_func( call_update_base, cities[0] )
#	call_func( call_update_wall, cities[0] )
#	call_func( call_update_store, cities[2] )
#	call_func( call_update_store, cities[1] )

	
	
	

	#call_update_tech()
	#call_update_build()

if __name__ == "__main__":
	#print check_minxin()
	print sg.change_city( cities[0] )
	#call_make_new_weapon( 13, 103,103)
	#call_do_task(1, [363930,364214,326572])
	#print check_general()
	#print call_up_shiqi(  )
	main()
	#print call_make_new_weapon(13, 205, 105 )

	

reactor.run()

