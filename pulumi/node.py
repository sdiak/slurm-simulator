from dataclasses import dataclass, field
from enum import Enum

import common
from network import Network

@dataclass
class OsImage:
    name: str
    source: str

class Os(Enum):
    ROCKY_8_10 = OsImage(name="rocky8.x86_64.qcow2", source="https://dl.rockylinux.org/pub/rocky/8/images/x86_64/Rocky-8-OCP-Base-8.10-20240528.0.x86_64.qcow2")
    UBUNTU_24_04 = OsImage(name="ubuntu-24.04.x86_64.qcow2", source="https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img")

@dataclass
class Node:
    """ A cluster node
    """

    name: str
    """ Node name """

    networks: set[Network] = field(default_factory=set)
    """ The network that this node is connected to """

    cpus: int = 4
    """ The number of virtual CPU """
    
    mem_gb: float = 1
    """ The amount of RAM in Gigabyte """

    roles: set[str] = field(default_factory=set)
    """ The set of roles """

    os: Os = Os.ROCKY_8_10
    """ The operating system """

    def __post_init__(self):
        common.check_identifier(self.name, "node name")
        map(common.check_identifier, self.roles)
        
    
