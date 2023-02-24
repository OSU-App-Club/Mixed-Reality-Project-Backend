import boto3
import logging
from botocore.exceptions import ClientError
import pygltflib
import numpy as np
from stl import mesh
from math import sqrt

STL_BUCKET_NAME = 'osuapp-winter2023-aws-backend'
GLTF_BUCKET_NAME = 'osuapp-winter2023-gltf'
CSV_BUCKET_NAME = 'metadata-cvs-out' 

s3 = boto3.client('s3')

def convert_stl_to_glb(file: str):
    stl_mesh = mesh.Mesh.from_file(file)

    stl_points = []
    for i in range(0, len(stl_mesh.points)):  # Convert points into correct numpy array
        stl_points.append(
            [stl_mesh.points[i][0], stl_mesh.points[i][1], stl_mesh.points[i][2]])
        stl_points.append(
            [stl_mesh.points[i][3], stl_mesh.points[i][4], stl_mesh.points[i][5]])
        stl_points.append(
            [stl_mesh.points[i][6], stl_mesh.points[i][7], stl_mesh.points[i][8]])

    points = np.array(
        stl_points,
        dtype="float32",
    )

    stl_normals = []
    for i in range(0, len(stl_mesh.normals)):  # Convert points into correct numpy array
        normal_vector = [stl_mesh.normals[i][0],
                         stl_mesh.normals[i][1], stl_mesh.normals[i][2]]
        normal_vector = normalize(normal_vector)
        stl_normals.append(normal_vector)
        stl_normals.append(normal_vector)
        stl_normals.append(normal_vector)

    normals = np.array(
        stl_normals,
        dtype="float32"
    )

    points_binary_blob = points.tobytes()
    normals_binary_blob = normals.tobytes()

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=0, NORMAL=1), indices=None
                    )
                ]
            )
        ],
        accessors=[
            pygltflib.Accessor(
                bufferView=0,
                componentType=pygltflib.FLOAT,
                count=len(points),
                type=pygltflib.VEC3,
                max=points.max(axis=0).tolist(),
                min=points.min(axis=0).tolist(),
            ),
            pygltflib.Accessor(
                bufferView=1,
                componentType=pygltflib.FLOAT,
                count=len(normals),
                type=pygltflib.VEC3,
                max=None,
                min=None,
            ),
        ],
        bufferViews=[
            pygltflib.B
            ufferView(
                buffer=0,
                byteOffset=0,
                byteLength=len(points_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(points_binary_blob),
                byteLength=len(normals_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),
        ],
        buffers=[
            pygltflib.Buffer(
                byteLength=len(points_binary_blob) + len(normals_binary_blob)
            )
        ],
    )
    gltf.set_binary_blob(points_binary_blob + normals_binary_blob)
    glb_filename = f'{file}.glb'
    gltf.save(glb_filename)

    return glb_filename

def _test_():
    # Grab the key from the event that was triggered (filename that was placed in the .stl s3 bucket == key?)
    key = event['Records'][0]['s3']['object']['key']

    # Download the .stl from the stl s3 bucket
    stl_resp = s3.get_object(bucket=STL_BUCKET_NAME, key=key)
    lcl_stl_file = stl_resp['Body'].read().decode('utf-8')

    # Convert .stl to .gltf
    lcl_gltf_file = convert_stl_to_glb(lcl_stl_file)

    # Upload the local .gltf convert file to the gltf s3 bucket
    # TODO await for the uplaod so we can pull from the s3 bucket
    s3.upload_file(lcl_gltf_file, bucket=GLTF_BUCKET_NAME, key=lcl_gltf_file)

    # Generate a presigned url for the gltf file in the s3 bucket
    gtlf_presigned_url = create_presigned_url(lcl_gltf_file)

    # Download the current .csv file from the s3 bucket
    csv_resp = s3.get_object(bucket=CSV_BUCKET_NAME, key='metadata.csv')
    lcl_csv_file = stl_resp['Body'].read().decode('utf-8')
    
    # Append the new presigned url to it
    with open(lcl_csv_file, 'a+') as metadata_file:
        metadata_file.write(gtlf_presigned_url)

    # Reupload the .csv with the added presigned url
    s3.upload_file(lcl_csv_file, bucket=CSV_BUCKET_NAME, key=lcl_csv_file)


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
    # update BUCKET_IN_NAME
    response = s3.get_object(Bucket=BUCKET_IN_NAME, Key='metadata.csv')
    file_content = response['Body'].read().decode('utf-8')
        
    localFileName = "/tmp/file.stl"

    with open(localFileName, 'w') as f:
        f.write(file_content)
    upload_to_s3(localFileName, tgt_file_name)

    # TODO: convert stl file to gltf
    

    # file name with extension
    localFileName = os.path.basename('/root/file.ext')
    # file name without extension
    print(os.path.splitext(file_name)[0])

    create_presigned_url(tgt_file_name)

    # TODO: download metadata.csv and save to lambda temp folder
    # update BUCKET_IN_NAME
    response = s3.get_object(Bucket=BUCKET_IN_NAME, Key='metadata.csv')
    file_content = response['Body'].read().decode('utf-8')
    new_file_content = 'new_file_name,new_metadata\n'

    with open('/tmp/metadata.csv', 'w') as f:
        # append metadata.csv with new file name and metadata
        f.write(new_file_content)
    

    # TODO: Create a bucket to store the csv.
    #       DO NOT put it back into the same bucket we downloaded the .stl from
    upload_to_s3('/tmp/metadata.csv', 'metadata.csv', bucket=CSV_BUCKET_NAME)

# upload local file to s3 bucket
# local_file - name of local file
# s3_file - name that file will be uploaded with to s3 bucket
def upload_to_s3(local_file, s3_file, bucket):
    try:
        s3.upload_file(local_file, bucket, s3_file)

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
                                                    Params={'Bucket': GLTF_BUCKET_NAME,
                                                            'Key': key_object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response