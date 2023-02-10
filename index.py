import boto3
import logging
from botocore.exceptions import ClientError

BUCKET_NAME = "osuapp-winter2023"
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # parse json in event to get key
    key = event['Records'][0]['s3']['object']['key']

    print('filename: ' + key)

    # Set the source bucket name
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

    # copy a file from one S3 bucket to another S3 bucket
    # src_bucket_path = 's3://sourcebucket'
    # tgt_bucket_path = 's3://targetbucket'
    # src_file_name = 'sourcefile.txt'
    # tgt_file_name = 'targetfile.txt'
    # src_bucket_path + '/' + src_file_name = s3://sourcebucket/sourcefile.txt
    # tgt_bucket_path + '/' + tgt_file_name = s3://targetbucket/targetfile.txt
    print('src' + src_file_name)
    print('tgt' + tgt_file_name)

    # TODO: download the file from s3 locally
    response = s3.get_object(Bucket=BUCKET_NAME, Key='metadata.csv')
    file_content = response['Body'].read().decode('utf-8')

    with open('/tmp/file.stl', 'w') as f:
        f.write(file_content)
        
    localFileName = "/tmp/file.stl"
    upload_to_s3(localFileName, tgt_file_name)

    # file name with extension
    localFileName = os.path.basename('/root/file.ext')
    # file name without extension
    print(os.path.splitext(file_name)[0])

    create_presigned_url(tgt_file_name)

    # TODO: download metadata.csv and save to lambda temp folder
    response = s3.get_object(Bucket=BUCKET_NAME, Key='metadata.csv')
    file_content = response['Body'].read().decode('utf-8')
    new_file_content = 'new_file_name,new_metadata\n'

    with open('/tmp/metadata.csv', 'w') as f:
        # append metadata.csv with new file name and metadata
        f.write(new_file_content)
    

    # TODO: upload metadata.csv to s3
    upload_to_s3('/tmp/metadata.csv', 'metadata.csv')


# upload local file to s3 bucket
# local_file - name of local file
# s3_file - name that file will be uploaded with to s3 bucket
def upload_to_s3(local_file, s3_file):
    try:
        s3.upload_file(local_file, BUCKET_NAME, s3_file)

        print("Upload Successful", url)
        return None
    except FileNotFoundError as e:
        print("File not found: ", e)
        return e
    except NoCredentialsError as e:
        print("Credentials not available", e)
        return e

def create_presigned_url(key_object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': key_object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response