kubectl delete pod musicapp
docker build -t musicapp:latest .
kubectl create -f musicapp-pod.yaml