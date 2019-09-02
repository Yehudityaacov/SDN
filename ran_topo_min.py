from pprint import pprint
import json
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink



class Topology(Topo):

	def __init__(self):
	        Topo.__init__(self)

    	def build(self):   
		switches = []
		hosts = []
		t_hosts = []
		t_switches = []
		
		with open('random_topo.json') as F:  
			json_data = json.load(F)  
         
		for x,y in json_data.items():
			if x == 'hosts':
				for host,mac_ip in y.items():
					hosts.append(self.addHost('h%s'%host,ip=mac_ip['ip'],mac=mac_ip['mac']))
					t_hosts.append(host)
		for x,y in json_data.items():
			if x == 'switches':
				for switch,dpid in y.items():
					num = int(switch)+1
					dp = None
					if num<10:
						dp = "000000000000000%s"%str(num)
					else:
						dp = "00000000000000%s"%str(num)
					switches.append(self.addSwitch('s%s'%switch,dpid=dp))
					t_switches.append(switch)
		for x,y in json_data.items():
			if x == 'edges':
				for key,value in y.items():
					edge1 = ""
					edge2 = ""
					t = value['edge']
					e1 = t[0]
					e2 = t[1]
					if str(e1) in t_hosts:
						edge1 = 'h%s'%e1
					else:
						edge1 = 's%s'%e1
					if str(e2) in t_hosts:
						edge2 = 'h%s'%e2
					else:
						edge2 = 's%s'%e2
					self.addLink(edge1,edge2,value['port1'],value['port2'])
			

	
		
def int_dpid(dpid):
	try:
		dpid = hex(dpid)[2: ]
		dpid = '0' * (16-len(dpid))+dpid
		return dpid
	except IndexError:
		raise Exeption ('Unable to create dpid')			 
   

def run():
	c = RemoteController(name='c0',ip='127.0.0.1',protocol = 'tcp',port=6633)
        net = Mininet(topo=Topology(),controller=None,link=TCLink)
        net.addController(c)
        net.start()

        CLI(net)
	try:
        	net.stop()
	except OSError as exc:
		if exc.errno == 36:
			print ""

if __name__ == '__main__':
	t_hosts = []
	t_switches = []
    	setLogLevel('info')
    	run()			


