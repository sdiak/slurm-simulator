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
# `pulumi up` does not wait for cloud-init on rocky (if you know why; please open an issue), workaround :
sleep 60s
cd ..
```

# Configuring the nodes

You need to provide the compiled slurm packages :

- if you have **Rocky Linux** nodes in your cluster, add the `slurm-*.rpm` to [./roles/slurm/files/rpms](https://github.com/sdiak/slurm-simulator/tree/98d9981571332d54c9bf69af114e83c52685c9cb/roles/slurm/files/rpms)
- if you have **Ubuntu** nodes in your cluster, add the `slurm-smd*.deb` to [./roles/slurm/files/debs](https://github.com/sdiak/slurm-simulator/tree/98d9981571332d54c9bf69af114e83c52685c9cb/roles/slurm/files/debs)

You can use the [sdiak/slurm-compiler](https://github.com/sdiak/slurm-compiler) to compile for **rocky** and/or **ubuntu**.

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
