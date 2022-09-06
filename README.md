# Musicapp app using Docker.

This exercise aims to build a Minio container that stores a number of music files. A container
running MySQL adds music file info to a database. A container runnung Flask serves up a webpage
to display song information and play the music files. The folder 'app' contains everything to
deploy the app using Docker. Below you will find the instructions on deployment in Kubernetes.

## Minio Container
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

## MySQL Container
Run this using db/runmysql. Command:

```
docker run --name=spotifydb -e MYSQL_ROOT_PASSWORD=mypassword -e MYSQL_DATABASE=spotifydb -p 3306:3306 -d mysql 
```

## Flask container
```
docker build -t musicapp .
docker run -p 5002:5002 --name=musicapp musicapp
```
The webpage should be accessible at localhost:5002. 

# Musicapp using Kubernetes

For the kubernetes deployments see the spotify/kubernetes folder. All yaml files to create pods, deployments and services are placed here. The goal is to first create the Minio and MySQL pods and services. After this you need to build the musicapp docker image and push it to a docker registry (hub.docker.com). Then deploy a kubernetes pod with this custom image.

## Kubernetes - Minio
Firstly create the minio pod using
```
kubectl create -f minio-pod.yaml
```
Then start the minio service that will forward traffic to the pod
```
kubectl create -f minio-service.yaml
```
Once the service is created you must perform port-forwarding from local machine to the service.
```
kubectl port-forward service/minio-service 9000:9000 9001:9001
```
You should now be able to open a browser and visit localost:9001 to see the minio console. You can log in as before, with the root user and root password set in the minio-pod.yaml.

## Kubernetes - MySQL

Start the MySQL pod and service using

```
kubectl create -f mysql-pod.yaml
kubectl create -f mysql-service.yaml
```
Then run portforwarding for the service:
```
kubectl port-forward service/mysql-controller 3306:3306
```
You should be able to connect to the database in VSCode through a MySQL extension using the IP localhost:3306, user as 'root' and password as 'mypassword'. If Flask is not running and there is nothing in the Minio bucket then the DB will be an empty table.

## Kubernetes - Musicapp (Flask)

Now run the musicapp which is built on flask. Note this is a custom image build, so the image needs to be built, sent to a docker registry and then this image is pulled during the musicapp pod deployment. There are a number of commands that need to be run each time the Python, CSS or HTML is updated. I've grouped these under a bash executable:

```
./redo-docker-oush.sh
```

This will kill a current musicapp pod, rebuild the image, push to docker registry, then deploy the kubernetes pod again. After the musicapp pod is deployed, run the musicapp service

```
kubectl create -f mysql-service.yaml
```

Now visit localhost:5002 to see the musicapp homepage. If mp3 files are in the 'songs' bucket on Minio they should show up in the musicapp player.

# Current Issues

* **MySQL service name not recognised by SQLAlchemy** - Currently the Kubernetes service IP for the MySQL pod is hardcoded into app.py. This is not ideal, as the service IPs change on pod redployment. I tried the mysql service name in SQLAlchemy database URI definition in app.py but it does not work. Need to implement the Kubernetes Python API to get the IPs from the service names.

* **Minio service name not streaming songs** - The 'minio-service' name works in getting Flask connected to the minio bucket and song names and urls can be read from the 'songs' bucket. However, the songs cannot be streamed/played using the preseigned url returned by Minio. To get around this I've implemented a cheap hack in app.py, where the url 'minio-service:9000' is replaced with 'localhost:9000'. The app can play music if the url is with localhost.

* **Google chrome page refresh showing odd behavior** - If the page is refreshed in Google Chrome the html rendering changes each time. Have to refresh about five times for the proper style to appear. Doesn't happen in FireFox.