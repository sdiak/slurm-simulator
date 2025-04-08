from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import common
from network import Network

@dataclass
class OsImage:
    name: str
    source: str
    nic_name: str
    nic_offset: int

class Os(Enum):
    ROCKY_8_10 = OsImage(name="rocky8.x86_64.qcow2", source="https://dl.rockylinux.org/pub/rocky/8/images/x86_64/Rocky-8-OCP-Base-8.10-20240528.0.x86_64.qcow2", nic_name="eth", nic_offset=0)
    UBUNTU_24_04 = OsImage(name="ubuntu-24.04.x86_64.qcow2", source="https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img", nic_name="ens", nic_offset=3)

    def is_rhel(self) -> bool:
        return self in (Os.ROCKY_8_10, )


class NodeRole(Enum):
    SLURMCTLD = 'slurmctld'
    ''' The slurm controller '''

    NFSD = 'nfsd'
    ''' The nfs server '''

    LOGIN = 'login'
    ''' A login node '''

    COMPUTE = 'compute'
    ''' A compute node '''

@dataclass
class Node:
    """ A cluster node
    """

    name: str
    """ Node name """

    networks: list[Network] = field(default_factory=list)
    """ The network that this node is connected to """

    sockets: int = 2
    """ The number of virtual Sockets """

    cpus_per_socket: int = 2
    """ The number of virtual CPU per socket """
    
    mem_gb: float = 1
    """ The amount of RAM in Gigabyte """

    roles: set[NodeRole] = field(default_factory=set)
    """ The set of roles """

    os: Os = Os.ROCKY_8_10
    """ The operating system """

    ansible_vars: dict[str, Any] = field(default_factory=dict)
    """ Ansible variables """

    def __post_init__(self):
        common.check_identifier(self.name, "node name")

    def total_cpus(self) -> int:
        return self.sockets * self.cpus_per_socket

    def slurm_def(self) -> dict[str, Any]:
        return dict(
            name=self.name,
            cpus=self.sockets * self.cpus_per_socket,
            sockets=self.sockets,
            cpus_per_socket=self.cpus_per_socket,
            real_memory=int(self.mem_gb * 1024 * 0.7),
        )


    def get_nics(self, cluster_name: str, admin_net: Network) -> list[dict[str, Any]]:
        nics = []
        i = self.os.value.nic_offset
        for net in self.networks:
            nic = dict(
                name=self.os.value.nic_name + str(i),
                dhcp4=True
            )
            if False and self.os.is_rhel() and not net == admin_net:
                nic['nameservers'] = dict(
                    search='[' + common.domain(cluster_name, net) + ']',
                    addresses='[' + net.dns_server() + ']',
                )
            nics.append(nic)
            i += 1
            
        return nics
        
    
