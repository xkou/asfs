#! coding:utf-8
from twisted.internet import reactor, defer
from twisted.internet import threads
from libsg import SG, tostr
import  time
import functools
from smtplib import SMTP
from email.mime.text import MIMEText
from random import randint


cities = [116399,125463,145742,57747,63829]
tids = [ -40050 , -34034 , -50256, -50278, -51019, -51071]

def sendemail( content ):
	f = '"����" <hk888@163.com>'
	t = 'netmud@gmail.com'
	smtp = SMTP()
	smtp.connect('smtp.163.com')
	smtp.login("hk888","3281044")

	msg = MIMEText(content)
	msg['subject']='����֮���ٳ���'
	msg.set_charset('gbk')
	msg['From'] = f

	smtp.sendmail( f,t, msg.as_string( ) )
	

sg = SG()

def call_make_weapon():
	global sg
	num = 2
	reactor.callLater( 10,call_make_weapon)
	
	def check(wtype, gid, pid, tab ):
		if len(sg.get_build(gid, pid, tab)) <= 1:
			r = sg.make(num, wtype)
			if r['ret']:
				print "����ʧ��",wtype
	
	# Ұ����
	check(406,15,19,1)
	
	# ����ս��
	check(306,14,24,1)
	
	# ����
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
				print "����",tostr(e[1]), sellcount,"��, ʧ��"

	
	return 20

def call_buy_resource( num = 5, low=50000):
	res = sg.get_resouce_number( )
	def check( name, id ):
		if res[name] < low - 12 * (res["-"+name] if res["-"+name]<0 else 0) :
			print sg.cname, "����", name
			sg.buy(num, id)

	check("stone", SG._stone )
	check("food", SG._food )
	check("iron", SG._iron )
	check("wood", SG._wood )
	
	tasklist = sg.get_current_update()
	m = sg.get_money_number()
	print  time.asctime(), sg.cname, ", ͭǮ:", m,"��ǰ������:",len(tasklist)

	return randint(30, 60)



top_level = 20

def call_update_tech():
	global top_level
	
	ret = sg.get_current_update_tech()
	if ret:
		print "��ǰ�о�:", tostr(ret[1]), "����:", ret[2], "ʣ��ʱ��:", ret[4]
		return ret[4]
	techlist=range(16,30) #,13,12,15 #,1,4,3,2,
	#techlist= [16,20,24] #,13,12,15 #,1,4,3,2,
	#techlist = [28]
	alltech = sg.get_all_tech()['list']
	alltech = filter( lambda x: x[0] in techlist, alltech)
	alltech = filter( lambda x: x[2] < top_level, alltech)
	alltech.sort( cmp = lambda x,y: cmp( x[2] , y[2] ) )
	for tech in alltech:
		r = sg.update_tech( tech[0] )['ret']
		print "�����Ƽ�", tostr(tech[1]), r == 0
		if r==0:
			return 5
	else:
		print "���пƼ��������"
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
		print sg.tname, "����", tostr(obj[2]), obj[1], "����:", obj[3], ret['ret'] == 0
		if ret['ret'] == 0:
			break
	else:
		print sg.tname,"Ӫկ�޷������ɹ��κν���"
		return m if l else 300
	
	return 5

def call_update_building2( gids = [] ):
	tasklist = sg.get_current_update()
	bs = sg.get_all_building()
	
	l = len( tasklist)
	ts = tasklist.values()
	print sg.cname
	for e in tasklist:print "\t", sg.get_building_name( e ),"����:", filter( lambda x:x[1] == e , bs )[0][3], "ʣ��ʱ��:", tasklist[e]
	if len(ts) == 3 : return min(ts)
	if gids: bs = filter( lambda x:x[0] in gids , bs )
	m = min(ts) if l else 0
	bdings = filter( lambda x:x[1] in tasklist.keys(), bs )
	bs = filter( lambda x:x[1] not in tasklist.keys(), bs )
	if len(bs) == 0 :
		print  sg.cname, "�޷������ɹ��κν���",min(ts),"�������"
		return min(ts)
	bs.sort( key = lambda x:x[3] )
	for obj in bs:
		ret = sg.force_update_building( obj[1] )
		print sg.cname, "����", tostr(obj[2]), obj[1], "����:", obj[3], ret['ret'] == 0
		if ret['ret'] == 0:
			return 5
	else:
		t = m if m > 0 and m < 300 else randint( 280, 320 )
		print  sg.cname, "�޷������ɹ��κν���",t,"�������"
		return t



def call_update_building( gid ):
	tasklist = sg.get_current_update()
	bs = sg.get_all_building()
	l = len(tasklist)
	ts = tasklist.values()
	m = 0
	if l:
		m = min(ts)
		print sg.cname
		for e in tasklist:print "\t", sg.get_building_name( e ),"����:", filter( lambda x:x[1] == e , bs )[0][3], "ʣ��ʱ��:", tasklist[e]
	if l >= 3:
		print sg.cname, m, "�������"
		return m
	
	bs = filter( lambda x: x[0] != 5, bs )
	if gid : bs = filter( lambda x: x[0]==gid, bs )
	bs = filter( lambda x: x[1] not in tasklist.keys(), bs )
	
	bs.sort( cmp = lambda x,y : cmp(x[3], y[3]) )
	for obj in bs:
		ret = sg.force_update_building( obj[1] )
		print sg.cname, "����", tostr(obj[2]), obj[1], "����:", obj[3], ret['ret'] == 0
		if ret['ret'] == 0:
			break
	else:
		t = m if m > 0 and m < 300 else randint( 280, 320 )
		print  sg.cname, "�޷������ɹ��κν���",t,"�������"
		return t
	
	return 5
	

call_update_hourse = functools.partial( call_update_building, gid = 3)
call_update_store = functools.partial( call_update_building, gid = 4)
call_update_rest =  functools.partial( call_update_building, gid = 8)
call_update_base =  functools.partial( call_update_building, gid = 1)	
call_update_wall =  functools.partial( call_update_building, gid = 2)
call_update_all =  functools.partial( call_update_building2, [2,4,3,1,13,6,15,11,14] )

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
		if call_func_error_no == 100 : threads.deferToThread( sendemail, "���ӳ���.." )
		if call_func_error_no == 150 : threads.deferToThread( sendemail, "���ӳ���.." )
		if call_func_error_no == 150 : reactor.stop()
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
			print sg.cname, "��Ҫ����",r['left'],"�������"
			return r['left']
		else:
			sg.buy( r['population'] * 3 /1000, SG._food )
			sg.anfu()
	return randint(315,400)
	
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
			print sg.cname, "����", tostr(gen[1]) ,"Ϊ̫��"
			sg.give_job( gen[0], 1 )
	else:
		threads.deferToThread( sendemail, "�ҵ����� " + tostr(w[3]) )
		sg.dofind(w[0])
	return randint(300,400)

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
		if  v[3]+1 >= v[4] : return randint(600,700)
		return 30

def check_general():
	all = filter( lambda x:x[6] < 60 , sg.get_wu_infos() +  sg.get_wen_infos() )
	for g in all:
		print sg.cname, "����", tostr(g[1]) , sg.give_money( g[0], g[12] *10)['ret'] == 0
	
	return 1200

def check_skill_point():
#    {"ret":0,"head_img":4006,"name":"�볬","histroy_name":"","type":2,"job":0,"partner_id":364837,"partner_name":"�ضش�","status":24,"city_tent_id":116399,"level":66,"exp":3314,"update_exp":3620,"loyalty":66,"hp":760,"hp_max":760,"strength":74,"agility":116,"captain":43,"salary":660,"heal_left":0,"skill_point":12,"hpmax_add1":0,"attrib_add1":0,"attrib_add2":0,"attrib_add3":0}
#	  {"ret":0,"head_img":4000,"name":"�ضش�","histroy_name":"","type":1,"job":3,"partner_id":364214,"partner_name":"�볬","status":24,"city_tent_id":116399,"level":66,"exp":3273,"update_exp":3620,"loyalty":63,"hp":760,"hp_max":760,"charm":47,"brain":115,"manage":68,"salary":660,"heal_left":0,"skill_point":12,"hpmax_add1":0,"attrib_add1":0,"attrib_add2":6,"attrib_add3":0}
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
		print sg.cname, tostr(l['name']), "����", addpt1, addpt2
		sg.add_point( l['id'], newlist[1][0], addpt2   )
		sg.add_point( l['id'], newlist[2][0], addpt1   )
		
		return randint( 800, 1000 )
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
	info = sg.get_trader_info()
	gotores = filter( lambda x: x[3] == dest, info['goto'] )
	res = sg.get_res_number(dest)
	del res['money']
	seqs = dict( food=6, wood=7,stone=8,iron=9 )
	for e in res:
		total = sum( [ x[seqs[e]] for x in gotores ] )
		if res[e] + total < eval(e):
			cmd = "sg.do_trans( dest, %s=%d )" % (e, num)
			eval(cmd)
	return timeout

def call_trans_res( dest,  stone=0, wood=0, iron = 0, food = 0, money = 0 ):
	info = sg.get_trader_info()
	
	n = (stone+wood+iron+food)/10000
	
	if info['trader'] > n:
		sg.do_trans( dest, stone = stone, wood=wood, iron=iron, food=food, money = money )
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
		print "�������ڽ�����", t,"�������"
	elif s == 2:
		print "��������ս��", t,"�������"
	elif s == 3:
		print "������ɣ����ڷ���", t,"�������"
	if s != 0:
		return t

	# ����
	n =[0,6000,500, 6000]
	infos = sg.get_generals_info()
	generals = infos['generals']
	for geninfo in generals:
		genid = geninfo[0]
		if genid not in gs: continue
		t1,t2,t3 = geninfo[4][0],geninfo[5][0],geninfo[6][0]
		isneed = 0
		for e in [1,2,3]:
			need = n[e] - eval("t%d" % e )
			
			if  need > 0 :
				isneed+=need
				print tostr(geninfo[1]), t1, t2, t3
				sg.add_soldier( need )
				sg.add_to_gen( genid, e, need )
		if isneed > 0 : return 1

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
		print sg.cname, "����ʿ��", tostr(inf[2]),r['ret'] == 0
	if len(ls) == 0:
		if len( filter( lambda x:x[7] < 90 , infos ) ) == 0:
			infos.sort( cmp = lambda x,y : cmp(y[8],x[8]))
			return  infos[0][8]
				
		infos.sort( cmp = lambda x,y : cmp(x[8],y[8]))
		return infos[0][8]
	return 5

def check_city_money( cid, timeout = 300 ):
	num = sg.get_money_number()
	if num > 2000000:
		call_trans_res( cid, money = 10000 )
	return timeout

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

def call_destroy_building( gid_pids ):
	tasklist = sg.get_current_update()
	vs = tasklist.values()
	if len(tasklist) == 3 :
		return min(vs)
	ts = []
	for gid, pid in gid_pids:
		if pid in tasklist.keys():
			ts.append( tasklist[pid] )
		r = sg.force_update_building( pid )
		if r['ret']:
			r = sg.destroy_building( gid, pid )
			if r['ret'] == 0:
				return 5
	else:
		return min(ts) if ts else min(vs)

def do_task2( gens, ty ): # [id, ���������� �������, �������� ]
	genids = [ y[0] for y in gens ]
	infos = sg.get_generals_info()
	generals = infos['generals']
	allname = []
	bok = 1
	for gen in gens:
		genid = gen[0]
		geninfo = filter( lambda x:x[0] == genid, generals )
		if geninfo:
			geninfo=geninfo[0]
			name = geninfo[1]
			allname.append(name)
		else: 
			bok =0
			continue
		# ����
		t1,t2,t3 = geninfo[4][0],geninfo[5][0],geninfo[6][0]
		print tostr(name), t1, t2, t3, gen
		for e in [1,2,3]:
			need = gen[e] - eval("t%d" % e )
			if  need > 0 :
				sg.add_soldier( need )
				sg.add_to_gen( genid, e, need )
	
	# ���ʿ��
	infos = sg.get_soldier_info()
	
	infos = filter( lambda x:x[1] in genids, infos )

	if infos:
		nfs = filter( lambda x: x[7] < 100 and x[8] == -1, infos )
		if nfs:
			bok *= 0
			n = call_up_shiqi( genids )
			return 5
		nfs = filter( lambda x:  x[7] < 90 and x[8] > -1, infos )
		
		if nfs:
			t = min( [ x[8] for x in nfs ])
			print "������ʿ��" ,t,"�������"
			return  t
	else:
		bok = 0
	
	
	if len(allname) < len(genids):
		bok = 0
		infos  = sg.get_mili_info()
		ts = []
		for  info in  infos['come']:
			for gen in info[7]:
				if gen[0] in genids:
					ts.append( info[-1] )
		
		for  info in  infos['goto']:
			for gen in info[8]:
				if gen[0] in genids:
					ts.append( info[-2] )
		if ts:
			print "������,",min(ts),"�������."
			return min(ts)
		else:
			bok = 1
	

	
	
	if bok == 0:
		return 100
		
	infos = sg.get_wu_infos()
	infos = filter( lambda x:x[0] in genids and x[4] == 0 , infos )
	if len(infos) != len( genids ):
		return 150
	
	print "�����Ѿ���."
	for e in allname: print tostr(e)
		
	from libsgmap import MapInfo
	mi = MapInfo()
	best = mi.getbest( ty )
	dest = 0
	for b in best:
		for e in  sg.lookup_map(b[1])['npc_tent']:
			if e[2] == b[1]:
				dest = b
				break
		else:
			mi.remove(b[1])
			continue
		break
	print dest
	if dest:
		r = sg.do_beat_city( genids, dest[1] )
		print "����" , r['ret'] == 0
		
	return 100
	
	
	

def main():
	
#	call_func( call_beat_city, tids[3] , 13 )

	#call_make_weapon()
#	call_func( call_yz_update_building, tids[0], [0] )
#	call_func( call_yz_update_building, tids[1], [0] )
#	call_func( call_yz_update_building, tids[2], [0] )
#	call_func( call_yz_update_building, tids[3], [0] )
#	call_func( call_yz_update_building, tids[4], [2,0,1] )
#	call_func( call_yz_update_building, tids[5], [2,0,1] )

# Ӫկ
	call_func( call_build_wall, tids[0] )
	call_func( call_build_wall, tids[2] )
	call_func( call_build_wall, tids[3] )
	call_func( call_build_wall, tids[1] )
	call_func( call_build_wall, tids[4] )
	call_func( call_build_wall, tids[5] )
	
#	call_func( check_skill_point, tids[0] )
#	call_func( check_skill_point, tids[2] )
#	call_func( check_skill_point, tids[3] )
#	call_func( check_skill_point, tids[1] )
#	call_func( check_skill_point, tids[4] )
#	call_func( check_skill_point, tids[5] )





# ��������

	call_many( check_general, (0,1,2,3,4) )



#	call_func( call_check_yz_res, cities[0], tids[0], wood= 400000, stone = 400000, iron = 150000 )
#	call_func( call_check_yz_res, cities[0], tids[1], wood= 400000, stone = 400000, iron = 150000 )
	call_func( call_check_yz_res, cities[0], tids[3], wood= 20000, stone = 20000, iron = 20000 , food = 600000 )
# ����
	cid = cities[0]
	call_func( call_get_newb_general, cid, 7 )
	call_func( call_get_newb_general, cid , 8 )

	call_func( do_task2, cid, [ [442487,5000,0,5000  ], [470182, 5000,0,5000] ], (1,2) )
	call_func( do_task2, cid, [ [363930,6000,0,6000  ], [364214,6000,0,6000  ], [326572,6000,0,6000  ] ], (3,0) )
	
	call_func( call_update_tech, cid )
	call_func( call_buy_resource, cid, 15 )
#	call_func( call_build_wall, cities[0] )
	call_func( call_update_hourse, cid )
	call_func( call_make_new_weapon, cid, 13,  205, 105, 2 )
	call_func( call_make_new_weapon, cid, 14,  305, 305, 3 )
	call_func( call_make_new_weapon, cid, 15,  405, 405, 1 )
#	call_func( call_sell_weapon,     cities[0], ( 207,306,406 ) )
	call_func( check_minxin, cid )
#	call_func( call_do_task, cid, 1 ,[ 	326572, 	363930] )
#	call_func( call_do_task, cid, 1, [363930,364214 ,326572 ] )

	call_func( check_skill_point, cid )
#	call_func( call_up_shiqi, cid, [470182,442097,470166,442487] )
	
# �³�	Ӫկ5: tid = 4
	cid = cities[1]
	call_func( call_check_yz_res, cid, tids[2], wood= 20000, stone = 20000, iron = 20000, food = 20000 )
	call_func( call_check_yz_res, cid, tids[4], wood= 20000, stone = 20000, iron = 20000, food = 20000 )
	call_func( call_buy_resource, cid, 20, low = 20000 )
	call_func( call_make_new_weapon, cid, 13,  205, 105,2 )
	call_func( call_make_new_weapon, cid, 14,  305, 305,2 )
	call_func( call_make_new_weapon, cid, 15,  405, 405,1 )
	call_func( call_update_hourse, cid )
#	call_func( call_update_wall, cid )
#	call_func( call_update_all, cid )
	call_func( call_build_wall, cid )
	call_func( check_minxin, cid )
	call_func( check_skill_point, cid )
	call_func( call_up_shiqi, cid, [442097] )

#	call_func( call_sell_weapon,  cities[1], (205,305,405) )
#	call_func( call_sell_weapon,  cities[0], (206,306,406) )
	
#�³�2, 
	cid = cities[2]
#	call_func( call_make_new_weapon, cities[2], 13,  103, 103, 1 )
#	call_func( call_sell_weapon,  cities[2], (103,) )
	call_func( call_buy_resource, cid, 10, low=2000 )
#	call_func( call_update_store, cid )
#	call_func( call_update_base, cid )
#	call_func( call_update_all, cid )
	call_func( call_update_hourse, cid )
	call_func( call_build_wall, cid )
	call_func( check_minxin, cid )
	call_func( check_skill_point, cid)
#	call_func( check_city_money, cid, cities[0] , timeout = 600)
#	call_func( call_destroy_building, cid, [[6,9],[9,11],[11,6]] )
#	call_func( check_city_money, cid, cities[4] , timeout = 300)
#	call_func( call_update_building2, cities[2], [9,6])

#	call_func( call_update_base, cities[0] )
#	call_func( call_update_wall, cities[0] )
#	call_func( call_update_store, cities[2] )
#	call_func( call_update_store, cities[1] )

# ˭������
	cid = cities[3]
	call_func( call_build_wall, cid )
	call_func( call_buy_resource, cid, 10 )
#	call_func( call_update_base, cities[3]  )
	call_func( call_update_all, cities[3]  )
	call_func( check_skill_point, cid)
	call_func( check_minxin, cid )
#	call_func( call_update_hourse, cid )
	call_func( call_check_yz_res, cid, tids[5], wood= 20000, stone = 20000, iron = 20000, food = 20000 )
	call_func( check_city_money, cid, cities[0] , timeout = 80)

# ����
	cid = cities[4]
	call_func( call_build_wall, cid )
	call_func( call_buy_resource, cid, 10 )
	call_func( check_skill_point,cid)
	call_func( check_minxin, cid )
	call_func( call_update_all, cid )
	
	
	
	print "Started.."

	#call_update_tech()
	#call_update_build()
from libsgmap import getmapinfo
def done(n, r ):
	print r
	if r:
		print n
	reactor.callLater(600, getmap )

def getmap():
	threads.deferToThread(getmapinfo, sg).addCallback( done, 0 ).addErrback(done, 1)




if __name__ == "__main__":
	#print check_minxin()
	print sg.change_city( cities[0] )
	#call_make_new_weapon( 13, 103,103)
	#call_do_task(1, [363930,364214,326572])
	#print check_general()
	#check_skill_point()
	#call_buy_resource()
	#call_func( call_make_new_weapon, cities[1], 13,  205, 105,2 )
	#do_task2( [ [442487,0,0,5000  ], [470182, 1000,0,3500] ] )
	#print call_do_task(1,[363930,364214 ,326572 ])
	getmap()
	main()
	#threads.deferToThread(execfile, "libsgmap.py").addCallback( main.done ).addErrback(main.done)
	#print call_make_new_weapon(13, 205, 105 )

	

reactor.run()

