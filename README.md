# SDN


OpenFlow-controller-POX
OpenFlow controller POX and implementation of Firewall and Flowspace Slicing

How to run?
In the controller "con.py". Change the path that leads to the file "firewall-policies.csv" based on where you put it in your computer. The path is stored in variable "policyFile", right under all the imports.
Execute pox controller - "con.py"
Execute mininet topology - "topo.py"
How it works?
Firewall
Implementing a layer-2 firewall app using the POX controller.
The file "firewall-policies.csv" contains pairs of MAC addresses that are not allowed ro communicate witch each other.
When a connection between a switch and a controller is up, the app installs flow entries to disable the traffic between each pair of the MAC addresses in the list.

Flowspace Slicing
The network is sliced based on the app that is sending the traffic.
The video and non-video traffic treated differrently.
All the video traffic go through the high bandwith path, and all other traffic go through the lowe bandwith path.
Assuming all the video traffic use TCP port 10000.
