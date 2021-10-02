import sys
from os import path
import json
from base64 import b64encode
import requests

    
client_secret = "pLfps_g-4~RfMxXiRo5md2zOV.9I5UVVCc"
app_id = "f2fc7c38-1d57-4925-a151-2ddd4e4d2490"
url = "https://login.microsoftonline.com/fcb2b37b-5da0-466b-9b83-0014b67a7c78/oauth2/v2.0/token"


def get_token(url, app_id, client_secret):
    '''
    Azure authentication
    '''
    
    scope = app_id+'/.default'
    basic_auth = b64encode(f'{app_id}:{client_secret}'
                            .encode('ascii')).decode('ascii')
    headers = {'Authorization': f'Basic {basic_auth}'}
    payload = {'grant_type': 'client_credentials',
                'scope':scope}

    try:
        resp = requests.post(url, headers=headers, data=payload)
        resp.raise_for_status()
        return resp.json()
    except Exception as ex:
        print(ex)
        return None


    # resp = requests.post(url, headers=headers, data=payload)
    # resp.raise_for_status()
    # return resp
token = get_token(url, app_id, client_secret)['access_token']
print("token")
print(token)

# defining the api-endpoint  
API_ENDPOINT = "https://fst-dqe-dev.agro.services/run"

with open('C:\\Users\\gluzo\\Documents\\Projects\\dqe-python\\tdcompleteness.json') as json_file:
    data = json.load(json_file)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization': 'Bearer {}'.format(token)}

# sending post request and saving response as response object

input_dqe = {
        "data" : data,
        "tests" :[{"TDCompleteness" : {}
        }]
    }

r = requests.post(url = API_ENDPOINT, data=json.dumps(input_dqe), headers=headers) 
#r = requests.get(url = API_ENDPOINT, , headers=headers) 

# extracting response text  

# pastebin_url = r.text 

# print("The pastebin URL is:%s"%pastebin_url)
print(r)
rtn = r.text
print(rtn)
_score = rtn[0]['TDCompleteness']['score']
print(_score)