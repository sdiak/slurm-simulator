"""Cluster definition main program

"""
import pulumi
import ipaddress


import virsh
from cluster import Cluster
from network import Network, NetworkRole
from node import Node, Os, NodeRole
from user import User

def main() -> None:
    cluster = Cluster(name=pulumi.get_stack(), config=pulumi.Config())
    cluster.add_network(Network(role=NetworkRole.ADMIN, address=ipaddress.IPv4Network('10.0.0.0/24')))
    cluster.add_network(Network(role=NetworkRole.STORAGE, address=ipaddress.IPv4Network('10.0.1.0/24')))
    cluster.add_network(Network(role=NetworkRole.FABRIC, address=ipaddress.IPv4Network('10.0.2.0/24')))
    cluster.add_user(User(name="root", password="abcd", uid=0))
    cluster.add_user(User(name="user1", groups={'group1', 'group2'}))
    cluster.add_user(User(name="user2", groups={'group3'}))

    cluster.add_node(Node(name="admin", networks=[cluster.networks['admin'], cluster.networks['storage']], mem_gb=2, roles={NodeRole.SLURMCTLD, NodeRole.NFSD, NodeRole.LOGIN}))
    cluster.add_node(Node(name="ubuntu01", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}, os=Os.UBUNTU_24_04))
    cluster.add_node(Node(name="ubuntu02", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}, os=Os.UBUNTU_24_04))
    cluster.add_node(Node(name="rocky01", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}))
    cluster.add_node(Node(name="rocky02", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}))

    groups: dict[str,set] = dict(all=set())
    for node in cluster.nodes.values():
        groups['all'].add(node.name)
        for role in node.roles:
            group = role.value
            if group in groups:
                groups[group].add(node.name)
            else:
                groups[group] = { node.name }
    for node in cluster.nodes.values():
        node.ansible_vars['all_groups'] = groups
        node.ansible_vars['cluster_name'] = cluster.name
    virsh.build(cluster)
    pulumi.export("cluster", cluster.output)
    

if __name__ == "__main__":
    main()
