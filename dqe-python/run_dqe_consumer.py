import sys
from os import path
import json
from base64 import b64encode
import requests
import time
import asyncio
import psycopg2
import sqlanydb
from config import *
from  get_tpt_id import call_graphql_api,call_dqe 
import psycopg2
import datetime
from datetime import timedelta

env = {
    #'DATA_SOURCE': 'JSON',
    'DATA_SOURCE': 'GRAPHQLAPI',
    
}

tpt_id_key_list = []

###########################
#### main function entry point
##########################
if __name__ == "__main__" :
    
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
    # TODO get credentials from vault

    postgresConnection= psycopg2.connect(user='fstapcdevteam', host='localhost',
    port=9003, password='FstApc2021FSTAPC2021', database='scoutdb')
    cursor = postgresConnection.cursor()
    time_now = datetime.datetime.utcnow()
    time_before = time_now - timedelta(hours = 2.5)
    #yyyy-mm-dd hh:mm:ss
    sql_st1 = "select distinct tpt_id_key from dqe_consumer.insert_tpt_id where create_date >= '{}'".format(time_before.strftime('%Y-%m-%d %H:%M:%S'))
    cursor.execute(sql_st1)

    tpt_ids = cursor.fetchall()

    for key in tpt_ids :
        for k in key:
            print(k)
            tpt_id_key_list.append(k)

    #print(tpt_id_key_list)
    

    cursor.close() 
    postgresConnection.close()
    #print(postgresConnection)
   



    ## STEP 1  Calling DQE 

        
    for item in tpt_id_key_list:
        print(env["DATA_SOURCE"])

        if env['DATA_SOURCE'] == 'GRAPHQLAPI':
            data = call_graphql_api(item)

        if env['DATA_SOURCE'] == 'JSON':
            with open('C:/Users/gluzo/Documents/Projects/dqe_python_airflow/dqe-python/tdcompleteness.json', 'r') as f1:
                data = json.load(f1)
            data = {
                    "data" : data
                }

        input_dqe = data
        input_dqe['tests'] = [{"TDCompleteness" : {}
            }]


        _score, tpt_id_key = call_dqe(data, item)
        print(_score, tpt_id_key)


            
        
