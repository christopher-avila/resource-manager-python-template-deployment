# Using this package which is a HTTP library
import requests
import os

# Parameters need for API
subscription = os.environ.get('AZURE_SUBSCRIPTION_ID', '11111111-1111-1111-1111-111111111111')   # your Azure Subscription Id
token = ''
offer = 'MS-AZR-0003P'
currency = 'USD'
locale = 'en-US'
region = 'US'
rateCardUrl = "https://management.azure.com:443/subscriptions/{subscriptionId}/providers/Microsoft.Commerce/RateCard?api-version=2016-08-31-preview&$filter=OfferDurableId eq '{offerId}' and Currency eq '{currencyId}' and Locale eq '{localeId}' and RegionInfo eq '{regionId}'".format(subscriptionId = subscription, offerId = offer, currencyId = currency, localeId = locale, regionId = region)

# Don't allow redirects and call the RateCard API
response = requests.get(rateCardUrl, allow_redirects=False, headers = {'Authorization': 'Bearer %s' %token})

# Look at response headers to get the redirect URL
# print response.headers['Location']
redirectUrl = response.headers['Location']
# print(redirectUrl)

# Get the ratecard content by making another call to go the redirect URL
rateCard = requests.get(redirectUrl)

# Print the ratecard content
print(rateCard.content)
