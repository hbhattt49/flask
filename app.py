apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: jupyterlab-deployment
  labels:
    app: jupyterlab
spec:
  replicas: 1
  selector:
    app: jupyterlab
  template:
    metadata:
      labels:
        app: jupyterlab
    spec:
      containers:
        - name: jupyterlab
          image: jupyter/base-notebook:latest
          command: ["/bin/bash", "-c"]
          args:
            - |
              echo "Copying .condarc file..." && \
              cp /data/condarc/.condarc /home/jovyan/.condarc && \
              echo "Starting JupyterLab with Content-Security-Policy headers..." && \
              jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' \
              --NotebookApp.tornado_settings='{"headers": {"Content-Security-Policy": "frame-ancestors * self"}}'
          ports:
            - containerPort: 8888
          volumeMounts:
            - name: condarc-volume
              mountPath: /data/condarc
            - name: jupyter-home
              mountPath: /home/jovyan
      volumes:
        - name: condarc-volume
          hostPath:
            path: /path/to/condarc  # Replace with the location of your .condarc file
        - name: jupyter-home
          emptyDir: {}

  triggers:
    - type: ConfigChange
  strategy:
    type: Rolling
