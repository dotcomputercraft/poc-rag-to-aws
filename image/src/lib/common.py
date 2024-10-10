import datetime
import json
import logging
import os
import random
import threading
import traceback
import sys

import boto3
from lib.constants import aws_region, ACCESS_KEY, SECRET_KEY

LOGGER = logging.getLogger()


def set_logging(logger):
    # Setup Logging
    FORMAT = '%(lineno)s %(levelname)s:%(name)s %(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT)

    if os.getenv('STAGE') == 'dev' or os.getenv('VERBOSE', '').lower() in ('true', '1'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('nose').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_secret(key):
    client = get_boto3_session().client('ssm',
                                        region_name=aws_region,
                                        aws_access_key_id=ACCESS_KEY,
                                        aws_secret_access_key=SECRET_KEY, )
    resp = client.get_parameter(
        Name=key,
        WithDecryption=True
    )

    return resp['Parameter']['Value']



def get_lambda_client():
    if os.getenv('IS_OFFLINE'):
        return get_boto3_session().client('lambda', region_name='localhost', endpoint_url='http://localhost:3000')
    else:
        return get_boto3_session().client('lambda')


def get_boto3_session():
    # boto3 is not thread-safe
    d = threading.local()
    if not hasattr(d, 'boto3_session'):
        if os.getenv('IS_OFFLINE') == 'true':
            LOGGER.info("Using offline dynamo endpoint")
            d.boto3_session = boto3.session.Session(region_name='localhost')
        else:
            d.boto3_session = boto3.session.Session()
    return d.boto3_session


def get_account_info():
    account_info_for_gcp_provision = None
    try:
        account_info_for_gcp_provision = get_secret(SQS_ACCOUNT_INFO)
        # LOGGER.info(f"account_info_for_gcp_provision={account_info_for_gcp_provision}")
        account_info = json.loads(account_info_for_gcp_provision)

    except Exception as e:
        traceback.print_exc()
        LOGGER.error(e)

    return account_info

def get_s3_account_info():
    account_info_for_gcp_provision = None
    try:
        account_info_for_gcp_provision = get_secret(S3_ACCOUNT_INFO)
        # LOGGER.info(f"account_info_for_gcp_provision={account_info_for_gcp_provision}")
        account_info = json.loads(account_info_for_gcp_provision)

    except Exception as e:
        traceback.print_exc()
        LOGGER.error(e)

    return account_info

