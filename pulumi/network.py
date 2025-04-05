from dataclasses import dataclass, field
import ipaddress
import pulumi_libvirt as pulibvirt

import common

@dataclass(eq=True)
class Network:
    """ A cluster network
    """
    sort_index: str = field(init=False, repr=False)

    name: str
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
