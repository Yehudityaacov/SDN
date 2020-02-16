from pox.core import core
from pox.lib.util import dpidToStr
from pox.openflow import *
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet import *
import csv
import string

policyFile = "/home/judit/pox/pox/misc/firewall-policies.csv"
policyList = None

h1 = "00:00:00:00:00:01"
h2 = "00:00:00:00:00:02"
h3 = "00:00:00:00:00:03"
h4 = "00:00:00:00:00:04"

h1_ip = "10.0.0.1"
h2_ip = "10.0.0.2"
h3_ip = "10.0.0.3"
h4_ip = "10.0.0.4"

s1 = "00-00-00-00-00-01"
s2 = "00-00-00-00-00-02"
s3 = "00-00-00-00-00-03"
s4 = "00-00-00-00-00-04"

switch = None
src_host=None
dst_host=None
video=None

ip_mac = {h1_ip:h1,h2_ip:h2,h3_ip:h3,h4_ip:h4}
	

AllRoutes = {
	#routes for s1
	(s1,h1,h2,"non_video"):4,
	(s1,h1,h3,"non_video"):1,
	(s1,h1,h4,"non_video"):1,
	(s1,h1,h2,"video"):4,
	(s1,h1,h3,"video"):2,
	(s1,h1,h4,"video"):2,
	
	(s1,h2,h1,"non_video"):3,
	(s1,h2,h3,"non_video"):1,
	(s1,h2,h4,"non_video"):1,
	(s1,h2,h1,"video"):3,
	(s1,h2,h3,"video"):2,
	(s1,h2,h4,"video"):2,

	(s1,h3,h1,"non_video"):3,
	(s1,h3,h2,"non_video"):4,
	(s1,h3,h4,"non_video"):1,
	(s1,h3,h1,"video"):3,
	(s1,h3,h2,"video"):4,
	(s1,h3,h4,"video"):2,

	(s1,h4,h1,"non_video"):3,
	(s1,h4,h2,"non_video"):4,
	(s1,h4,h3,"non_video"):1,
	(s1,h4,h1,"video"):3,
	(s1,h4,h2,"video"):4,
	(s1,h4,h3,"video"):2,

	#routes for s2
	(s2,h1,h2,"non_video"):1,
	(s2,h1,h3,"non_video"):2,
	(s2,h1,h4,"non_video"):2,
	
	
	(s2,h2,h1,"non_video"):1,	
	(s2,h2,h3,"non_video"):2,
	(s2,h2,h4,"non_video"):2,
	

	(s2,h3,h1,"non_video"):1,
	(s2,h3,h2,"non_video"):1,
	(s2,h3,h4,"non_video"):2,
	
	(s2,h4,h1,"non_video"):1,
	(s2,h4,h2,"non_video"):1,
	(s2,h4,h3,"non_video"):2,

        #routes for s3
	(s3,h1,h2,"video"):1,
	(s3,h1,h3,"video"):2,
	(s3,h1,h4,"video"):2,
	
	
	(s3,h2,h1,"video"):1,
	(s3,h2,h3,"video"):2,
	(s3,h2,h4,"video"):2,
	

	(s3,h3,h1,"video"):1,
	(s3,h3,h2,"video"):1,
	(s3,h3,h4,"video"):2,
	
	(s3,h4,h1,"video"):1,
	(s3,h4,h2,"video"):1,
	(s3,h4,h3,"video"):2,
	
        #routes for s4
	(s4,h1,h2,"non_video"):1,
	(s4,h1,h3,"non_video"):3,
	(s4,h1,h4,"non_video"):4,
	(s4,h1,h2,"video"):2,
	(s4,h1,h3,"video"):3,
	(s4,h1,h4,"video"):4,
	
	(s4,h2,h1,"non_video"):1,
	(s4,h2,h3,"non_video"):3,
	(s4,h2,h4,"non_video"):4,
	(s4,h2,h1,"video"):2,
	(s4,h2,h3,"video"):3,
	(s4,h2,h4,"video"):4,

	(s4,h3,h1,"non_video"):1,
	(s4,h3,h2,"non_video"):1,
	(s4,h3,h4,"non_video"):4,
	(s4,h3,h1,"video"):2,
	(s4,h3,h2,"video"):2,
	(s4,h3,h4,"video"):4,

	(s4,h4,h1,"non_video"):1,
	(s4,h4,h2,"non_video"):1,
	(s4,h4,h3,"non_video"):3,
	(s4,h4,h1,"video"):2,
	(s4,h4,h2,"video"):2,
	(s4,h4,h3,"video"):3,

	
}


def firewall (src,dst):
	for rule in policyList:
		if src == rule[1] and dst == rule[2] : 
			print "Firewall blocked src:%s and dst:%s" %(src,dst)
			return True
		if src == rule[2] and dst == rule[1] :
			print "Firewall blocked src:%s and dst:%s" %(src,dst)
			return True
	return False
		
		

#Handles packet in messages from the switch.
def _handle_PacketIn (event):
	packet = event.parsed
	arp_packet = packet.find('arp')
	dest_mac = None

	if arp_packet is not None:      
        	if arp_packet.opcode == arp.REQUEST:
                	print "Received arp request from %s" % arp_packet.hwsrc
                	print "Creating fake arp reply"

			#create arp packet
          		a = arp()
          		a.opcode = arp.REPLY

			#Convert from ip destination address to mac address
			for ip,mac in ip_mac.items():
				if arp_packet.protodst == ip:
					dest_mac = mac
			
			if firewall(dest_mac,str(arp_packet.hwsrc)):
				return		

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
	print "Switch with dpid=%s connected" % dpidToStr(event.dpid)

	for vid, OutPort in AllRoutes.items():
		switch,src_host,dst_host,video=vid
		#print "switch %s = event %s" % (switch, dpidToStr(event.dpid))
		if(switch == dpidToStr(event.dpid)):
			if video == "video":
				match = of.ofp_match()
				match.dl_src = EthAddr(src_host)
				match.dl_dst = EthAddr(dst_host)
				match.dl_type = 0x0800
				match.nw_proto = 6
				match.tp_dst = 10000
			
				fm = of.ofp_flow_mod()
				fm.match = match
				fm.hard_timeout = 300
 				fm.idle_timeout = 100
				fm.priority = 2;
  				fm.actions.append(of.ofp_action_output(port=OutPort))
			
				event.connection.send(fm)
			else:
				match = of.ofp_match()
				match.dl_src = EthAddr(src_host)
				match.dl_dst = EthAddr(dst_host)
			
				fm = of.ofp_flow_mod()
				fm.match = match
				fm.hard_timeout = 300
 				fm.idle_timeout = 100
				fm.priority = 1;
  				fm.actions.append(of.ofp_action_output(port=OutPort))
			
				event.connection.send(fm)

			

def _handle_ConnectionDown(event):
  print "Switch %s disconnected" % dpidToStr(event.dpid)



def launch ():
	global policyList
  	with open (policyFile) as f:
		reader = csv.reader(f)
		policyList = list(reader)

	del policyList[0]
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
        core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
        core.openflow.addListenerByName("ConnectionDown", _handle_ConnectionDown)
		



