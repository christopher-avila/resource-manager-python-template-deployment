import os.path
from deployer import Deployer


# This script expects that the following environment vars are set:
#
# AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
# AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
# AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret

scaleNumber = 1
print("Credentials (client_id, client_secret, tenant_id, subscription_id): ({} {} {} {})\n".format(os.environ['AZURE_CLIENT_ID'], os.environ['AZURE_CLIENT_SECRET'], os.environ['AZURE_TENANT_ID'], os.environ['AZURE_SUBSCRIPTION_ID']))

my_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID', '11111111-1111-1111-1111-111111111111')   # your Azure Subscription Id
my_resource_group = "rg-scale-{}".format(scaleNumber)            # the resource group for deployment
my_pub_ssh_key_path = os.path.expanduser('~/.ssh/id_rsa.pub')   # the path to your rsa public key file

msg = "\nInitializing the Deployer class with subscription id: {}, resource group: {}" \
    "\nand public key located at: {}...\n\n"
msg = msg.format(my_subscription_id, my_resource_group, my_pub_ssh_key_path)
print(msg)

# Initialize the deployer class
deployer = Deployer(my_subscription_id, my_resource_group, my_pub_ssh_key_path, scaleNumber)

print("Beginning the deployment... \n\n")

## Deploy the template
my_deployment = deployer.deploy()
print("Done deploying!!\n\nYou can connect via: `ssh {}@{}.westus2.cloudapp.azure.com`".format(deployer.adminUsername, deployer.dns_label_prefix))

## Stop Machines
# deployer.stopMachines()

## Resume Machines
# deployer.resumeMachines()

print("IP: {}".format(deployer.getIPAddress()))

# Destroy the resource group which contains the deployment
# deployer.destroy()
