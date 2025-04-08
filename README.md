slurm-simulator
-----------------------

Simulate a cluster to help you test various Slurm settings


# Boostrap

To use this project you have to install and initialize **Pulumi** see [./doc/bootstrap.md](./doc/bootstrap.md)


# Starting the cluster

Configure your cluster in [pulumi/\_\_main\_\_.py](https://github.com/sdiak/slurm-simulator/blob/3fbbdd2db435a5550db914e4850e2009fae14ee0/pulumi/__main__.py#L15-L27)

```shell
cd pulumi
# Start the cluster
pulumi up
# `pulumi up` does not wait for cloud-init on rocky (if you know why; please open an issue),
# workaround :
sleep 60s
# check that every nodes as an ip (replace "test-cluster" with the name of
# your cluster that you defined in the bootstrap phase by "pulumi stack init test-cluster")
virsh net-dhcp-leases test-cluster-admin
# Back to the root of the project
cd ..
```

# Configuring the nodes

This project provide compiled slurm packages for :
- RHEL (Rocky) 8.10
- Ubuntu 24.04

If you need to support other nodes OS, see [doc/compiling-slurm.md](./doc/compiling-slurm.md).

Run the ansible playbook
```shell
ansible-playbook playbook.yml
```

At the end of the playbook, you have a cluster configured with :

- Slurm :
    - accounting: slurmdbd+mariadb,
    - cgroup v2
- pdsh :
    - `pdsh -g all uname -r | dshbak -c` : get kernel version on all nodes,
    - `pdsh -g compute uname -r | dshbak -c` : get kernel version on compute nodes.
- nfs for home folder and slurm conf.

Every node should be up and all compute node should be `IDLE` in the **all** partition.

You can now experiment with various slurm settings to solve your issue.

# Destroying the cluster

```shell
cd pulumi
pulumi down
```
