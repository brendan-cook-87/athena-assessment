from util import *
import requests
import pytest

def test_good1():
    expected_result = "0017F00000rC0PQQA0 Trust No. 5"
    actual_result = getEquitableOwner_internal('a9c7F000000Cc0PQAS')
    assert(actual_result == expected_result)

def test_good2():
    expected_result = "0017F00001xtulBQAQ Trust No. 3"
    actual_result = getEquitableOwner_internal('a9c7F000000GsJ7QAK')
    assert(actual_result == expected_result)

def test_good3():
    expected_result = "0017F00000lIAbbQAG Trust No. 4"
    actual_result = getEquitableOwner_internal('a9c7F0000004EIiQAM')
    assert(actual_result == expected_result)

def test_none():
    with pytest.raises(KeyError, match=r'equitable_owner_id'):
        getEquitableOwner_internal(None)

def test_unknownid():
    with pytest.raises(KeyError, match=r'equitable_owner_id'):
        getEquitableOwner_internal('asdf')


def test_api_good1():
    request_str = 'http://ec2-13-211-206-33.ap-southeast-2.compute.amazonaws.com:5000/getEquitableOwner/a9c7F000000Cc0PQAS'

    response = requests.get(request_str)

    expected_result = {
        "AccountingEntryId": "a9c7F000000Cc0PQAS",
        "EquitableOwner": "0017F00000rC0PQQA0 Trust No. 5"
    }

    assert(response.status_code == 200)
    assert(response.json() == expected_result)

def test_api_good2():
    request_str = 'http://ec2-13-211-206-33.ap-southeast-2.compute.amazonaws.com:5000/getEquitableOwner/a9c7F000000GsJ7QAK'

    response = requests.get(request_str)

    expected_result = {
        "AccountingEntryId": "a9c7F000000GsJ7QAK",
        "EquitableOwner": "0017F00001xtulBQAQ Trust No. 3"
    }

    assert(response.status_code == 200)
    assert(response.json() == expected_result)

def test_api_good3():
    request_str = 'http://ec2-13-211-206-33.ap-southeast-2.compute.amazonaws.com:5000/getEquitableOwner/a9c7F0000004EIiQAM'

    response = requests.get(request_str)

    expected_result = {
        "AccountingEntryId": "a9c7F0000004EIiQAM",
        "EquitableOwner": "0017F00000lIAbbQAG Trust No. 4"
    }

    assert(response.status_code == 200)
    assert(response.json() == expected_result)

def test_none():
    request_str = 'http://ec2-13-211-206-33.ap-southeast-2.compute.amazonaws.com:5000/getEquitableOwner/'

    response = requests.get(request_str)

    assert(response.status_code == 404)

def test_unknownid():
    request_str = 'http://ec2-13-211-206-33.ap-southeast-2.compute.amazonaws.com:5000/getEquitableOwner/asdf'

    response = requests.get(request_str)

    expected_result = {
        "AccountingEntryId": "asdf",
        "Error": 500
    }

    assert(response.status_code == 500)
    assert(response.json() == expected_result)

def test_unknownid2():
    request_str = 'http://ec2-13-211-206-33.ap-southeast-2.compute.amazonaws.com:5000/getEquitableOwner/-9'

    response = requests.get(request_str)

    expected_result = {
        "AccountingEntryId": "-9",
        "Error": 500
    }

    assert(response.status_code == 500)
    assert(response.json() == expected_result)
