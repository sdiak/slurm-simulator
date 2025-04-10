from dataclasses import dataclass, field
from typing import Any
from collections import OrderedDict
import pulumi

import common
from network import Network, NetworkRole
from node import Node
from user import User

@dataclass
class Cluster:
    """ A cluster
    """

    name: str
    """ The cluster name"""

    config: pulumi.Config = field(repr=False)
    """ Pulumi configuration """

    output: dict[str, Any] = field(default_factory=dict, repr=False)
    """ Json data printed by `pulumi stack output cluster` """

    networks: OrderedDict[str, Network] = field(default_factory=OrderedDict)
    """ This cluster networks """

    nodes: OrderedDict[str, Node] = field(default_factory=OrderedDict)
    """ This cluster nodes """

    users: OrderedDict[str, User] = field(default_factory=OrderedDict)
    """ This cluster users """

    groups: set[str] = field(default_factory=set)
    """ This cluster groups """

    __next_uid: int = field(repr=False, default=1000)
    __uids: set[int] = field(default_factory=set)
    __admin_network: Network|None = None

    def __post_init__(self):
        common.check_identifier(self.name, "cluster name")

    def add_network(self, network: Network):
        """Add a network to this cluster

        Args:
            network (Network): The network

        Raises:
            ValueError: when the network is invalid
        """
        if len(self.nodes) > 0:
            raise ValueError("Networks can not be added after nodes are defined")
        if network.role == NetworkRole.ADMIN and self.__admin_network is not None:
            raise ValueError("Only one admin network can be defined")
        if network.name in self.networks:
            raise ValueError(f"Duplicate network name {network.name}")
        for net in self.networks.values():
            if net.address.overlaps(network.address):
                raise ValueError(f"{network.name}:{network.address} overlaps with existing {net.name}:{net.address}")
        self.networks[network.name] = network
        if network.role == NetworkRole.ADMIN:
            self.__admin_network = network
    
    def admin_network(self) -> Network:
        if self.__admin_network is None:
            raise ValueError("The admin network is not defined")
        return self.__admin_network

    def add_node(self, node: Node):
        """Add a node to this cluster

        Args:
            node (Node): The node

        Raises:
            ValueError: when the node is invalid
        """
        if node.name in self.nodes:
            raise ValueError(f"Duplicate node name {node.name}")
        if len(node.networks) == 0:
            raise ValueError(f"No networks in {node.name}")
        for network in node.networks:
            if network.name not in self.networks:
                raise ValueError(f"Node {node.name} network network {network.name} is not present in the Cluster")
        self.nodes[node.name] = node
    
    def add_user(self, user: User):
        """Add a user to this cluster

        Args:
            user (User): The user

        Raises:
            ValueError: when the user is invalid
        """
        if user.name in self.users:
            raise ValueError(f"Duplicate user name {user.name}")
        if user.uid is None:
            while self.__next_uid in self.__uids:
                self.__next_uid += 1
            user.uid = self.__next_uid
            self.__next_uid += 1
        elif user.uid in self.__uids:
            raise ValueError(f"Duplicate user uid {user.uid}")
        
        ssh_pubkey = self.config.get("ssh_pubkey")
        if ssh_pubkey is not None:
            user.ssh_authorized_keys.append(ssh_pubkey)
        self.users[user.name] = user
        self.groups.update(user.groups)


