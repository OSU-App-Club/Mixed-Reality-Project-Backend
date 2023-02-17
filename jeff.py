import boto3
import os
import json
import zipfile

# upload bucket = source, where files uploaded
# download bucket = destination (re-upload after file conversion)

def lambda_handler(event, context):
  s3 = boto3.client('s3')
  bucket_name = 'osuapp-winter2023-new-upload'
  result = s3.list_objects_v2(Bucket=bucket_name)
  objects = result.get('Contents', [])
  sorted_objects = sorted(objects, key=lambda x: x['LastModified'], reverse=True)
  filearray=[]
  for obj in sorted_objects:
    print(obj['Key'])
    filearray.append(obj['Key'])
  print('filename: ' + filearray[0])
  
  src_bucket_path = 'osuapp-winter2023-new-upload'
  src_file_name = filearray[0]
  tgt_file_name = filearray[0]
  tgt_bucket_path = 'osuapp-winter2023-new-download'
  
  
  print('src' + src_file_name)
  print('tgt' + tgt_file_name)
      
  
  s3 = boto3.resource('s3')
  copy_source = {
  'Bucket': src_bucket_path,
  'Key': src_file_name
  }
 
  s3.meta.client.copy(copy_source, tgt_bucket_path, tgt_file_name)
  
  s3 = boto3.client('s3')
  s3.download_file('osuapp-winter2023-new-upload', 'test1.txt', '/tmp/test1.txt')

  s3.upload_file('/tmp/test1.txt', 'osuapp-winter2023-new-download', 'test7.txt')

  url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
                'Bucket': tgt_bucket_path,
                'Key': tgt_file_name
            },
            ExpiresIn=24 * 3600
    )

  # TODO implement
  return {
  'statusCode': 200,
  'body': json.dumps('Hello from Lambda!')
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