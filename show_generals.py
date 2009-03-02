from libsg import SG, tostr

sg = SG()

infos =  sg.get_city_list()['infos'] 
cities = dict( [ (x[1],x[2]) for x in infos if x[1]>0  ] )

for k in cities:
	print tostr( cities[k] ), k
	sg.change_city(k)
	ks = sg.get_wu_infos()
	for k in ks:print "\t", tostr( k[1] ), k[0], k[5]