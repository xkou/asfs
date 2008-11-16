#! coding:utf-8
from twisted.internet import reactor, defer
from twisted.internet import threads
from libsg import SG, tostr
import random, time
import functools
from smtplib import SMTP
from email.mime.text import MIMEText
import random


cities = [116399,125463,145742,57747]
tids = [ -40050 , -34034 , -50256, -50278, -51019, -51071]

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

def call_buy_resource( num = 5, low=50000):
	res = sg.get_resouce_number( )
	def check( name, id ):
		if res[name] < low - 12 * (res["-"+name] if res["-"+name]<0 else 0) :
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
	techlist= [29] #,13,12,15 #,1,4,3,2,
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


def call_yz_update_building( pids ):
	tasklist = sg.get_current_update()
	bs = sg.get_all_building()
	l  = len( tasklist )
	m = 5
	if l: m = min( tasklist.values() )
	if l == 3:
		
		print sg.tname, tasklist
		return m
	bs = filter( lambda x: x[1] not in tasklist.keys(), bs )
	bs = filter( lambda x: x[1] in pids, bs )
	bs.sort( key = lambda x:x[3] )
	for obj in bs:
		ret = sg.update_building( obj[1], obj[0] )
		print sg.tname, "升级", tostr(obj[2]), obj[1], "级别:", obj[3], ret['ret'] == 0
		if ret['ret'] == 0:
			break
	else:
		print sg.tname,"营寨无法升级成功任何建筑"
		return m if l else 300
	
	return 5

def call_update_res_number():
	sg.update_self_res()
	return 60


def call_update_building( gid ):
	tasklist = sg.get_current_update()
	bs = sg.get_all_building()
	l = len(tasklist)
	ts = tasklist.values()
	m = 0
	if l: m = min(ts)
	if l >= 3:
		
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
		t = m if m > 0 and m < 300 else 300
		print  sg.cname, "无法升级成功任何建筑",t,"秒后重试"
		return t
	
	return 5
	

call_update_hourse = functools.partial( call_update_building, gid = 3)
call_update_store = functools.partial( call_update_building, gid = 4)
call_update_rest =  functools.partial( call_update_building, gid = 8)
call_update_base =  functools.partial( call_update_building, gid = 1)	
call_update_wall =  functools.partial( call_update_building, gid = 2)
call_update_all =  functools.partial( call_update_building, gid = 0)

call_func_error_no = 0
def call_func( func, cid, *args, **awk ):
	global call_func_error_no
	try:
		sg.change_city( cid )
		r = func( *args, **awk )
		call_func_error_no = 0
	except Exception , err:
		print func, sg.cid, args ,err
		call_func_error_no += 1
		if call_func_error_no > 100 : threads.deferToThread( sendemail, "连接出错.." )
		reactor.callLater( 10, call_func, func, cid, *args, **awk )
		return
	reactor.callLater( r, call_func, func, cid, *args, **awk )
	
def call_func2( func, cid, *args ):
	try:
		sg.change_city( cid )
		r = func( *args )
	except Exception , err:
		print func, sg.tid, args ,err
		reactor.callLater( 10, call_func2, func, cid, *args )
		return
	reactor.callLater( r, call_func2, func, cid,  *args )


def call_make_new_weapon( btype, wtype, wtype2, speed = None ):
	n = 6
	
	c = sg.get_build( btype )
	
	
	if len(c) >= 2:
		ts = [ x[3] for x in c ]
		return min(ts)
	if len(c) == 1:
		if( c[0][0] == wtype ):
			sg.make( n, wtype2, speed )
		else:
			sg.make( n, wtype, speed )
		return c[0][3]
	
	sg.make( n, wtype,speed )
	return 20

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
		threads.deferToThread( sendemail, "找到名将 " + tostr(w[3]) )
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

def check_skill_point():
#    {"ret":0,"head_img":4006,"name":"冯超","histroy_name":"","type":2,"job":0,"partner_id":364837,"partner_name":"关敦川","status":24,"city_tent_id":116399,"level":66,"exp":3314,"update_exp":3620,"loyalty":66,"hp":760,"hp_max":760,"strength":74,"agility":116,"captain":43,"salary":660,"heal_left":0,"skill_point":12,"hpmax_add1":0,"attrib_add1":0,"attrib_add2":0,"attrib_add3":0}
#	  {"ret":0,"head_img":4000,"name":"关敦川","histroy_name":"","type":1,"job":3,"partner_id":364214,"partner_name":"冯超","status":24,"city_tent_id":116399,"level":66,"exp":3273,"update_exp":3620,"loyalty":63,"hp":760,"hp_max":760,"charm":47,"brain":115,"manage":68,"salary":660,"heal_left":0,"skill_point":12,"hpmax_add1":0,"attrib_add1":0,"attrib_add2":6,"attrib_add3":0}
	def addpt( l, props ):
		addpt1 = l['skill_point']
		addpt2 = 0
		if addpt1 == 0: return
		prodict = {}
		for p in props:
			prodict[p] = l[p]
		newlist = sorted( prodict.items(), key = lambda x:x[1])
		d1 = newlist[2][0]
		d2 = newlist[1][0]
		d3 = newlist[0][0]
		
		for pt in range( l['skill_point'] ):
			if l[d1]+addpt1 > l[d2]+addpt2 + l[d3]:
				addpt1 -= 1
				addpt2 += 1
			else:
				break
		print sg.cname, tostr(l['name']), l['skill_point'] ,newlist
		print sg.cname, tostr(l['name']), "点数", addpt1, addpt2
		sg.add_point( l['id'], newlist[1][0], addpt2   )
		sg.add_point( l['id'], newlist[2][0], addpt1   )
		
		return 900
		# add point

		
	ls = sg.get_all_gen()['generals']
	for l in ls:
		info = sg.get_gen_detail( l[0] )
		info['id'] = l[0]
		if info['type'] == 1:
			addpt( info, [ "charm","brain","manage" ] )
		else:
			addpt( info , [ "strength","agility","captain"] )
	
	return 900

def call_many( fun, ls , *args, **awk ):
	for l in  ls:
		call_func( fun, cities[l], * args, **awk )

def call_check_yz_res( dest, food = 50000, stone=50000, iron=50000,wood=50000, num = 10000, timeout=200 ):
	res = sg.get_res_number(dest)
	for e in res:
		if res[e] < eval(e):
			cmd = "sg.do_trans( dest, %s=%d )" % (e, num)
			eval(cmd)
	return timeout

def call_trans_res( dest,  stone=0, wood=0, iron = 0, food = 0 ):
	info = sg.get_trader_info()
	
	n = (stone+wood+iron+food)/10000
	
	if info['trader'] > n:
		sg.do_trans( dest, stone = stone, wood=wood, iron=iron, food=food )
		return 30*60
	
	if info['back']:
		gt = info['back']
		gt.sort( key = lambda x:x[12] )
		return gt[0][12]
	
	
	if info['goto']:
		gt = info['goto']
		gt.sort( key = lambda x:x[12] )
		return gt[0][12]
	
	return 60


def call_do_task( tid, gs ):
	at = 900

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
		return t
	
	infos = sg.get_soldier_info()
	infos = filter( lambda x:x[1] in gs, infos )
	infos = filter( lambda x:x[7] < 100, infos )
	ns = filter( lambda x:x[8] != -1 and x[7] > 89, infos )
	if len(ns) == len(infos) and len(ns)!=0:
		infos.sort( cmp = lambda x,y : cmp(y[8], x[8]) )
		if infos[0][8] < at:
			sg.do_task( tid, gs )
			return 5
	if len(infos) == 0 :
		sg.do_task( tid, gs )
		return 5
	
	n = call_up_shiqi( gs )
	if n > at: return n -at 
	return 10

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
		print sg.cname, "提升士气", tostr(inf[2]),r['ret'] == 0
	if len(ls) == 0:
		if len( filter( lambda x:x[7] < 90 , infos ) ) == 0:
			infos.sort( cmp = lambda x,y : cmp(y[8],x[8]))
			return  infos[0][8]
				
		infos.sort( cmp = lambda x,y : cmp(x[8],y[8]))
		return infos[0][8]
	return 5


def call_beat_city( target ):
	ts = sg.get_max_time()
	ts.sort( key = lambda x: x[1] )
	if ts[-1][1] != 0: return ts[-1][1]
	if len( sg.get_useable_gens() ) == 0 : return 20
	sg.do_beat_city( target )
	return 5

def call_check_giving( dest, supid, count ):
	sg.set_giving( dest, count, supid )
	return 60

def main():
	
#	call_func( call_beat_city, tids[3] , 13 )

	#call_make_weapon()
#	call_func( call_yz_update_building, tids[0], [0] )
#	call_func( call_yz_update_building, tids[1], [0] )
#	call_func( call_yz_update_building, tids[2], [0] )
#	call_func( call_yz_update_building, tids[3], [0] )
#	call_func( call_yz_update_building, tids[4], [2,0,1] )
#	call_func( call_yz_update_building, tids[5], [2,0,1] )

# 营寨
	call_func( call_build_wall, tids[0] )
	call_func( call_build_wall, tids[2] )
	call_func( call_build_wall, tids[3] )
	call_func( call_build_wall, tids[1] )
	call_func( call_build_wall, tids[4] )
	call_func( call_build_wall, tids[5] )
	
	call_func( check_skill_point, tids[0] )
	call_func( check_skill_point, tids[2] )
	call_func( check_skill_point, tids[3] )
	call_func( check_skill_point, tids[1] )
	call_func( check_skill_point, tids[4] )
	call_func( check_skill_point, tids[5] )
	
#	call_func( call_check_yz_res, cities[0], tids[0], wood= 400000, stone = 400000, iron = 150000 )
#	call_func( call_check_yz_res, cities[0], tids[1], wood= 400000, stone = 400000, iron = 150000 )
#	call_func( call_check_yz_res, cities[0], tids[3], wood= 400000, stone = 400000, iron = 150000 , food = 150000 )
# 主城	
	call_func( call_get_newb_general, cities[0], 7 )
	call_func( call_get_newb_general, cities[0], 8 )

	
	
	call_many( check_general, (0,1,2) )
	call_func( call_update_tech, cities[0] )
	call_func( call_buy_resource, cities[0], 15 )
#	call_func( call_build_wall, cities[0] )
	call_func( call_update_hourse, cities[0] )
	call_func( call_make_new_weapon, cities[0], 13,  205, 105, 1 )
	call_func( call_make_new_weapon, cities[0], 14,  305, 305, 1 )
	call_func( call_make_new_weapon, cities[0], 15,  501, 501, 1 )
#	call_func( call_sell_weapon,     cities[0], ( 207,306,406 ) )
	call_func( check_minxin, cities[0] )
#	call_func( call_do_task, cities[0], 1 ,[ 	326572, 	363930] )
	call_func( call_do_task, cities[0], 1, [363930,364214 ,326572 ] )

	call_func( check_skill_point, cities[0])
#	call_func( call_up_shiqi, cities[0], [ 363930, 326572,364214,442487,442097 ] )
	
# 新城	
#	call_func( call_check_yz_res, cities[1], tids[2], wood= 400000, stone = 150000, iron = 150000 )
#	call_func( call_check_yz_res, cities[1], tids[4], wood= 200000, stone = 150000, iron = 50000, food = 30000 )
	call_func( call_buy_resource, cities[1], 10, low = 10000 )
	call_func( call_make_new_weapon, cities[1], 13,  205, 105,2 )
	call_func( call_make_new_weapon, cities[1], 14,  305, 305,2 )
	call_func( call_make_new_weapon, cities[1], 15,  405, 405,2 )
	call_func( call_update_hourse, cities[1] )
#	call_func( call_update_wall, cities[1] )
#	call_func( call_update_all, cities[1] )
	call_func( call_build_wall, cities[1] )
	call_func( check_minxin, cities[1] )
	call_func( check_skill_point, cities[1])

#	call_func( call_sell_weapon,  cities[1], (205,305,405) )
#	call_func( call_sell_weapon,  cities[0], (206,306,406) )
	
#新城2
	call_func( call_make_new_weapon, cities[2], 13,  103, 103, 1 )
	call_func( call_sell_weapon,  cities[2], (103,) )
	call_func( call_buy_resource, cities[2], 2 ) 
	call_func( call_update_store, cities[2] )
	call_func( call_update_base, cities[2] )
	call_func( call_update_wall, cities[2] )
	call_func( call_build_wall, cities[2] )
	call_func( check_minxin, cities[2] )
	call_func( check_skill_point, cities[2])

#	call_func( call_update_base, cities[0] )
#	call_func( call_update_wall, cities[0] )
#	call_func( call_update_store, cities[2] )
#	call_func( call_update_store, cities[1] )

# 谁与争锋	
	call_func( call_build_wall, cities[3] )
	call_func( call_buy_resource, cities[3], 10 )
	call_func( call_update_base, cities[3]  )
	call_func( check_skill_point, cities[3])
	call_func( check_minxin, cities[3] )
	call_func( call_update_hourse, cities[3] )
#	call_func( call_check_yz_res, cities[3], tids[5], wood= 50000, stone = 50000, iron = 50000, food = 50000 )

	#call_update_tech()
	#call_update_build()

if __name__ == "__main__":
	#print check_minxin()
	print sg.change_city( tids[0] )
	#call_make_new_weapon( 13, 103,103)
	#call_do_task(1, [363930,364214,326572])
	#print check_general()
	#check_skill_point()
	#call_func( call_make_new_weapon, cities[1], 13,  205, 105,2 )
	main()
	#print call_make_new_weapon(13, 205, 105 )

	

reactor.run()

