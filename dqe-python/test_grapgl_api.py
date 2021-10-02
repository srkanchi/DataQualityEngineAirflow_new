import requests 

import json

from base64 import b64encode


client_secret = "a9~_.MGuol6UnGu5VJo357h~u_zPuJT58n"
app_id = "b4fd365f-23e4-4fb9-a2ed-1cf01d38ab17"
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
token = get_token(url, app_id, client_secret)['access_token']

print(token)

# defining the api-endpoint  
API_ENDPOINT = "https://fst-graphql-dev.agro.services/graphql"
  
headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization': 'Bearer {}'.format(token)}
# sending post request and saving response as response object 


query = """ query{
trialDescriptions(filter: [{
tdKeys:["HA22ARG7AJPX"]
}]
){
tptIdKey
siteType
trialResponsibles{
siteName
internalValue
testType
hasName
plannedNumberOfTrials
}
plannedNumberOfApplications
numberOfReplicates
crops{
name
}
targets{
name
}
experimentalSeason
keywords
projectNumbers
}
}"""


r = requests.post(url = API_ENDPOINT,headers=headers,data=json.dumps({"query":query}))
print(r)
