kubectl delete deployment musicapp-deploy
docker build -t musicapp:latest .
kubectl create -f musicapp-deployment.yaml