#! coding: utf-8
import wmi
import time
import pythoncom


def get_cpu():
	c = wmi.WMI()

	r = "Server Status:\n"
	n = 0
	for s in c.Win32_Processor():
		r += " -- CPU %d ռ %d%%\n" % (n, s.LoadPercentage )
		n += 1
	return r;


def get_mem():
	info =""
	c = wmi.WMI()
	print dir(c)
	print c.query("select * from Win32_LogicalMemoryConfiguration") 
	memory=c.Win32_LogicalMemoryConfiguration()[0]
	print memory.TotalPhysicalMemory 
	

	e = c.query( "Select * from Win32_PerfRawData_PerfOS_Memory")[0]
	info += "PhysicalMemory: %f%%" % (int(e.AvailableMBytes)*100 /( memory.TotalPhysicalMemory/1024.0))
	return info


def get_iis():
	info = "Server Informations:\n"
	I = wmi.WMI(moniker='//./root/MicrosoftIISv2')
	rs = I.query("SELECT * FROM IIsWebServerSetting where ServerAutoStart = true  ")
	for r in  rs:
		c = wmi.WMI()
		server = c.query("select * from Win32_PerfRawData_W3SVC_WebService where name = '%s'" %  r.ServerComment )
		info += " -- "+r.ServerComment +" "+ str(server[0].CurrentConnections) +"\n"

	return info.encode("gbk")


def send_mail( t, cont ):
	import smtplib
	f = " <keger@126.com>"
	to = ["server-mon@googlegroups.com"]
	s = smtplib.SMTP("smtp.126.com")
	s.set_debuglevel(1)
	s.login("keger", "168168donge")
	msg = ""
	msg += "From: %s\r\nTo: %s\r\nSubject: %s\r\nContent-Type: text/plain; charset=UTF-8;\r\n\r\n" % (f, ", ".join(to), t )
	msg += cont

	s.sendmail(f, to, msg)
	s.quit()


if __name__ == "__main__":
	info =""
	info += get_cpu()
	info += get_mem()
	info += "\n"
	info +=  get_iis()

	send_mail( time.strftime("%Y%m%d %H:%M:%S"), info )