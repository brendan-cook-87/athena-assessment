import boto3
import time
from pandas.io.json import json_normalize
import pandas as pd
import json

from flask_logger import log_message
from config import *

from flask import Flask
from flask import render_template

from util import getEquitableOwner_internal

import traceback

app = Flask(__name__)

@app.route("/getEquitableOwner/<accountingEntryId>")
def getEquitableOwner(accountingEntryId):
    try:
        log_message(f'/getEquitableOwner/{accountingEntryId}', type='api_call')
        print(f'/getEquitableOwner/{accountingEntryId}')
        owner = getEquitableOwner_internal(accountingEntryId)
        result = {
            'AccountingEntryId': accountingEntryId,
            'EquitableOwner': owner
        }

        log_message(json.dumps(result), type='api_result')
        print(json.dumps(result))

        return result
    except:
        message = traceback.format_exc()
        result = {
            'AccountingEntryId': accountingEntryId,
            'Error': 500
        }
        log_message(message, type='Exception', severity='High')

        return result, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


