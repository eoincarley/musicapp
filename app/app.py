from flask import Flask, render_template
from minio import Minio
from minio.error import S3Error
from flask_sqlalchemy import SQLAlchemy
import datetime
import pymysql
import os
import datetime
import numpy as np

pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mypassword@172.17.0.3:3306/spotifydb' 
db = SQLAlchemy(app)


class dbSongs(db.Model):

    # Defining the Songs table columns for the MySQL database.

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
  
    db.create_all()

    # Loop through Minio objects and check for duplicates in the database.
    # This loop will become expensive for a large amount of objects.
    # Replace it by SQL query of which song ids already exist in db.
    # Note iteration over the minio object also means you lose access
    # to the data. This is because the generator in the loop is yielding
    # values over a stream that are not stored in memory, so they are lost
    # Another call to the minio client will retrieve the data again.
    
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



def get_minio_client(access, secret):

    # Note 172.17.0.2 is the address of the minio container that the Flask container needs.
    # If Flask is not running in its own container then localhost will work.
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
    insert_song_db(songs)

    songlist = [obj.object_name for obj in minio_client.list_objects(bucket_name)]

    return render_template('index.html', songlist=songlist)


if __name__ == "__main__":

    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)