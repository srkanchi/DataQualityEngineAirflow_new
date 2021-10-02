from pprint import pprint
import boto3
import json
from decimal import Decimal
import datetime
#boto3.setup_default_session(profile_name='default')
#boto3.client('sts').get_caller_identity()
#print("AWS get_caller_identity:", awsid)

def put_one_dqe_item(tpt_id_key, year, dqe_results, timestamp, doc_type, dqe_score, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('dqe_results')
    data_json = {
            'tpt_id_key': tpt_id_key,
            'trial_year': year,
            'timestamp': timestamp,
            'dqe_results': dqe_results,
            'doc_type': doc_type,
            'dqe_score':dqe_score
    }
    transform_json = json.loads(json.dumps(data_json), parse_float=Decimal)
    response = table.put_item( Item= transform_json)

if __name__ == '__main__':
    tpt_id_key = "IA19USAZ35UAK2"
    year = 2019
    curr_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    dqe_results = {'score': 10.5, 'missing_fields': 'dummytest'}
    doc_type = 'TD'
    dqe_score = 10.5 #dqe_results['score'] #result 
    json_info = json.loads(json.dumps(dqe_results), parse_float=Decimal)
    response = put_one_dqe_item(tpt_id_key, year, json_info, curr_timestamp, doc_type, dqe_score)
    print("Put one item succeeded:")