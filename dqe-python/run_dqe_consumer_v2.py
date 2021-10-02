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

#tpt_id_key_list = []
tpt_ids_dict = {}


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
    # v = FstVault(aws_auth=True, aws_fort_knox_role='fst-apc-engineering-team-ecstaskexecutionrole', aws_arn=None) 
    # config = v.read_secret('data-systems/database/postgres-scout')

    # postgresConnection= psycopg2.connect(user=config['user'], host=config['host'], port=int(config['port']),
    #    password=config['password'], database=config['dbname'])

    # cursor = postgresConnection.cursor()

    postgresConnection = psycopg2.connect(user='fstapcdevteam', host='localhost', port=9003, password='FstApc2021FSTAPC2021', database='scoutdb') 
    cursor = postgresConnection.cursor()

    time_now = datetime.datetime.utcnow()
    time_delta1 = time_now - timedelta(hours = 18)
    time_delta2 = time_delta1 - timedelta(hours = 2.5)

    test_code = 1

    if test_code == 0:
        #yyyy-mm-dd hh:mm:ss
        sql_st1 = "select distinct tpt_id_key , create_date from dqe_consumer.insert_tpt_id where create_date >= '{}' and create_date <= '{}'".format(time_delta2.strftime('%Y-%m-%d %H:%M:%S'), time_delta1.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(sql_st1)
        tpt_ids = cursor.fetchall()

        
        tpt_ids_dict = dict(tpt_ids)
        print("length of tpt dict printing", len(tpt_ids_dict))
        ## key contains tpt_id_key and val contains timestamp 
        for key,val in tpt_ids_dict.items():
                ## length of tpt_id == 12 for TD
                if len(key[0]) == 12:
                    print(key)
                    print(val.year)
                    

        cursor.close() 
        postgresConnection.close()
    
    elif test_code == 1:
        #tpt_ids_dict = {"ID21ARGM1JWR" : 2021}
        tpt_ids_dict = {"IA25WLDAGKVX":2021,"ID21ARGM1JWR":2021,"FA21WLDVRLTX":2021,"SD21ARGD6GGR":2021,"FR21EUR43KTR":2021}
    

    elif test_code == 2:
        print(test_code) 
        sql_st2 = "select distinct tpt_id_key, create_date from dqe_consumer.insert_tpt_id limit 10"
        cursor.execute(sql_st2)
        tpt_ids = cursor.fetchall()

        tpt_ids_dict = dict(tpt_ids)
        print("length of tpt dict printing", len(tpt_ids_dict))
        ## key contains tpt_id_key and val contains timestamp 
        for key,val in tpt_ids_dict.items():
                ## length of tpt_id == 12 for TD
                if len(key[0]) == 12:
                    print(key)
                    print(val.year)
                    

        cursor.close() 
        postgresConnection.close()
    


    ## STEP 1  Calling GraphQL 
    ### Passing tptids through GRAPHQL api

    #item = 'HA22EUR7LJPX'
    time_1 = time.time()
    counter = 0

    #tpt_id_key = tpt_id_key_test

    #for item in tpt_id_key_list:
    for tpt_key,val in tpt_ids_dict.items():
        if len(tpt_key) == 12:
            if test_code == 0:
                cur_year = val.year
            elif test_code == 1:
                cur_year = 2021    

            if env['DATA_SOURCE'] == 'GRAPHQLAPI':
                data = call_graphql_api(tpt_key)
                #data = call_graphql_api(tpt_id_key_test)
                #print(data)
            
                try:
                    input_dqe = data

                    # input_dqe['tests'] = [{"TDCompleteness" : {}
                    #     }]

                    ## STEP 2 - DATA QUALITY ENGINE 


                    td_desc = input_dqe.get('data')
                    check_list = td_desc.get('trialDescriptions')
                    print(check_list)
                    input("---- test2 -- checklist -----")
                    
                    if check_list:
                        
                        # input_dqe['tests'] = [ 
                        # #     { "TDCompleteness_0": {
                        # # "attributeMapping": "/home/ubuntu/DataQualityEngine/tests/Files/attribute_mapping_0.py",
                        # # "weights": "/home/ubuntu/DataQualityEngine/tests/Files/completeness_TD_V1_0_0.csv",
                        # # "version": "completeness_TD_V1_0_0"
                        # #}}]
                        # # } }
                        # # ,
                        # { "TDCompleteness_1": {
                        # "attributeMapping": "/home/ubuntu/DataQualityEngine/tests/Files/attribute_mapping_TD_1.py",
                        # "weights": "/home/ubuntu/DataQualityEngine/tests/Files/completeness_TD_V1_0_0.csv",
                        # "version": "completeness_TD_V1_0_0"
                        # }}
                        # ]
                        
                        input_dqe['tests'] = [{ "TDCompleteness_1": {
                        "attributeMapping": "/home/ubuntu/DataQualityEngine/tests/Files/attribute_mapping_TD_1.py",
                        "weights": "/home/ubuntu/DataQualityEngine/tests/Files/completeness_TD_V1_0_0.csv",
                        "version": "completeness_TD_V1_0_0"
                        }}
                        ]



                            
                        ## add rule name nd version to the result for dqe db 
                        _score,_version ,tpt_id_key ,json_return = call_dqe(input_dqe, tpt_key)
                        #json_return,tpt_id_key = call_dqe(input_dqe, tpt_key)
                        #print(call_dqe(data,item))
                        #print(_score, tpt_id_key) 
                        #results =  _score,_version ,tpt_id_key 
                        # print(json_return) 
                        input("---- test 1, json return------")

                        ## STEP 3 - STORING TO DYNAMODB 
                        
                        year = cur_year
                        curr_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
                        dqe_results = json_return
                        # #print("Json return ", json_return)
                        doc_type = 'TD'
                        # dqe_score = -1
                        dqe_score = _score["general"]["0"]["raw"] # score
                        print("dqe_score", dqe_score)
                        response = put_one_dqe_item(tpt_id_key, year, dqe_results, curr_timestamp, doc_type, dqe_score, table_name)
                        # print("Response print ",response)
                        counter = counter + 1       
                        print("Counter: " , counter)
                        input('***end of testing***')
                    
                except Exception as e:
                    print(e)
                    if not check_list:
                        print(not check_list)
                        print("List is empty so can't create result")

    ## STEP 4 - TIME CHECK 
    time_2 = time.time() 
    total_time = time_2 - time_1
    print(total_time)   