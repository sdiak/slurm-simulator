slurm-simulator
-----------------------

Simulate a cluster to help you test various Slurm settings


# Bootstrap

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

# FAQ

## Purpose

I sometimes have to setup very complex Slurm configuration and plugins for my clients.\
I have created a private pulumi project for this purpose and used it to test various solutions to solve my issues without requiring a baremetal cluster.

I have know decided to clean up the code and make public for every sys-admin that might need it.

## The documentation is lacking

Please open an [issue](https://github.com/sdiak/slurm-simulator/issues) explaining what is missing.

## Maintaining multiple simulator

You can have multiple simulator running :
- create a branch for each simulator : `git checkout -b sim1`
- create and configure a pulumi stack for the branch :
    - `pulumi stack init sim1`,
    - see [./doc/bootstrap.md](./doc/bootstrap.md) for "Create the pulumi stack"
- continue with [Starting the cluster](#starting-the-cluster)

## Can I use the ansible roles to deploy a real slurm install

This is not the purpose of this project:
- it might be dangerous (for example the database password is [public](https://github.com/sdiak/slurm-simulator/blob/531cb90eae89fecf7e01925ec468cb4d1964ea52/roles/slurm/vars/main.yml#L3)),
- the [inventory](https://github.com/sdiak/slurm-simulator/blob/531cb90eae89fecf7e01925ec468cb4d1964ea52/ansible-hosts) is generated dynamicaly from the pulumi stack,
- ...

However feel free to derive some proper ansible roles and inventory for your needs.


## Planned

- Configured **slurmrestd**,
- Use the **storage** network for sharing `/home`,
- Configured **OpenMPI** over the **fabric** network.
