import re
from typing import TypeVar

from cluster import Cluster
from network import Network, NetworkRole

IDENTIFIER_RE = re.compile("^[A-Za-z_][A-Za-z_\\-0-9]*$")
def check_identifier(identifier: str, message_postfix: str):
    if not IDENTIFIER_RE.match(identifier):
        raise ValueError(f"{identifier:!r} is not a valid {message_postfix}")

T = TypeVar('T')

def not_none(v: T|None) -> T:
    assert v is not None
    return v


def domain(cluster: str|Cluster, net: str|Network) -> str:
    if isinstance(cluster, Cluster) and net == cluster.admin_network():
        return cluster.name + ".home.arpa."
    cluster = cluster.name if isinstance(cluster, Cluster) else cluster
    if isinstance(net, Network) and net.role == NetworkRole.ADMIN:
        return cluster + ".home.arpa."
    net = net.name if isinstance(net, Network) else net
    return net + "." + cluster + ".home.arpa."