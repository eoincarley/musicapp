# Spotify app using Docker/Kubernetes.

This exercise aims to build a Minio container that stores a number of music files. A container
running MySQL adds music file info to a database. A container runnung Flask serves up a webpage
to display song information and play the music files. For the moment these containers are started
separately, but will eventually be orchestrated using Kubernetes.

# Minio Container
Run the Minio container using the command in app/minio/minio-run. 

```
docker run -t -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minioTest \
  -e "MINIO_ROOT_USER=testkey" \
  -e "MINIO_ROOT_PASSWORD=secretkey" \
  -v /home/eoincarley/spotify/backend/static:/data \
  quay.io/minio/minio server /data --console-address ":9001"
```

The Minio console should be available at localhost:9001. The login will be the above testket and secretkey. Create a bucket called 'songs' and upload mp3 files to this bucket.

# MySQL Container
Run this using db/runmysql. Command:

```
docker run --name=spotifydb -e MYSQL_ROOT_PASSWORD=mypassword -e MYSQL_DATABASE=spotifydb -p 3306:3306 -d mysql 
```

# Flask container
```
docker build -t musicapp .
docker run -p 5002:5002 --name=musicapp musicapp
```
The webpage should be accessible at localhost:5002. 

# Orchestration
The above could/should be orchestrated using Docker compose or Kubernetes.
