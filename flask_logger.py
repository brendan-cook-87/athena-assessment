import inspect
import json
import boto3
import time
import uuid
from config import *

def log_message(message, type='default', severity='normal'):
    log = {
        'message' : f"{message}",
        'type' : f"{type}",
        'severity' : f"{severity}",
        'caller' : f"{inspect.stack()[2][3]}",
        'timestamp' : f"{time.strftime('%Y-%m-%d : %H:%M:%S')}"
    }

    s3 = boto3.resource('s3')
    s3object = s3.Object(primary_bucket, f'logs/{uuid.uuid4()}.json')
    s3object.put(
        Body=(bytes(json.dumps(log).encode('UTF-8')))
    )


