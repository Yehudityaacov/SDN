from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

class SimplePktSwitch(Topo):

    def __init__(self):
        Topo.__init__(self)

    def build(self):    

        h1 = self.addHost('h1',ip='10.0.0.1',mac='00:00:00:00:00:01')
        h2 = self.addHost('h2',ip='10.0.0.2',mac='00:00:00:00:00:02')
        h3 = self.addHost('h3',ip='10.0.0.3',mac='00:00:00:00:00:03')
        h4 = self.addHost('h4',ip='10.0.0.4',mac='00:00:00:00:00:04')

        s1 = self.addSwitch('s1',dpid = "1")
        s2 = self.addSwitch('s2',dpid = "2")
        s3 = self.addSwitch('s3',dpid = "3")
        s4 = self.addSwitch('s4',dpid = "4")

        self.addLink(s1,h1,port1=3)
        self.addLink(s1,h2,port1=4)
	self.addLink(s1,s2,port1=1,port2=1,bw=1)
        self.addLink(s1,s3,port1=2,port2=1,bw=10)
        self.addLink(s4,h3,port1=3)
        self.addLink(s4,h4,port1=4)

     
        self.addLink(s4,s2,port1=1,port2=2,bw=1)
        self.addLink(s4,s3,port1=2,port2=2,bw=10)

    

def run():
    c = RemoteController(name='c',ip='127.0.0.1',protocol = 'tcp',port=6633)
    net = Mininet(topo=SimplePktSwitch(),controller=None,link=TCLink)
    net.addController(c)
    net.start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
