"""A deployer class to deploy a template on Azure"""
import os.path
import json
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from array import array

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.

    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """
    name_generator = Haikunator()

    def __init__(self, subscription_id, resource_group, pub_ssh_key_path='~/.ssh/id_rsa.pub'):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.dns_label_prefix = self.name_generator.haikunate()

        pub_ssh_key_path = os.path.expanduser(pub_ssh_key_path)
        # Will raise if file not exists or not enough permission
        with open(pub_ssh_key_path, 'r') as pub_ssh_file_fd:
            self.pub_ssh_key = pub_ssh_file_fd.read()

        self.credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID']
        )
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)
        self.network_client = NetworkManagementClient(
            self.credentials, self.subscription_id)
        self.compute_client = ComputeManagementClient(self.credentials, self.subscription_id)

        self.adminUsername = 'azureSample'

    def deploy(self):
        """Deploy the template to a resource group."""
        self.client.resource_groups.create_or_update(
            self.resource_group,
            {
                'location':'westus2'
            }
        )

        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'slurm.json')
        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)

        parameters = {
            'sshKeyData': self.pub_ssh_key,
            'adminPassword': 'Ylosabes17#',
            # 'vmName': 'slurm-vm',
            'vmSize': 'Standard_D4_v3',
            'scaleNumber': 1,
            'dnsLabelPrefix': self.dns_label_prefix
        }
        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            'azure-sample',
            deployment_properties
        )
        deployment_async_operation.wait()

    def getIPAddress(self):
        return self.network_client.public_ip_addresses.get(self.resource_group, "publicip" ).ip_address

    def stopMachines(self):
        scaleNumber = 1
        async_vm_stop = []
        async_vm_stop.append(self.compute_client.virtual_machines.power_off(self.resource_group, 'master'))
        for vm_index in range(scaleNumber):
            async_vm_stop.append(self.compute_client.virtual_machines.power_off(self.resource_group, "worker{0}".format(vm_index)))

        for wait_index in range(scaleNumber + 1):
            async_vm_stop[wait_index].wait()

    def resumeMachines(self):
        scaleNumber = 1
        async_vm_resume = []
        async_vm_resume.append(self.compute_client.virtual_machines.start(self.resource_group, 'master'))
        for vm_index in range(scaleNumber):
            async_vm_resume.append(self.compute_client.virtual_machines.start(self.resource_group, "worker{0}".format(vm_index)))

        for wait_index in range(scaleNumber + 1):
            async_vm_resume[wait_index].wait()

    def destroy(self):
        """Destroy the given resource group"""
        self.client.resource_groups.delete(self.resource_group)
