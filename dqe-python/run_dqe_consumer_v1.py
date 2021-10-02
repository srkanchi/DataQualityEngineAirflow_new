from os import error, path
from base64 import b64encode
import time
from  get_tpt_id import call_graphql_api,call_dqe 
import psycopg2
import datetime
from datetime import timedelta
from fstvault.vault import FstVault
import pandas as pd
from dynamo_db import put_one_dqe_item 
import json
from decimal import Decimal


env = {
    #'DATA_SOURCE': 'JSON',
    'DATA_SOURCE': 'GRAPHQLAPI',
    
}

tpt_id_key_list = []

#tpt_id_key_list = ["HA22ARG7AJPX","FD20RAP01DPR","IA22WLDDDNGX","HR21DEU500SBH1"]

# td_csv = pd.read_csv("C:/Users/gluzo/Downloads/results-20210915-141651.csv")
# tpt_id_key_list = td_csv['tpt_id_key'].to_list()
# tpt_id_key_list = tpt_id_key_list[3845:3888]


###########################
#### main function entry point
##########################
if __name__ == "__main__" :
    
    table_name = 'dqe_results'

    ## total time starter    
    start_time_exec = time.time()
    
    t1 = time.time()

    ## ge timing
    t2 = time.time() - t1
    print('Time of execution to set up variables: ', t2)
    

    ##################################
    #### begin process
    ##################################
    
    ##################################
    ## STEP 0: get tpt_ids from database 
    ##################################
    # Redshift connection params 
    #v = FstVault(aws_auth=True, aws_fort_knox_role='fst-apc-engineering-team-ecstaskexecutionrole', aws_arn=None) 
    #config = v.read_secret('data-systems/database/postgres-scout')

    #postgresConnection= psycopg2.connect(user=config['user'], host=config['host'], port=int(config['port']),
     #   password=config['password'], database=config['dbname'])

    postgresConnection = psycopg2.connect(user='fstapcdevteam', host='localhost', port=9003, password='FstApc2021FSTAPC2021', database='scoutdb') 
    cursor = postgresConnection.cursor()
    time_now = datetime.datetime.utcnow()
    time_delta1 = time_now - timedelta(hours = 18)
    time_delta2 = time_delta1 - timedelta(hours = 2.5)


    #yyyy-mm-dd hh:mm:ss
    # sql_st1 = "select distinct tpt_id_key from dqe_consumer.insert_tpt_id where create_date >= '{}' and create_date <= '{}'".format(time_delta2.strftime('%Y-%m-%d %H:%M:%S'), time_delta1.strftime('%Y-%m-%d %H:%M:%S'))
    # cursor.execute(sql_st1)

    sql_stl2 = "select distinct tpt_id_key , create_date from dqe_consumer.insert_tpt_id limit 10"
    cursor.execute(sql_stl2)
    tpt_ids = cursor.fetchall()

    for key in tpt_ids :
            ## length of tpt_id == 12 for TD
            if len(key[0]) == 12:
                tpt_id_key_list.append(key[0])
    

    cursor.close() 
    postgresConnection.close()
  
    

    ## STEP 1  Calling GraphQL 


    item = 'HA22EUR7LJPX'
    time_1 = time.time()
    counter = 0
    for item in tpt_id_key_list:

        if env['DATA_SOURCE'] == 'GRAPHQLAPI':
            data = call_graphql_api(item)
            print(data)
        
        try:
            input_dqe = data

            # input_dqe['tests'] = [{"TDCompleteness" : {}
            #     }]

            td_desc = input_dqe.get('data')
            check_list = td_desc.get('trialDescriptions')
            
            if check_list:
                
                input_dqe['tests'] = [{ "TDCompleteness_0": {
                "attributeMapping": "/home/ubuntu/DataQualityEngine/tests/Files/attribute_mapping_0.py",
                "weights": "/home/ubuntu/DataQualityEngine/tests/Files/completeness_TD_V1_0_0.csv",
                "version": "completeness_TD_V1_0_0"
                }
                }
                ]

                    
                ## add rule name nd version to the result for dqe db 
                _score,_version ,tpt_id_key ,json_return = call_dqe(input_dqe, item)
                #print(call_dqe(data,item))
                #print(_score, tpt_id_key) 
                results =  _score,_version ,tpt_id_key 
                print(results) 
                
                year = 2021
                curr_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
                dqe_results = json_return
                doc_type = 'TD'
                dqe_score = _score['rawScore'] # score
                response = put_one_dqe_item(tpt_id_key, year, dqe_results, curr_timestamp, doc_type, dqe_score, table_name)
                counter = counter + 1       
                print("Counter: " , counter)
             
        except Exception as e:
            print(e)
            if not check_list:
                print(not check_list)
                print("List is empty so can't create result")

    time_2 = time.time() 
    total_time = time_2 - time_1
    print(total_time)   


