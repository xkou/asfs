#! coding: utf-8
import wmi
import time
import pythoncom


def get_cpu():
	c = wmi.WMI()

	r = ""
	n = 0
	for s in c.Win32_Processor():
		r += "CPU %d 占用 %d%%\n" % (n, s.LoadPercentage )
		n += 1
	return r;


def get_mem():

	c = wmi.WMI()
	print dir(c)
	print c.query("select * from Win32_LogicalMemoryConfiguration") 
	memory=c.Win32_LogicalMemoryConfiguration()[0]
	info='Total Virtual Memory: ' +str( int ( memory.TotalVirtualMemory)/1024) + 	+'MB'
	print info

def get_iis():
	c = wmi.WMI()
	# http://timgolden.me.uk/python/wmi/cookbook.html
	iis = c.query("select * from Win32_PerfRawData_W3SVC_WebService" )
	for a in iis:
		print a.name
		a
#	connection = wmi.connect_server (server=".", namespace="root/MicrosoftIISv2")
	c = wmi.WMI (namespace="MicrosoftIISv2")

	for web_server in c.IIsWebService ( Name="W3SVC" ):
		break


def send_mail( t, cont ):
	import smtplib
	f = "服务器监控 <keger@126.com>"
	to = ["server-mon@googlegroups.com"]
	s = smtplib.SMTP("smtp.126.com")
	s.set_debuglevel(1)
	s.login("keger", "168168donge")

	msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nContent-Type: text/plain; charset=UTF-8;\r\n\r\n" % (f, ", ".join(to), t )
	msg += cont

	s.sendmail(f, to, msg)
	s.quit()


if __name__ == "__main__":
	info =""
#	info += get_cpu()
	print  get_iis()
#	get_mem()
#	send_mail( time.strftime("%Y年%m月%d日 %H:%M:%S"), info )