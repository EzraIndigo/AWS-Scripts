import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import datetime
import json
from botocore.vendored import requests

#Author - Ezra Wilton
#A script which looks into each AWS Account within an Organization and returns the IAM Users in each via monolithic JSON & uploads to S3
#Requires CF Role/Policy to be deployed to member accounts 

def lambda_handler(event, context):
    confirmation = ""
    #setup boto3 clients with current Lambda role/permissions
    orgs = boto3.client('organizations')
    s3 = boto3.client('s3')
    
    #Get all accounts within Org
    resp = orgs.list_accounts()
    accountsList = resp['Accounts']
    numAccounts = len(accountsList)
    s3_iam_users_list = []
    
    #For each account, loop and call function to get IAM Users in each account and build big dict of all IAM Users
    for account in accountsList:
        id = account['Id']
        iam_users = getIamUsers(id)
        s3_iam_users_list.append(iam_users)
    #convert to json with datetime handler for funky AWS datetime formats    
    iam_json = json.dumps(s3_iam_users_list, default=datetime_handler, indent=4)
    #upload data to an S3 bucket
    try:
        upload_s3 = s3.put_object(
        Bucket = 'BUCKET-NAME',
        Key = "Users.json",
        Body = iam_json,
        ACL = 'bucket-owner-full-control'
        )
        confirmation = "Uploaded to S3"
    except ClientError as e:
        confirmation = e
    return {
        'statusCode': 200,
        'body': iam_json,
        'uploaded?': confirmation
    }
    
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

#called for each account in Org
#uses role deployed in each account via CF via trust relationship back to Lambda role so lambda can assume
#dips into each account, calls IAM users list & account ID and adds to Dict, returns data
def getIamUsers(id):
    sts = boto3.client('sts')
    assumeRole = sts.assume_role(
        RoleArn= "arn:aws:iam::" + id + ":role/IamAuditor",
        RoleSessionName="AssumeRoleSession1"
        )
    creds = assumeRole['Credentials']
    iam = boto3.client(
        'iam',
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken']
        )
    iam_resp = iam.list_users()
    if iam_resp['ResponseMetadata']:
        del iam_resp['ResponseMetadata']
    iam_resp['AccountID'] = id
    return iam_resp
    
    
        