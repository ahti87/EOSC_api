import configparser
import requests
from gevent import config

config = configparser.ConfigParser()
config.read('config.ini')


def eosc_api_get():
    url = 'https://api.eosc-portal.eu/resource/byID/ETAIS.rocket'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    print(response)


def eosc_api_put(parameters):
    url = config['EOSC_PORTAL']['eosc_portal_url']
    eosc_apikey = config['EOSC_PORTAL']['eosc_apikey']
    header = {"Content-type": "application/json",
              "Accept": "application/json",
              "Authorization": eosc_apikey}
    response = requests.post(url, json=parameters, headers=header)
    print(response.text)
    print(response.status_code)


def get_waldur_data(header):
    waldur_query_url = config['WALDUR']['waldur_query_url']
    response_json = requests.get(waldur_query_url, headers=header).json()
    # print(response_json)
    return response_json


def find_trl_level(string):
    trl = ''
    for symbol in string:
        if symbol.isdigit():
            trl = 'trl-' + symbol
        else:
            trl = 'none'
    return trl


def get_eosc_vocabularies(type, name):
    url = config['EOSC_PORTAL']['eosc_vocabulary_url']
    response_json = requests.get(url + type.upper()).json()
    if name == 'HPC':
        name = 'Compute'
    if name is None:
        name = 'Other'
    for item in response_json:
        if item['name'] == name:
            return item['id']


def main():
    waldur_token = config['WALDUR']['waldur_token']
    header = {'Authorization': 'Token {}'.format(waldur_token)}
    service_list = get_waldur_data(header)

    for element in service_list:
        print('Processing %s' % element['name'])
        service_provider = requests.get(element['customer'], headers=header).json()
        if service_provider['owners']:
            service_owner = requests.get(service_provider['owners'][0]['url'], headers=header).json()
            category_prefix = element['category_title'].replace(" ", "").lower()

            service_place = element['attributes'].get(category_prefix + '_classification_place', 'none')
            service_language = element['attributes'].get(category_prefix + '_classification_language', 'none')
            service_guide = element['attributes'].get(category_prefix + '_support_guide', 'none')
            service_portal = element['attributes'].get(category_prefix + '_support_portal', 'none')
            service_support_email = element['attributes'].get(category_prefix + '_support_email', 'none')
            service_trl = element['attributes'].get(category_prefix + '_classification_trl', 'none')

            category = get_eosc_vocabularies('category', element['category_title'])
            subcategory = get_eosc_vocabularies('subcategory', 'Other')

            scientific_domain = get_eosc_vocabularies('scientific_domain', 'Other')
            scientific_subdomain = get_eosc_vocabularies('scientific_subdomain', 'Other')

            target_users = get_eosc_vocabularies('target_user', element['attributes'].get(category_prefix + '_classification_targetusers'))

            if element['customer_name'] == 'University of Tartu':
                print(service_owner)
                parameters_eosc = {
                    "name": element['name'],
                    "resourceOrganisation": 'unitartu',
                    "resourceProviders": [
                        'unitartu'
                    ],
                    "webpage": 'https://share.neic.no/marketplace-public-offering/' + element['uuid'] + '/',
                    "description": element['full_description'],
                    "tagline": element['description'],
                    "logo": element['thumbnail'],

                    "scientificDomains": [
                        {
                            "scientificDomain": scientific_domain,
                            "scientificSubdomain": scientific_subdomain
                        }
                    ],
                    "categories": [
                        {
                            "category": category,
                            "subcategory": subcategory
                        }
                    ],
                    "targetUsers": [
                        target_users
                    ],
                    "geographicalAvailabilities": [
                        "EU"
                    ],
                    "languageAvailabilities": [
                        service_language
                    ],
                    "resourceGeographicLocations": [
                        service_place
                    ],
                    "mainContact": {
                        "firstName": service_owner['first_name'],
                        "lastName": service_owner['last_name'],
                        "email": service_owner['email'],
                    },
                    "publicContacts": [
                        {
                            "email": service_support_email,
                        }
                    ],
                    "helpdeskEmail": service_support_email,
                    "securityContactEmail": service_support_email,
                    "trl": find_trl_level(''.join(service_trl)),
                    "helpdeskPage": service_portal,
                    "userManual": service_guide,
                    "termsOfUse": element['terms_of_service'],
                    "orderType": "order_type-fully_open_access",
                }

                print(parameters_eosc)
                #eosc_api_put(parameters_eosc)


main()
#eosc_api_get()

#get_waldur_data(header={'Authorization': 'Token {}'.format(config['WALDUR']['waldur_token'])})
