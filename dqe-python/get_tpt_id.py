from os import path
import json
from base64 import b64encode
import requests


#tpt_id_key_list = ["HA22ARG7AJPX","FD20RAP01DPR","IA22WLDDDNGX","HR21DEU500SBH1"]

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
    
    #headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization': 'Bearer {}'.format(token)}
    headers =  {'Authorization': 'Bearer {}'.format(token)}
    # sending post request and saving response as response 



    ## status 0 
    ## Correct  query
    query_status_0 = """ {
		trialDescriptions(filter: [{
		tdKeys:["%s"]
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
		} """ %(tpt_id_key)
    

    #tpt_id_key
    ## status 1 - will be different

    query_status_1 = """{
	  trialDescriptions(filter: [{
		tptIdKey:["%s"]
	  }]
	  ){
      tptIdKey
      dataDeadline
      gepCode
      gepCertification
      guidelines      
      keywords
      plannedNumberOfApplications
		  plannedNumberOfAssessments			      
			     
      controlFieldCode
      plannedAssessments{
        partRated
        sampleSize
        sampleSizeUnit
        ratingDataType
        standardEvaluationId
        assessmentCode
        target{
          name
        }
        crop{
          name
        }

      }
      
      treatments{
        
        applications{
          crops{
            cropStageCode
          }
          applicationCode
          applicationTiming
          products{
            equipment{
              method
              placement
            }
          }
        }
      }
      
    }  
	  }""" %(tpt_id_key)

 
    ## trial queries
    ## protocol queries 
     

    ## check or try catch for correct status 

    r = requests.post(url = API_ENDPOINT,headers=headers,json={"query": query_status_1})
    #print(r.text)
    return r.json()
  



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

    res = requests.post(url = API_ENDPOINT, data=json.dumps(data), headers=headers) 
    # extracting response text  

    pastebin_url = res.text 

    
    #return r --> res
    rtn = res.text
    #print("Return from method dqe",rtn)
    json_rtn = json.loads(rtn)
    
    
    try :
        json_rtn = json.loads(rtn)
        #print(json_rtn)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        print("Decoding JSON has failed")

    _score = json_rtn[0]['TDCompleteness_1']['scores']
    _version = json_rtn[0]['TDCompleteness_1']['version']
    return _score,_version ,tpt_id_key,json_rtn
    #return json_rtn


