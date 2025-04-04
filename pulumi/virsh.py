"""Wrapper to virsh binaries
"""
import logging
import subprocess
from dataclasses import dataclass
from typing import Any, Optional, Dict, List
import libvirt
import pulumi
import pulumi_libvirt as pulibvirt

from cluster import Cluster
from network import Network
from node import Node, OsImage
from user import User
from cloud_init import network_config_rendered, cloud_init_rendered

def net_dhcp_leases(network_name: str, logger: Any = logging) -> Optional[Dict[str, str]]:
    """Returns a dictionnary mapping mac-address to ip obtained from the network dhcp server

    Args:
        network_name (str): the libvirt network name

    Returns:
        dict[str, str]|None: a mapping of domain interface mac-address to ip (or None in case of errors)
    """
    buffer = _exec([ 'virsh', 'net-dhcp-leases', network_name ], logger)
    if buffer is None:
        return None
    result = {}
    for line in buffer.splitlines():
        cols = line.split()
        if len(cols) == 7 and len(cols[2].split(':')) == 6:
            cols[4] = cols[4].split('/')[0]
            result[cols[2].lower()] = None if len(cols[4]) == 0 else cols[4]
    return result

def vol_list(pool: str, logger: Any = logging) -> List[str]:
    conn = libvirt.open()
    try:
        return conn.storagePoolLookupByName(pool).listVolumes()
    except:
        logger.exception("Error")
    finally:
        conn.close()
    return []

def vol_exists(pool: str, name: str, logger: Any = logging) -> bool:
    return name in vol_list(pool, logger)

@dataclass
class DomIfAddr:
    name: str
    mac_addr: str
    protocol: str
    ip: str

    @staticmethod
    def of(domain_name: str, logger: Any = logging) -> Optional[List['DomIfAddr']]:
        buffer = _exec(['virsh', 'domifaddr', domain_name], logger)
        if buffer is None:
            return None
        result: list[DomIfAddr] = []
        for line in buffer.splitlines():
            cols = line.split()
            if len(cols) == 4 and len(cols[1].split(':')) == 6:
                cols[3] = cols[3].split('/')[0]
                cols[3] = None if len(cols[3]) == 0 else cols[3]
                result.append(DomIfAddr(name=cols[0], mac_addr=cols[1], protocol=cols[2], ip=cols[3]))
        return result



def _exec(cmd: List[str], logger: Any) -> Optional[str]:
    try:
        virsh_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        if virsh_result.returncode == 0:
            return virsh_result.stdout
        logger.error(f"`{' '.join(cmd)}`: {virsh_result.stderr}")
    except Exception as e:
        logger.error(f"Unable to execute: `{' '.join(cmd)}` ({e!r})")
    return None


def __libvirt_create_volume(cluster: Cluster, resource_name: str, img: OsImage) -> pulibvirt.Volume:
    base_volume = __libvirt_base_image_volume(cluster.config.get('base-image-pool', 'default'), img)
    base_volume_ref = dict(base_volume_id=base_volume.id) if isinstance(base_volume, pulibvirt.Volume) else base_volume
    return pulibvirt.Volume(
        resource_name=resource_name,
        pool=cluster.config.get('node-pool', 'default'),
        **base_volume_ref
    )

def __libvirt_base_image_volume(pool: str, img: OsImage) -> pulibvirt.Volume | Dict[str,str]:
    # Do not recreate if it exists
    if vol_exists(pool, img.name):
        return dict(base_volume_name=img.name, base_volume_pool=pool)
    return pulibvirt.Volume(
        name=img.name,
        opts=pulumi.ResourceOptions(retain_on_delete=True), # Kept on provider to avoid downloading again
        resource_name=img.name,
        pool=pool,
        source=img.source
    )

def __build_network(cluster: Cluster, network: Network):
    pulumi.log.debug(f"{__name__}: __build_network({cluster.name=!r}, {network.name=!r})")
    network.resource = pulibvirt.Network(
        cluster.name + "-" + network.name,
        addresses=[ str(network.address) ],
        autostart=network.autostart,
        domain=cluster.name + "." + network.name + ".local",
        mode = "nat",
        dns = pulibvirt.NetworkDnsArgs(enabled=True, local_only=False,) if network.dns else None,
        dhcp = pulibvirt.NetworkDhcpArgs(enabled=True) if network.dhcp else None,
    )
    cluster.output['networks'].append(dict(
        name=network.name,
        addresses=[ str(network.address) ],
        domain=cluster.name + "." + network.name + ".local",
        mode = "nat",
        libvirt=dict(name=cluster.name + "-" + network.name, dhcp=network.dhcp),
    ))

def __build_domain(cluster: Cluster, node: Node):
    pulumi.log.debug(f"{__name__}: __build_domain({cluster.name=!r}, {node.name=!r})")
    # Dictionary for cloud-init rendering
    env = dict(
        hostname=node.name,
        fqdn=node.name + '.' + cluster.name + ".admin.local",
        users=[user.to_json() for user in cluster.users.values() ],
        groups=list(cluster.groups),
        num_nets=len(cluster.networks)
    )
    if cluster.config.get('http_proxy') is not None:
        env['http_proxy'] = cluster.config.get('http_proxy')
    network_config = network_config_rendered(env)
    user_data = cloud_init_rendered(env)
    pulumi.log.debug(network_config)
    pulumi.log.debug(user_data)
    cloud_init = pulibvirt.CloudInitDisk(
        cluster.name + "-" + node.name + "-commoninit.iso",
        meta_data=user_data,
        user_data=user_data,
        network_config=network_config,
        pool=cluster.config.get('node-pool', 'default'),
    )
    volume = __libvirt_create_volume(cluster, cluster.name + "-" + node.name, node.os.value)
    domain = pulibvirt.Domain(
        resource_name=cluster.name + "-" + node.name,
        name=cluster.name + "-" + node.name,
        memory=int(node.mem_gb * 1024.),
        vcpu=node.cpus,
        cloudinit=cloud_init.id,
        qemu_agent=True,
        graphics=pulibvirt.DomainGraphicsArgs(type="vnc"),
        network_interfaces=[ pulibvirt.DomainNetworkInterfaceArgs(
            network_id = net.resource.id,
            wait_for_lease = True,
            hostname=cluster.name + "-" + node.name
        ) for net in cluster.networks.values() ],
        disks=[ pulibvirt.DomainDiskArgs(volume_id=volume.id) ],
        consoles=[
            pulibvirt.DomainConsoleArgs(type="pty", target_type="serial", target_port="0"),
            pulibvirt.DomainConsoleArgs(type="pty", target_type="virtio", target_port="0"),
        ],
    )
    cluster.output['hosts'].append(dict(
        name=node.name, roles=list(node.roles), ansible_vars={},
        libvirt=dict(name=domain.name, network_interfaces=domain.network_interfaces)
    ))

def __force_eval(collection):
    for _ in collection:
        pass

def build(cluster: Cluster):
    pulumi.log.info(f"{__name__}: build({cluster.name=!r})")
    # Build the networks
    cluster.output['networks'] = []
    __force_eval(map(lambda n : __build_network(cluster, n), cluster.networks.values()))
    # Build the nodes
    cluster.output['hosts'] = []
    __force_eval(map(lambda n : __build_domain(cluster, n), cluster.nodes.values()))
