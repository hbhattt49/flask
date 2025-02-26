apiVersion: apps/v1
kind: Deployment
metadata:
  name: jupyterlab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jupyterlab
  template:
    metadata:
      labels:
        app: jupyterlab
    spec:
      containers:
      - name: jupyterlab
        image: jupyter/base-notebook  # Change this to your JupyterLab image
        ports:
          - containerPort: 8888
        env:
          - name: JUPYTER_ALLOW_ORIGIN
            value: "https://web-ui.apps.openshift-cluster.com"
          - name: JUPYTER_TORNADO_SETTINGS
            value: '{"headers": {"Content-Security-Policy": "frame-ancestors '\''self'\'' https://web-ui.apps.openshift-cluster.com;"}}'
        args:
          - "jupyter"
          - "lab"
          - "--NotebookApp.allow_origin=$(JUPYTER_ALLOW_ORIGIN)"
          - "--NotebookApp.tornado_settings=$(JUPYTER_TORNADO_SETTINGS)"
