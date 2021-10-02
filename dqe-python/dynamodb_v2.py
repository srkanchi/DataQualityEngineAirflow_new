from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key
# boto3.setup_default_session(profile_name='saml')
#awsid = boto3.client('sts').get_caller_identity()
#print("AWS get_caller_identity:", awsid)

## query tpt_id_key and sorted by timestamp
def query_tpt_id_key(tpt_id_key, limt_num, dynamodb=None):
    
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    awsid = boto3.client('sts').get_caller_identity()
    print("AWS get_caller_identity:", awsid)

    table = dynamodb.Table('dqe_results')

    ## query tpt_id_key, order by trial_year, descending
    response = table.query(
        ScanIndexForward=False,
        Limit=limt_num,
        KeyConditionExpression=Key('tpt_id_key').eq(tpt_id_key)  
    )
    return response['Items']


if __name__ == '__main__':
    tpt_id_key = "FA21WLD9DLTX" # 'SE11DEU41BPKI1'
    limt_num = 10
    rtn_items = query_tpt_id_key(tpt_id_key, limt_num)
    print('len of results:', len(rtn_items))
    for x in rtn_items:
        print('========================')
        print([x['tpt_id_key'], x['trial_year'], x['timestamp'], x['dqe_results'] ])
        # pprint(x['info'], depth=1, width=1, indent=1 )