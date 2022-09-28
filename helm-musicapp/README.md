# Musicapp deployment via Helm

The kubernetes yaml files are copied to the templates folders. For the moment, only a few variables are taken from values.yaml, namely the app name and the ports to access each of the pods.

To deploy the app usin helm:

```
helm install musicapp ./helm-musicapp/
```

Or for a dry run to see the entire set of yaml files, without actually installing anything.

```
helm install --debug --dry-run musicapp ./helm-musicapp/
```


If you then run `kubectl get all`, you should be able to see the deployments, services and pods running for the musicapp.

## Port forwarding

To view the Musicapp or Minio in a console, don't forget to run the following port forward commands.

For MySQL:
```
kubectl port-forward service/mysql-controller 3306:3306
```
For Minio:
```
kubectl port-forward service/minio-service 9000:9000 9001:9001
```

## Note on the musicapp image

If running this helm chart for the first time, you need to have already built the musicapp image and have it accessible on your local machine. To do this you can cd to the spotify/kubernetes folder and run 

```
docker build -t musicapp:latest .
```
