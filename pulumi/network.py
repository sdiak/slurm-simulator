from dataclasses import dataclass, field
from enum import Enum
import ipaddress
from typing import Any
import pulumi_libvirt as pulibvirt

import common

class NetworkRole(Enum):
    ADMIN = 'admin'
    ''' The administrative network '''

    STORAGE = 'storage'
    ''' The storage network '''

    FABRIC = 'fabric'
    ''' The fabric network '''

@dataclass(eq=True)
class Network:
    """ A cluster network
    """
    sort_index: str = field(init=False, repr=False)

    role: NetworkRole
    """ The network name """

    address: ipaddress.IPv4Network
    """ The network IPv4 range """

    autostart: bool = False
    """ Autostart the network """

    dns: bool = True
    """ Adds a dns entry for this network """

    dhcp: bool = True
    """ Manage this network using DHCP """

    resource: pulibvirt.Network|None = None

    def __post_init__(self):
        common.check_identifier(self.name, "network name")
        self.sort_index = self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def dns_server(self) -> str:
        return str(self.address[1])
    
    def to_ansible(self, cluster_name: str) -> dict[str, Any]:
        return dict(
            name=self.name,
            role=self.role.value,
            address=str(self.address),
            domain=common.domain(cluster_name, self)
        )
    
    @property
    def name(self) -> str:
        return self.role.value
