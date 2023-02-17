import boto3
import os
import json
import zipfile

def lambda_handler(event, context):
  s3 = boto3.client('s3')
  bucket_name = 'osuapp-winter2023-jeff-upload-test'
  result = s3.list_objects_v2(Bucket=bucket_name)
  objects = result.get('Contents', [])
  sorted_objects = sorted(objects, key=lambda x: x['LastModified'], reverse=True)
  filearray=[]
  for obj in sorted_objects:
    print(obj['Key'])
    filearray.append(obj['Key'])
  print('filename: ' + filearray[0])
  
  src_bucket_path = 'osuapp-winter2023-jeff-upload-test'
  src_file_name = filearray[0]
  if ((src_file_name.find('/')) != (-1)):
    split = src_file_name.split('/')
    tgt_file_name = 'test2/' + split[1]
  else:
      tgt_file_name = 'test2/' + filearray[0]
      pass
  tgt_bucket_path = 'osuapp-winter2023-jeff-upload-test'
  
  
  print('src' + src_file_name)
  print('tgt' + tgt_file_name)
      
  
  s3 = boto3.resource('s3')
  copy_source = {
  'Bucket': src_bucket_path,
  'Key': src_file_name
  }
 
  s3.meta.client.copy(copy_source, tgt_bucket_path, tgt_file_name)
  
  s3 = boto3.client('s3')
  s3.download_file('osuapp-winter2023-jeff-upload-test', 'test1/test1.txt', '/tmp/test1.txt')

  
  #s3.meta.client.download_file(src_bucket_path, "test2/test4.txt", "test5.txt")
  
  #s3 = boto3.client('s3')
  s3.upload_file('/tmp/test1.txt', 'osuapp-winter2023-jeff-upload-test', 'test7.txt')
  # TODO implement
  return {
  'statusCode': 200,
  'body': json.dumps('Hello from Lambda!')
  }
  

'''
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
'''  

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
          

# code below unused / backup
'''
import json
import boto3

src_bucket_path = 'osuapp-winter2023-jeff-upload-test'
src_file_name = 'test1/test1.txt'
tgt_bucket_path = 'osuapp-winter2023-jeff-upload-test'
tgt_file_name = 'test2/test2.txt'

def lambda_handler(event, context):
 s3 = boto3.resource('s3')
 copy_source = {
 'Bucket': src_bucket_path,
 'Key': src_file_name
 }
 
 s3.meta.client.copy(copy_source, tgt_bucket_path, tgt_file_name)
 # TODO implement
 return {
 'statusCode': 200,
 'body': json.dumps('Hello from Lambda!')
 }
 '''
