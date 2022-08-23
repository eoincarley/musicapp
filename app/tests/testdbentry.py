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
        return f'<(Spectrogram: {self.id}, {self.songname})>'


db.create_all()
song = Songs(id=1, songname='test')
db.session.add(song)
db.session.commit()

import pdb
pdb.set_trace()

