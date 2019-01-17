from azure.mgmt.commerce import UsageManagementClient
from azure.common.credentials import ServicePrincipalCredentials
import os

class PriceManager(object):
    def __init__(self):
        self.subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID', '11111111-1111-1111-1111-111111111111')

        self.credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID']
        )

        self.commerce_client = UsageManagementClient(
            self.credentials,
            self.subscription_id
        )

    def getOfferDurableId(self):


    def getRateObject(self):
        return self.commerce_client.rate_card.get(
            "OfferDurableId eq 'MS-AZR-0003P' and Currency eq 'USD' and Locale eq 'en-US' and RegionInfo eq 'US'"
        )

price_manager = PriceManager()
# https://docs.microsoft.com/es-es/python/api/azure-mgmt-commerce/azure.mgmt.commerce.models.resourceratecardinfo?view=azure-python
rate = price_manager.getRateObject()

# https://docs.microsoft.com/es-es/python/api/azure-mgmt-commerce/azure.mgmt.commerce.models.meterinfo?view=azure-python
print(rate.currency)
