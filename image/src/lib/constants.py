import os

if 'ENV' in os.environ:
    env = str(os.environ['ENV'])
else:
    env = 'local'
if 'AWS_REGION' in os.environ:
    aws_region = str(os.environ['AWS_REGION']).lower()
else:
    aws_region = None
if 'AWS_SECRET_KEY' in os.environ:
    SECRET_KEY = str(os.environ['AWS_SECRET_KEY'])
else:
    SECRET_KEY = None
if 'AWS_ACCESS_KEY' in os.environ:
    ACCESS_KEY = str(os.environ['AWS_ACCESS_KEY'])
else:
    ACCESS_KEY = None

NO_RECORDS       = "No Records to Retrieve - Number of Records Found"
WORK_IN_PROGRESS = "2"
CLOSE_COMPLETE   = "3"
CLOSE_INCOMPLETE = "4"

# You will also need to have Bedrock's model name enabled and granted for the region you are running this in.

BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
