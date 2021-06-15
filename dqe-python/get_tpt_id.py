import sys
from os import path
import json
from base64 import b64encode
import requests
import asyncio
import psycopg2
import sqlanydb
from config import *
from base64 import b64encode



def call_graphql_api(tpt_id_key):

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


    # defining the api-endpoint  
    API_ENDPOINT = "https://fst-graphql-dev.agro.services/graphql"
    
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization': 'Bearer {}'.format(token)}
    # sending post request and saving response as response object 
    
    query =  """query{
        trialDescriptions(filter:[{
            tdKeys:["HD21RAPC2RFR"]
        }]){
        
            tdKey
                crops{
            name
            }
            keywords
            fieldTestingType
            projectNumbers
            fieldResponsibles{
            type
            }
            siteType
            plotArea
            plannedTotalNumberOfTrials
            experimentalSeason
            targets{
            name
            }
            externalField
        }
        }"""



    r = requests.post(url = API_ENDPOINT,headers=headers,data=json.dumps({"query":query}))
    #print(r.text)
    return r.text
  



def call_dqe(data, tpt_id_key):
    
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


    # defining the api-endpoint  
    API_ENDPOINT = "https://fst-dqe-dev.agro.services/run"
    
    # with open('./tdcompleteness.json') as json_file:
    #     data = json.load(json_file)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization': 'Bearer {}'.format(token)}

    
    # sending post request and saving response as response object 

    r = requests.post(url = API_ENDPOINT, data=json.dumps(data), headers=headers) 
    print(r)
    # extracting response text  

    pastebin_url = r.text 

    print("The pastebin URL is:%s"%pastebin_url)

    #return r 
    rtn = r.text
    json_rtn = json.loads(rtn)
 
    _score = json_rtn[0]['TDCompleteness']['score']
    return _score, tpt_id_key




def save_to_json(data):
    pass

def send_email(sender, receiver, html):
    pass

def summ_for_1_tpt(dqe_response, tpt_id_key, score):
    # tpt_id_key | quality_score | responsible_name | email
   
    
    #postgresConnection = psycopg2.connect(user='fstapcdevteam', host='localhost', port=9003, password='FstApc2021FSTAPC2021', database='scoutdb')
    con = sqlanydb.connect(uid=USER, pwd=PWD, host='10.205.43.162')
    cursor = con.cursor()


    sql_query = "select distinct top 100 \
        ft.tpt_id_key \
        , fr.responsible_name \
        , fr.email \
        , mc.decode1 as responsible_type \
        , u.mail_id \
        from \
        field_testing ft \
        join field_responsible fr on fr.field_testing_id=ft.field_testing_id \
        join master_code mc on mc.code_id=fr.responsible_type_code_id \
        join arm_users u on u.responsible=fr.responsible_name \
        where 1=1 \
        and mc.decode1 = 'Technical Manager' \
        and ft.tpt_id_key = '{}' ".format(tpt_id_key)
    
    cursor.execute(sql_query)
    output = cursor.fetchall()
    
    cursor.close()
    con.close()
    print(con)


    return {'tpt': tpt_id_key, 'quality_score': score, 'user': output[0][1], 'email': output[0][4]}



def summarize_per_resonsible(return_list):
    ##email of tm 
    pass 

return_list = []




    #return_list.append(rules)
    # save_to_json(return_list)
    # iter_email_sender = summarize_per_resonsible(return_list)


# for item in iter_email_sender:
#     send_email(item['sender'], item['receiver'], item['html'])