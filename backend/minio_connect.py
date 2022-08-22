from minio import Minio
from minio.error import S3Error
import os

def get_minio_client(access, secret):

    client = Minio(
        'localhost:9000',
        access_key = access,
        secret_key = secret,
        secure = False
    )

    return client


"""
    Setup client. Note I had to create a new Service Account with the following
    credentials in the Minio Console.
"""
minio_client = get_minio_client('EoinCarley', 'EXAMPLEKEY')
bucket_name = 'songs'

# Create a bucket
try:
    if (not minio_client.bucket_exists(bucket_name)):
        minio_client.make_bucket(bucket_name)
    else:
        print('Bucket \'%s\' already exists' %(bucket_name))
except S3Error as exc:
    print("error occurred.", exc)


# Upload a file to the desired bucket via the minio client object
file = './static/pianosample.mp3'
try:
    with open(file, 'rb') as testfile:
        statdata = os.stat(file)
        minio_client.put_object(
            bucket_name,
            file,
            testfile,
            statdata.st_size
        )
    testfile.close()
except S3Error as exc:
    print("error occurred.", exc)


# List bucket contents
objects = minio_client.list_objects(bucket_name)

for obj in objects:
    print(obj.bucket_name, obj.object_name, obj.last_modified, \
            obj.etag, obj.size, obj.content_type)
    


