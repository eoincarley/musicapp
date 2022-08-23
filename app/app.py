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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mypassword@localhost:3306/spotifydb'
db = SQLAlchemy(app)

# Defining the Songs table columns for the MySQL database.

class dbSongs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    songname = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    album = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    duration = db.Column(db.Integer)

    def __repr__(self):
        """
        Return a string representation.

        Returns
        -------
        str
            String version representation
        """
        return f'<(Spectrogram: {self.id}, {self.songname}, '\
               f'{self.artist}, {self.album}, ' \
               f'{self.genre}, {self.duration})>'


def insert_song_data(minio_objects):


    id = datetime.datetime.utcnow().timestamp()*np.random.uniform()
    song = dbSongs(id=id, 
                songname='a', 
                artist='b', 
                album='c',
                genre='d',
                duration='2')

    db.session.add(song)



def get_minio_client(access, secret):

    # Note 172.17.0.2 is the address of the minio container that the Flask container needs.
    # If Flask is not running in its own container then localhost will work.
    client = Minio(
        'localhost:9000', 
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

    # Create database tables and insert minio song data into database.
    db.create_all()
    result = insert_song_data(songs)
    #db.session.commit()
    

    return render_template('index.html', songs=songs)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)