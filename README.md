# slurm-simulator
Simulate a cluster to help you test various Slurm settings


# Initial set-up

Install dependencies :

[Download and install Pulumi](https://www.pulumi.com/docs/iac/download-install/)

```shell
# deb: sudo apt install libvirt-dev genisoimage
# rhel: sudo dnf install libvirt-devel genisoimage
cd pulumi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the pulumi stack :

```shell
cd pulumi
source venv/bin/activate
pulumi login --local
# Cluster name
pulumi stack init test-cluster
# Copy your public ssh-key to the cluster nodes
pulumi config set ssh_pubkey "$(cat ~/.ssh/id_ed25519.pub)"
# If your nodes needs a proxy, you can configure http_proxy
# pulumi config set http_proxy http://my-proxy:8080
# Configure the pool for cloud init images (default: "default")
pulumi config set base-image-pool default
# Configure the pool for node volumes (default: "default")
pulumi config set node-pool default
```
