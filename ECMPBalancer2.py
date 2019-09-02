from pox.core import core
from pox.lib.util import dpidToStr
from pox.openflow import *
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet import *

from pprint import pprint
import json

switches_dpid = {}
event_dpid = {}
hosts_mac = {}
hosts_ip_mac = {}
hosts_ip = {}
connections = []
path = {}
current_path = {}
topo_json = "/home/sophie/SDN/ex3/random_topo.json"

def change_path():
	global current_path
	out_port = None
	destination = None
	if len(current_path) == 0:
		print "Looking for first shortest pathes:"
		for p in path.items():
			flag = 0
			cur_p = p[1]
			for p1 in current_path.items():
				if p1[0] == cur_p[0] and p1[-1] == cur_p[-1]:
					flag = 1
			if flag == 0:
				current_path[p[0]] = p[1]
	else:
		print "Looking for new shortest pathes:"
		for p in path.items():
			all_path = p[1]
			if all_path not in current_path.items():
				for cur_path in current_path.items():
					host = cur_path[1]
					if host[0] == all_path[0] and host[-1] == all_path[-1]:
						current_path[p[0]] = all_path
	print "Shortest pathes are: "
	for cur in current_path.items():
		print cur[1]

	for pathes in current_path.items():
		curr_path = pathes[1]
		for switch in curr_path:
			if switch != curr_path[0] and switch != curr_path[-1]:
				destination = curr_path[curr_path.index(switch)+1]
				for con in connections:
					switch_s = switches_dpid[str(switch)]
					if str(destination) in switches_dpid:
						destination_s = switches_dpid[str(destination)]
					else:
						destination_s = hosts_mac[str(destination)]
					if destination_s in con and switch_s in con:
						if switch_s == con[0]:
							out_port = con[2]
						else:
							out_port = con[3]
						if out_port != None:
							s_host = hosts_mac[str(curr_path[0])]
							d_host = hosts_mac[str(curr_path[-1])]
							match = of.ofp_match()
							match.dl_src = EthAddr(s_host)
							match.dl_dst = EthAddr(d_host)
							fm = of.ofp_flow_mod()
							fm.match = match
							fm.hard_timeout = 300
 							fm.idle_timeout = 100
  							fm.actions.append(of.ofp_action_output(port=out_port))
							event_dpid[switches_dpid[str(switch)]].connection.send(fm)
	
	
	




def _handle_ConnectionDown(event):
	print "Connection down"

def _handle_PacketIn(event):
	packet = event.parsed
	arp_packet = packet.find('arp')
	dest_mac = None
		
	if arp_packet is not None:      
        	if arp_packet.opcode == arp.REQUEST:
			change_path()
			print "Received arp request from %s" % arp_packet.hwsrc
                	print "Creating fake arp reply"

			#create arp packet
          		a = arp()
          		a.opcode = arp.REPLY

			#Convert from ip destination address to mac address
			for ip,mac in hosts_ip_mac.items():
				if arp_packet.protodst == ip:
					dest_mac = mac	
			print "Arp from %s,%s to %s%s"%(dest_mac,arp_packet.protodst,arp_packet.hwsrc,arp_packet.protosrc)

			
			a.hwsrc = EthAddr(dest_mac)
           		a.hwdst = EthAddr(arp_packet.hwsrc)

			a.protosrc = arp_packet.protodst
         		a.protodst = arp_packet.protosrc
          		a.hwlen = 6
          		a.protolen = 4
          		a.hwtype = arp.HW_TYPE_ETHERNET
          		a.prototype = arp.PROTO_TYPE_IP

			#create ethernet packet
          		e = ethernet()
          		e.set_payload(a)

			e.src = EthAddr(dest_mac)
            		e.dst = EthAddr(arp_packet.hwsrc)  

			e.type = ethernet.ARP_TYPE

          		msg = of.ofp_packet_out()
          		msg.data = e.pack()
			
			#send the packet back to the source
         		msg.actions.append( of.ofp_action_output( port = event.port ) )
          		event.connection.send( msg )
		  	
			
					
			

def _handle_ConnectionUp (event):
	event_dpid[dpidToStr(event.dpid)] = event
								
			
				
				
			
	

def launch ():
	global switches_dpid,hosts_mac,hosts_ip,connections,path,current_path
	with open(topo_json) as F:  
		json_data = json.load(F)  
        for x,y in json_data.items():
		if x == "switches":
			for switch in y:
				for switch,dpid in y.items():
					if (int(switch)+1)<10:
						switches_dpid[switch] = "00-00-00-00-00-0%s"%(str(int(switch)+1))
					else:
						switches_dpid[switch] = "00-00-00-00-00-%s"%(str(int(switch)+1))
	for x,y in json_data.items():
		if x == "hosts":
			for host,mac_ip in y.items():
				hosts_mac[host] = mac_ip['mac']
				hosts_ip[host] = IPAddr(mac_ip['ip'])
				hosts_ip_mac[mac_ip['ip']] =  hosts_mac[host]
	for x,y in json_data.items():
		if x == "edges":
			for key,value in y.items():
				e1 = None
				e2 = None
				t = value['edge']
				edge1 = str(t[0])
				edge2 = str(t[1])
				if edge1 in switches_dpid:
					e1 = switches_dpid[edge1]
				else:
					e1 = hosts_mac[edge1]
					
				if edge2 in switches_dpid:
					e2 = switches_dpid[edge2]
				else:
					e2 = hosts_mac[edge2]
					
				connections.append((e1,e2,value['port1'],value['port2']))
	for x,y in json_data.items():
		if x == "path":
			path = y
	
	

	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
        core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
        core.openflow.addListenerByName("ConnectionDown", _handle_ConnectionDown)
	
