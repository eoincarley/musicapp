
import os
import datetime
import numpy as np
import pymysql
import datetime

from flask import Flask, flash, render_template, request, redirect
from minio import Minio
from minio.error import S3Error
from flask_sqlalchemy import SQLAlchemy
from forms import MusicSearchForm
from kubernetes import client, config


config.load_incluster_config()
api = client.CoreV1Api()
service = api.read_namespaced_service(name="mysql-service", namespace="default")

pymysql.install_as_MySQLdb() 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ''.join(('mysql://root:mypassword@', 
                                                service.spec.cluster_ip, ':3306/spotifydb')) 
db = SQLAlchemy(app)


class dbSongs(db.Model):
    '''
        Class to define the Songs table columns for the MySQL database.

        args:
            db: A db object from SQLAlchemy.

        Returns:
            A string representation of db columns.

    '''
    id = db.Column(db.String(255), primary_key=True)
    songname = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    album = db.Column(db.String(255))
    minio_bukcet = db.Column(db.String(255))
    filename = db.Column(db.String(255))
    filesize = db.Column(db.String(255))


    def __repr__(self):
        """
        Return a string representation.

        Returns
        -------
        str
            String version representation
        """
        return f'<(Song: {self.id}, {self.songname}, '\
               f'{self.artist}, {self.album}, ' \
               f'{self.genre}, {self.duration})>'


def insert_song_db(minio_objs):
    """
    Function to insert songs from a Minio client object into 
    the dbSongs database table.

    args: 
        minio_objs: Minio Object list returned by a connection to a minio bucket.
                    e.g. songobjects = minio_client.list_objects(bucketname)
    
    Returns: 
        None

    Notes: This function could be improved a lot:
            # Loop through Minio objects and check for duplicates in the database.
            # This loop will become expensive for a large amount of objects.
            # Replace it by SQL query of which song ids already exist in db.
            # Note iteration over the minio object also means you lose access
            # to the data. This is because the generator in the loop is yielding
            # values over a stream that are not stored in memory, so they are lost
            # Another call to the minio client will retrieve the data again.
    """
    db.create_all()
    
    for minio_obj in minio_objs:
        instance = dbSongs.query.filter_by(id=minio_obj.etag).first()
        if not instance: 
            song = dbSongs(id = minio_obj.etag, 
                            songname = ' ', 
                            artist = ' ', 
                            album = ' ',
                            minio_bukcet = minio_obj.bucket_name,
                            filename = minio_obj.object_name,
                            filesize = minio_obj.size)
            db.session.add(song)
        else:
            print('Song %s already exists in database with id %s.' %(minio_obj.object_name, minio_obj.etag), flush=True)
    db.session.commit()

    return None


def get_minio_client(access, secret, minio_endpoint='localhost'):
    """
    Function to return a minio client object.

    args: 
        access (str): Username access
        secret (str): password

    keywords:
        minio_endpoint (str): The host to connect to. Will accept a Kubernetes
                              service name if one exists.
    
    Returns: 
        minio client object.

    Notes: # Note 172.17.0.2 is the address of the minio container that the Flask container needs.
    # If Flask is not running in its own container then localhost will work.
    # Note the container IP was not providing the mp3 objects. Replaced with the docker gateway
    # IP and that seems to have worked. 192.168.0.234
    #config.load_incluster_config()
    #api = client.CoreV1Api()
    #service = api.read_namespaced_service(name="minio-service", namespace="default")
    """
    minio_client = Minio(minio_endpoint, 
        access_key = access,
        secret_key = secret,
        secure = False
    )

    return  minio_client

def get_songinfo(bucket_name, minio_client, minio_service):

    songnames = [obj.object_name
                    for obj in minio_client.list_objects(bucket_name)]

    songurls = [minio_client.presigned_get_object(bucket_name, obj.object_name).split('?')[0].replace(minio_service, 'localhost')
                    for obj in minio_client.list_objects(bucket_name)]

    return list(zip(songnames, songurls))


@app.route('/', methods=['POST', 'GET'])
def home():
    '''
    Flask home route definition.
    '''
    #--------------------------------------------------------#
    #    Define bucket, Minio endpoint. Setup Minio client
    #
    bucket_name = 'songs'
    minio_port = '9000'
    minio_service = 'minio-service'
    minio_endpoint = ':'.join((minio_service, minio_port))
    minio_client = get_minio_client('testkey', 'secretkey', 
                                    minio_endpoint=minio_endpoint)

    #---------------------------------------------------#
    #    Create a bucket if not already created.
    #
    try:
        if (not minio_client.bucket_exists(bucket_name)):
            minio_client.make_bucket(bucket_name)
        else:
            print('Bucket \'%s\' already exists' %(bucket_name))
    except S3Error as exc:
        print("Error occurred during bucket query/creation:", exc)
    
    songs = minio_client.list_objects(bucket_name)

    #---------------------------------------------------#
    #     Insert song info into MySQL database.
    #
    try:
        insert_song_db(songs)
    except:
        print('Error inserting songs into database.')

    
    #---------------------------------------------------#
    #    Return song names and file locations. 
    #    Could/Should render this from the DB.
    #
    songinfo = get_songinfo(bucket_name, minio_client, minio_service)

    #---------------------------------------------------#
    #    If search item request, search songinfo. 
    #    This could also be done from the DB.
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        search_string = search.data['search']
    else:
        search_string = None

    if search_string: songinfo = [songtuple for songtuple in songinfo 
                    if search_string.lower() in songtuple[0].lower()]

    return render_template('index.html', songlist=songinfo, form=search, searchitem=search_string)


if __name__ == "__main__":

    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)