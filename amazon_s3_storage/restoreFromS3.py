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


import boto3
import os
db_name = "Odoo14"
bucket_name = "test-webkul-erp"

s3_client = boto3.client('s3')
local_file = "/home/users/ubuntu/.local/share/Odoo/filestore/"


def download_dir(prefix, local, bucket, client):
    """
    params:
    - prefix: pattern to match in s3
    - local: local path to folder in which to place files
    - bucket: s3 bucket with target contents
    - client: initialized s3 client object
    """
    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket': bucket,
        'Prefix': prefix,
    }
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        results = client.list_objects_v2(**kwargs)
        contents = results.get('Contents')
        for i in contents:
            k = i.get('Key')
            if k[-1] != '/':
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get('NextContinuationToken')
    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))

    for k in keys:
        dest_pathname = os.path.join(local, k)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        client.download_file(bucket, k, dest_pathname)
        print (k)
    print ("=======Finish Download========")


download_dir(db_name, local_file, bucket_name, s3_client)
