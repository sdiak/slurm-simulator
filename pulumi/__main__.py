"""Cluster definition main program

"""
import pulumi
import ipaddress
from typing import Any

import virsh
from cluster import Cluster
from network import Network, NetworkRole
from node import Node, Os, NodeRole
from user import User

def create_cluster() -> Cluster:
    cluster = Cluster(name=pulumi.get_stack(), config=pulumi.Config())

    cluster.add_network(Network(role=NetworkRole.ADMIN, address=ipaddress.IPv4Network('10.0.0.0/24')))
    cluster.add_network(Network(role=NetworkRole.STORAGE, address=ipaddress.IPv4Network('10.0.1.0/24')))
    cluster.add_network(Network(role=NetworkRole.FABRIC, address=ipaddress.IPv4Network('10.0.2.0/24')))

    cluster.add_user(User(name="root", password="abcd", uid=0))
    cluster.add_user(User(name="user1", groups=['group1', 'group2']))
    cluster.add_user(User(name="user2", groups=['group3']))

    cluster.add_node(Node(name="admin", networks=[cluster.networks['admin'], cluster.networks['storage']], mem_gb=2, roles={NodeRole.SLURMCTLD, NodeRole.NFSD, NodeRole.LOGIN}))
    cluster.add_node(Node(name="ubuntu01", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}, os=Os.UBUNTU_24_04))
    cluster.add_node(Node(name="ubuntu02", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}, os=Os.UBUNTU_24_04))
    cluster.add_node(Node(name="rocky01", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}))
    cluster.add_node(Node(name="rocky02", networks=[cluster.networks['admin'], cluster.networks['storage'], cluster.networks['fabric']], mem_gb=1, roles={NodeRole.COMPUTE}))

    return cluster

def main() -> None:
    cluster = create_cluster()

    populate_ansible_vars(cluster)
        
    virsh.build(cluster)
    pulumi.export("cluster", cluster.output)
    

def populate_ansible_vars(cluster: Cluster):
    networks: dict[str, dict[str, Any]] = {
        net.role.value: net.to_ansible(cluster.name) for net in cluster.networks.values()
    }
    groups: dict[str,set] = dict(all=set())
    slurm_nodes: list[dict[str, Any]] = []
    all_computes=''
    for node in cluster.nodes.values():
        if NodeRole.COMPUTE in node.roles:
            slurm_nodes.append(node.slurm_def())
            if len(all_computes) == 0:
                all_computes = node.name
            else:
                all_computes += "," + node.name
        groups['all'].add(node.name)
        for role in sorted(node.roles):
            group = role.value
            if group in groups:
                groups[group].add(node.name)
            else:
                groups[group] = { node.name }
    
    wlm = dict(groups=sorted(cluster.groups), users=list(map(User.to_wlm, cluster.users.values())))
    for node in cluster.nodes.values():
        node.ansible_vars['all_groups'] = groups
        node.ansible_vars['cluster_name'] = cluster.name
        node.ansible_vars['slurm_nodes'] = slurm_nodes
        node.ansible_vars['all_computes'] = all_computes
        node.ansible_vars['networks'] = networks
        node.ansible_vars['wlm'] = wlm
    


if __name__ == "__main__":
    main()
