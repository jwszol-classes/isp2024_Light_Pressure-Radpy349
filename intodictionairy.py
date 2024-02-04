from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys
import threading
import boto3
import time
import json

#s3.Object('iotstorage180281', filename).put(Body=content)

s3 = boto3.resource(
    's3',
    region_name='us-east-1',
    aws_access_key_id=None,
    aws_secret_access_key=None
)


s3 = boto3.resource('s3')
bucket = s3.Bucket('iotstorage180281')

data = {}
for index, obj in enumerate(bucket.objects.all()):
    key = obj.key
    if("core2" in key):
        keys = key.split("/")
        body = obj.get()['Body'].read()
        body = json.loads(body)

        if(keys[1] in data):
            data[keys[1]].append(body)
        else:
            data[keys[1]] = [body]
        if(index%100==0):
            print(f"Przetworzono {index} elemntów")

        
s3.Object('iotstorage180281', "fajny_slownik.json").put(Body=json.dumps(data, indent = 4))
        
        


