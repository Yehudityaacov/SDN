#!/usr/bin/env python
import itertools
from random import *
import math
from pprint import pprint
import json
import networkx as nx
from networkx.readwrite import json_graph
from networkx.generators.classic import empty_graph, path_graph, complete_graph

from collections import defaultdict
import matplotlib.pyplot as plt

switches = []
hosts = []
host_switch_edges = []

def int_dpid(dpid):
	try:
		dpid = hex(dpid)[2: ]
		dpid = '0' * (16-len(dpid))+dpid
		return dpid
	except IndexError:
		raise Exeption ('Unable to create dpid')


def create_host_switches(num_switches):
	global switches
	global hosts
	num_hosts = randint(2,num_switches/2)
	
	for x in range(num_switches):
		switches.append(x)

	for x in range(num_hosts):
		hosts.append(x+num_switches)

def edges_from_hosts_to_switches():
	global host_switch_edges
	switches_with_host_connected = []
	for x in hosts:
		while(True):
			switch_to_connect = choice(switches)
			if switch_to_connect not in switches_with_host_connected:
				break
		switches_with_host_connected.append(switch_to_connect)
		host_switch_edges.append((x,switch_to_connect))


if __name__ == '__main__':
	shortest_path = {}	
	num_switches = 10
	g = nx.gnp_random_graph(num_switches, 0.5, seed=None, directed=False)

	create_host_switches(num_switches)
	edges_from_hosts_to_switches()
	
	pos = nx.spring_layout(g)
	
	#Add nodes that are hosts
	g.add_nodes_from(hosts,label = "hosts")
	#Edges between hosts and switches
	g.add_edges_from(host_switch_edges)

	#Find shortest path
	for x in hosts:
		for y in hosts:
			if x != y:
				shortest_path['%s,%s'%(x,y)] = nx.dijkstra_path(g,x,y)

	#Add dpid to switches and name them
	switches_d = {}
	for switch in switches:
		switches_d[switch] = int_dpid(switch)

	#Add mac and ip to hosts
	hosts_d = {}
	for host in hosts:
		if host < 10:
			hosts_d[host] = {'ip':'10.0.0.%s'%host,'mac':'00:00:00:00:00:0%s'%host}
		else:
			hosts_d[host] = {'ip':'10.0.0.%s'%host,'mac':'00:00:00:00:00:%s'%host}
	#Add ports to edges
	edges_d = {}
	i=1
	for edge in list(g.edges()):
		port1 =None
		port2 = None
		if edge[0] in switches:
			port1 = i
		if edge[1] in switches:
			port2 = i+1
		edges_d[str(edge)] = {'edge':edge,'port1':port1,'port2':port2}
		i += 2
	

	nx.draw(g)

	#plt.show()

	data = dict()
	data['hosts'] = hosts_d
	data['switches'] = switches_d
	data['edges'] = edges_d
	data['path'] = shortest_path 
	
	file = open("./random_topo.json","w")
	file.write(json.dumps(data))
	file.close
	

