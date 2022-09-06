kubectl delete pod musicapp
docker build -t musicapp .
docker tag musicapp:latest eoincarley/musicapp
docker push eoincarley/musicapp
kubectl create -f musicapp-pod.yaml