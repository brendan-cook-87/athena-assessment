import boto3
from botocore.config import Config
import time
from pandas.io.json import json_normalize
from unicodedata import normalize
import json
import pandas as pd
from flask_logger import log_message

def get_query_results(query_str):
    db_name='bcook-assessment'
    prod = boto3.session.Session()

    config=Config()
    client = prod.client('athena', region_name='ap-southeast-2', config=config)

    def results_to_df(results):
        columns = [
            col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']
        ]
        listed_results = []
        for res in results['ResultSet']['Rows'][1:]:
            values = []
            for field in res['Data']:
                try:
                    values.append(list(field.values())[0])
                except:
                    values.append('')
            listed_results.append(dict(zip(columns, values)))
        return listed_results


    response = client.start_query_execution(
        QueryString=query_str,
        QueryExecutionContext={
            'Database': db_name
        },
        WorkGroup='primary'
    )

    r2 = client.get_query_execution(
        QueryExecutionId=response['QueryExecutionId']
    )

    while r2['QueryExecution']['Status']['State'] in ['QUEUED', 'RUNNING']:
        r2 = client.get_query_execution(
            QueryExecutionId=response['QueryExecutionId']
        )
        time.sleep(1)

    if r2['QueryExecution']['Status']['State'] == 'SUCCEEDED':
        token = None
        df = None
        result = client.get_query_results(
            QueryExecutionId=response['QueryExecutionId']
        )
        df = json_normalize(
            results_to_df(result)
        )

        try:
            while True:
                token = result['NextToken']
                result = client.get_query_results(
                    QueryExecutionId=response['QueryExecutionId'],
                    NextToken=token
                )
                df = pd.concat([df, json_normalize(
                    results_to_df(result)
                )])
        except KeyError:
            pass
    else:
        message = 'Athena query failed: {}'.format(response['QueryExecutionId'])
        log_message(message, type='Exception', severity='high')
        raise Exception(message)

    return df

def getEquitableOwner_internal(id):
    query_str=f'''
        with a AS 
        (SELECT id,
            transaction_date,
            loan_account_id
        FROM accounting_entry
        WHERE id='{id}')
            SELECT *
    FROM a
    LEFT JOIN equitable_owner_history
    ON a.loan_account_id = equitable_owner_history.loan_account_id AND equitable_owner_history.reallocation_date >= a.transaction_date
    ORDER BY  reallocation_date limit 1
    '''

    df = get_query_results(query_str)
    log_message(df.to_json(), type='query_result')
    print(df.to_json())
    return df['equitable_owner_id'][0]