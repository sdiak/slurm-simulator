"""Cluster definition main program

"""
import pulumi
import ipaddress


import virsh
from cluster import Cluster
from network import Network
from node import Node, Os
from user import User

def main():
    cluster = Cluster(name=pulumi.get_stack(), config=pulumi.Config())
    cluster.add_network(Network(name="admin", address=ipaddress.IPv4Network('10.0.0.0/24')), admin=True)
    cluster.add_network(Network(name="storage", address=ipaddress.IPv4Network('10.0.1.0/24')))
    cluster.add_network(Network(name="fabric", address=ipaddress.IPv4Network('10.0.2.0/24')))
    cluster.add_user(User(name="root", password="abcd", uid=0))
    cluster.add_user(User(name="user1", groups={'group1', 'group2'}))
    cluster.add_user(User(name="user2", groups={'group3'}))

    cluster.add_node(Node(name="admin", networks=[cluster.networks['admin'], cluster.networks['storage']], mem_gb=2, roles={'slurmctld', 'nfsd', 'login'}))
    cluster.add_node(Node(name="ubuntu01", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={'compute'}, os=Os.UBUNTU_24_04))
    cluster.add_node(Node(name="ubuntu02", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={'compute'}, os=Os.UBUNTU_24_04))
    cluster.add_node(Node(name="rocky01", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={'compute'}))
    cluster.add_node(Node(name="rocky02", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={'compute'}))

    virsh.build(cluster)
    pulumi.export("cluster", cluster.output)
    

if __name__ == "__main__":
    main()
