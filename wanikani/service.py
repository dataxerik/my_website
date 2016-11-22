import re
import requests
import json

def is_valid_api_key(api_key):
    return re.fullmatch('[0-9a-zA-Z].{31}$', api_key)

def get_api_information(api_key):
    url = 'https://www.wanikani.com/api/v1.4/user/{0}/user-information'.format(api_key)
    print(url)
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data
