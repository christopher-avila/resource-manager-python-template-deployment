from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.commerce import UsageManagementClient
from azure.mgmt.resource import SubscriptionClient
import os
import urllib2
from bs4 import BeautifulSoup
import json

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

        self.offersOutputFile = "offersCodes.json"

    def currentSubscriptionName(self):
        subscriptionClient = SubscriptionClient(self.credentials)
        for subscription in subscriptionClient.subscriptions.list():
            if subscription.state == "Enabled":
                return subscription.display_name

    def getListOfOffers(self):
        quote_page = 'https://azure.microsoft.com/es-es/support/legal/offer-details/'
        page = urllib2.urlopen(quote_page)
        soup = BeautifulSoup(page, 'html.parser')
        section = soup.find('section', attrs={'aria-label': 'Ofertas actuales'})
        data = {}
        for tr in section.find_all('tr')[2:]:
            tds = tr.find_all('td')
            data[tds[0].text] = tds[1].text
        with open(self.offersOutputFile, 'w') as outfile:
            json.dump(data, outfile)

    def getOfferDurableId(self, offerType):
        with open(self.offersOutputFile, 'r') as fp:
            offers = json.load(fp)
            return offers[offerType]

    def getRateObject(self):

        offerId = self.getOfferDurableId(self.currentSubscriptionName())

        return self.commerce_client.rate_card.get(
            "OfferDurableId eq 'MS-AZR-{offerId}' and Currency eq 'USD' and Locale eq 'en-US' and RegionInfo eq 'US'".format(offerId = offerId)
        )

price_manager = PriceManager()
price_manager.getListOfOffers()

# https://docs.microsoft.com/es-es/python/api/azure-mgmt-commerce/azure.mgmt.commerce.models.resourceratecardinfo?view=azure-python
rate = price_manager.getRateObject()

# https://docs.microsoft.com/es-es/python/api/azure-mgmt-commerce/azure.mgmt.commerce.models.meterinfo?view=azure-python
print(rate.currency)
