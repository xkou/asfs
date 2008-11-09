import winpcap  as pcap
import dpkt
cap = pcap.open( mode = 0, timeout = 500)
cap.setfilter("tcp port 80 and host 60.12.226.253")
for t, d in cap:
	pack = dpkt.ethernet.Ethernet( d )
	data = pack.data.data.data.decode("utf8",'ignore').encode("gbk",'ignore')
	
	F = open("c:/sg.txt", "ab")
	if data.startswith('POST /') or data.startswith('HTTP/1.1 200 OK') : F.write("\r\n\r\n")
	
	F.write(data)
	
	F.close()