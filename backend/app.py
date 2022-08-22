from flask import Flask, render_template
from minio import Minio
from minio.error import S3Error
import os

app = Flask(__name__)

def get_minio_client(access, secret):

    client = Minio(
        '172.17.0.2:9000',
        access_key = access,
        secret_key = secret,
        secure = False
    )

    return client


@app.route('/', methods=['POST', 'GET'])
def home():

    minio_client = get_minio_client('testkey', 'secretkey')
    bucket_name = 'songs'
    songs = minio_client.list_objects(bucket_name)

    return render_template('index.html', songs=songs)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)