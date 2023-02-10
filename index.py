import boto3
# presiged url trigger
import json
import logging
from botocore.exceptions import ClientError


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


# upload_test_jeff2
# import boto3
# import os
# import json

BUCKET_NAME = "osuapp-winter2023"


def lambda_handler(event, context):
    # parse json in event to get key
    key = json.loads(event)['Records'][0]['s3']['object']['key']

    # Create a connection to S3
    s3 = boto3.client('s3')
    # Set the bucket name where the file is stored
    # bucket_name = BUCKET_NAME
    # List all objects in the bucket
    # result = s3.list_objects_v2(Bucket=bucket_name)
    # Store the list of objects in a variable
    # objects = result.get('Contents', [])
    # sorted_objects = sorted(
    #     objects, key=lambda x: x['LastModified'], reverse=True)     # Sort the objects by date created
    # Create an array to store the names of the files in the bucket
    # filearray = [key]
    # for obj in sorted_objects:                          # For each object in the bucket
    #     # Print the key (file name)
    #     print(obj['Key'])
    #     # Add the key to the filearray variable
    #     filearray.append(obj['Key'])
    # Print the file name of the most recently created file

    print('filename: ' + key)

    # Set the source bucket name
    src_bucket_path = BUCKET_NAME
    # Set the source file name
    src_file_name = key
    if ((src_file_name.find('/')) != (-1)):             # If the filename contains a forward slash
        # Split the filename into an array
        split = src_file_name.split('/')
        # Set the target filename
        tgt_file_name = 'gltb/' + split[1]
    else:
        # Set the target filename
        tgt_file_name = 'gltb/' + src_file_name # temporarily use the same input file and send it back
        pass
    tgt_bucket_path = BUCKET_NAME               # Set the target bucket name

    # copy a file from one S3 bucket to another S3 bucket
    # src_bucket_path = 's3://sourcebucket'
    # tgt_bucket_path = 's3://targetbucket'
    # src_file_name = 'sourcefile.txt'
    # tgt_file_name = 'targetfile.txt'
    # src_bucket_path + '/' + src_file_name = s3://sourcebucket/sourcefile.txt
    # tgt_bucket_path + '/' + tgt_file_name = s3://targetbucket/targetfile.txt
    print('src' + src_file_name)
    print('tgt' + tgt_file_name)

    # get the source file
    s3 = boto3.resource('s3')
    copy_source = {
        'Bucket': src_bucket_path,
        'Key': src_file_name
    }

    # copy the source file to the target bucket
    # s3.meta.client.copy(copy_source, tgt_bucket_path, tgt_file_name)

    # download the file
    file = 

# file_upload
# import boto3
# import json
# import zipfile


BUCKET_NAME = "osuapp-file-upload-bucket"
s3 = boto3.client('s3')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    print(bucket)
    print(key)

    # with zipfile.ZipFile('test3.zip', 'r') as zip_ref:
    #     zip_ref.extractall('')
    upload_to_s3("test.txt", "test.txt")

    return {
        'statusCode': 200,
        'body': json.dumps('file_upload lambda')
    }


# upload local file to s3 bucket
# local_file - name of local file
# s3_file - name that file will be uploaded with to s3 bucket
def upload_to_s3(local_file, s3_file):
    try:
        s3.upload_file(local_file, BUCKET_NAME, s3_file)
        # generates temporary link for 1 day
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_file
            },
            ExpiresIn=24 * 3600
        )

        print("Upload Successful", url)
        return url
    except FileNotFoundError:
        print("File not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None
