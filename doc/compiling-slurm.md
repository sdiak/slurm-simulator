Compiling slurm 
------------------

This project provide compiled slurm packages for :
- RHEL (Rocky) 8.10
- Ubuntu 24.04

If you need to support other nodes OS, you need to provide the compiled slurm packages :

- if you have **Rocky Linux** nodes in your cluster, add the `slurm-*.rpm` to [../roles/slurm/files/rpms](https://github.com/sdiak/slurm-simulator/tree/98d9981571332d54c9bf69af114e83c52685c9cb/roles/slurm/files/rpms)
- if you have **Ubuntu** nodes in your cluster, add the `slurm-smd*.deb` to [../roles/slurm/files/debs](https://github.com/sdiak/slurm-simulator/tree/98d9981571332d54c9bf69af114e83c52685c9cb/roles/slurm/files/debs)

Then change [../roles/slurm/vars/main.yml:slurm_version](https://github.com/sdiak/slurm-simulator/blob/98d9981571332d54c9bf69af114e83c52685c9cb/roles/slurm/vars/main.yml#L2) to the slurm version.

You can use the [sdiak/slurm-compiler](https://github.com/sdiak/slurm-compiler) to compile for **rocky** and/or **ubuntu**.