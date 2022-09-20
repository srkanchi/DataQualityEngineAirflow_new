# The DAG object; we'll need this to instantiate a DAG
import boto3
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonVirtualenvOperator
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta
from datetime import datetime
from airflow.utils.dates import days_ago
from pprint import pprint
from airflow.operators.python import task
from math import gcd
from cpc.query import table_names
from cpc.fstvault.vault import FstVault
from dagenvs.dagenvs import dagEnvs
from sk_demo.get_tpt_id_key import call_graphql_api, call_dqe
from sk_demo.types_of_tpt_ids import types_of_tpt_id_keys, test_tpt_ids_tds
import psycopg2
import boto3


# [START default_args]
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['jan.betermieux.ext@bayer.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1

}
# [END default_args]


@task
def batch_tptids(tpt_id_list):
    '''
    Function to split the result of tpt_id_keys into batches of size n 
    and saves to a list that contains those n batches
    
    '''

    print("Splitting tpt ids into batches ")
    
    ## list for saving batches of tpt_ids 
    batch_list = []
    n = 10
    batch_list = [tpt_id_list[i:i + n] for i in range(0, len(tpt_id_list), n)]
    #return batch_list
    print(batch_list)
    return batch_list



@task
def call_graphql_and_store_to_s3(tpt_id_key_list,my_secrets,bucket_name):
    """
    Function for passing batch list of tpt_ids to graphql api and storing the output of graphql api
    into S3 bucket in .txt format

    TODO: Add check feature and folder for type of tpt_id_key --> TD, Protocol, Trial

    
    """
    doc_type = 'TD'
    ## app_id, secret
    g_client = my_secrets['dqe_graphql']['client'] 
    g_secret = my_secrets['dqe_graphql']['secret']

    # for batch in batch_list:
    #     print("Print test of each batch")
    #     print(batch)
    #     tpt_id_key_list = batch

    ## loop through tpt_id_key from each batch

    for tpt_id_key in tpt_id_key_list:
        if doc_type == 'TD' and len(tpt_id_key) == 12:
            print('***** This is a TD test ******')
            ## get TD-0
            graphql_opt = 'TD_0'
            td_0_data = {}
            print("printing td-0 graphql output")
            td_0_data = call_graphql_api(tpt_id_key, graphql_opt,g_secret,g_client)
            print(type(td_0_data))
            print(td_0_data)

            ## get TD-1
            graphql_opt = 'TD_1'
            td_1_data = {}
            td_1_data = call_graphql_api(tpt_id_key, graphql_opt,g_secret,g_client)
            print("printing td-1 output from graphql")
            print(td_1_data)

            ### Write graphql json output of TD, protocol, Trial to text file 
            ## get current date and time
            current_datetime = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            print("Current date & time : ", current_datetime)
            str_current_datetime = str(current_datetime)

            # create a file object along with extension
            file_name =  str(tpt_id_key) + "_" + str_current_datetime  + ".txt"
            print("type of filename", type(file_name))

            ## storing data in str format in txt file
            with open(file_name,'w') as data: 
                data.write(str(td_0_data))
                data.write(str(td_1_data)) 

            #print("File created : ", file_name.name)
            
            s3_client = boto3.client('s3')

            ## upload graphql output of tpt_id_key 

            if ".txt" in file_name:
                s3_TD_url = "TrialDescriptions/" + str(file_name)
                s3_client.upload_file(file_name,bucket_name,s3_TD_url)
                print("Uploaded File with key " , s3_TD_url )
            else:
                print("File upload not successful for key" , s3_TD_url)
            #test file return 
            #return file_name



@task
def temp_storage(tpt_id_key,bucket_name, file_name):
    """
    Function for temporary storage of text files from graphql api 

    TODO: Add check feature and folder for type of tpt_id_key --> TD, Protocol, Trial

    """
    print("temp storage - efs or s3 ")

    s3_client = boto3.client('s3')

    ## upload graphql output of tpt_id_key 

    if ".txt" in file_name:
        s3_TD_url = "TrialDescriptions/" + str(file_name)
        s3_client.upload_file(file_name,bucket_name,s3_TD_url)
        print("Uploaded file")
    
    # if ".txt" in file_name:
    #     s3_TD_key = "Protocols/" + str(file_name)
    #     s3_client.upload_file(file_name,bucket_name,s3_TD_key)
    #     print("uploaded file")
    
    ## upload graphql json
    # if ".json" in file_name:
    #     s3_TD_graphql_json = "TD_graphql_json/" + str(file_name) 
    #     s3_client.upload_file(file_name,bucket_name,s3_TD_graphql_json)
    


          
@task
def get_secrets(**kwargs):

    """
    Grabbing secrets for authentication 

    """

    app_role_id = dagEnvs.APP_ROLE_ID
    app_secret_id = dagEnvs.APP_SECRET_ID
    vault2 = FstVault(app_role_id=app_role_id, app_secret_id=app_secret_id)
    config = vault2.read_secret(absolute_path="/secret/fst-apc-engineering-team/data-systems/database/postgres-scout")
    secrets = {}
    secrets['postgres'] = config
    dqe_api_call = vault2.read_secret(absolute_path="/secret/fst-apc-engineering-team/data-systems/dqe_api")
    secrets['dqe_api'] = dqe_api_call
    dqe_graphql_call = vault2.read_secret(absolute_path="/secret/fst-apc-engineering-team/data-systems/dqe_graphql")
    secrets['dqe_graphql'] = dqe_graphql_call

    print(secrets)

    return secrets


@task
def get_sql_results(my_secrets):
    """
    Sample function for running sql_query
    that grabs tpt_id_keys
    
    """
    print("Grabbing tpt_id_keys - TDs")

    # Connect Database
    postgresConnection= psycopg2.connect(user=my_secrets['postgres']['user'], host=my_secrets['postgres']['host'], port=int(my_secrets['postgres']['port']),
            password=my_secrets['postgres']['password'], database=my_secrets['postgres']['dbname'])
    cursor = postgresConnection.cursor()


    test_year = 2022 

    ## SQL query for TDs 
    sql_st1 = """Select DISTINCT 
                    ft.tpt_id_key ,
                    ft.field_year, 
                    document_type.code_value 
                    from scout_internal.field_testing ft 
                    left join scout_internal.master_code document_type on document_type.code_id = ft.field_testing_type_code_id 
                    left join scout_internal.master_code status on status.code_id = ft.status_code_id 
                    where document_type.code_value in ('TD') and 
                    status.code_value in ('0','1') AND 
                    ft.field_year in ({}) 
                    ORDER BY TPT_ID_KEY """.format(test_year)
    

    cursor.execute(sql_st1)
    result = cursor.fetchall()
    print(result)
    tpt_id_list = []

    for tup in result:
        #print(tup[0])
        #print(type(tup[0]))
        tpt_id_list.append(tup[0])

    cursor.close()
    postgresConnection.close()
    #return tpt_id_list 
    print(tpt_id_list)
    print(len(tpt_id_list))

    return tpt_id_list




with DAG(
        'Demo2_test_tpt_id_keys', 
        default_args=default_args,
        description='Demo2 on the MWAA by Jan',
        schedule_interval=timedelta(hours=2),
) as dag:
    #nests task2
   bucket_name = "fst-dqe-non-prod-storage"  
   my_secrets = get_secrets()
   tpt_id_key_list = get_sql_results(my_secrets)
   batch_list = batch_tptids(tpt_id_key_list) 
   batch_counter = 0
   for batch in batch_list:
        print("Print test of each batch")
        print(batch)
        call_graphql_and_store_to_s3(batch,my_secrets,bucket_name)
        print("Storing graphql output for batch Done" , batch_counter )
        batch_counter = batch_counter + 1    
        print(batch_counter)
#    for tids in types_of_tpt_id_keys:
#         if tids == 'TD':
#             call_graphql(batch_list,tids)
#   temp_storage(tpt_id_key,bucket_name,batch_list)