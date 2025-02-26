apiVersion: apps/v1
kind: Deployment
metadata:
  name: jupyterlab
spec:
  template:
    spec:
      containers:
      - name: jupyterlab
        image: jupyter/base-notebook
        args:
          - "jupyter"
          - "lab"
          - "--NotebookApp.allow_origin=https://web-ui.apps.openshift-cluster.com"
          - "--NotebookApp.tornado_settings={\"headers\": {\"Content-Security-Policy\": \"frame-ancestors 'self' https://web-ui.apps.openshift-cluster.com;\"}}"
