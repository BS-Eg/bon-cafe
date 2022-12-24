# Before we start , Make sure you notice down your S3 access key and S3 secret Key.
# 1. AWS Configure
#
# Before we could work with AWS S3. We need to configure it first.
#
#     Install awscli using pip
#
# pip install awscli
#
#     Configure
#
# aws configure
# AWS Access Key ID [None]: input your access key
# AWS Secret Access Key [None]: input your secret access key
# Default region name [None]: input your region
# Default output format [None]: json
#
#     Verifies
#
# aws s3 ls
#
# if you see there is your bucket show up. it mean your configure is correct. Ok, Now let's start with upload file.

import os
import boto3

#config file here

db_name = "odoo"
os.environ['AWS_ACCESS_KEY_ID'] = "XXXXXXXXXXXXXXXX"
os.environ['AWS_SECRET_ACCESS_KEY'] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
region = 'us-east-1'
path = "/opt/odoo/.local/share/Odoo/filestore/" + db_name
bucket_name = "bucketname"


s3 = boto3.client('s3',region_name=region)
for r, d, f in os.walk(path):
    for file in f:
        path = os.path.join(r, file)
        fname = path.split("filestore/")[1]
        s3.upload_file(path, bucket_name, fname)
        print(fname)
print("---upload finish-----")


# https://qiita.com/hengsokvisal/items/329924dd9e3f65dd48e7
