from flask import Flask, render_template
from minio import Minio
from minio.error import S3Error
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mypassword@localhost:3306/spotifydb'
db = SQLAlchemy(app)

# Defining the Songs table columns for the MySQL database.

class Songs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    songname = db.Column(db.String(255))

    def __repr__(self):
        """
        Return a string representation.

        Returns
        -------
        str
            String version representation
        """
        return f'<(Songs: {self.id}, {self.songname})>'


db.create_all()
song = Songs(id=1, songname='test')
db.session.add(song)
song = Songs(id=2, songname='test')
db.session.add(song)
song = Songs(id=3, songname='test')
db.session.add(song)
db.session.commit()
#///

songids = [1,2,3,4]

pk = Songs.__mapper__.primary_key[0]
items = Songs.query.filter(pk.in_(songids)).all()
exist_ids = [item.id for item in items]
result = list(set(exist_ids)^set(songids)) # list of song ids not in db.

#db.session.query(Songs).filter(Songs.id.not_in([1, 2, 3, 4]))

