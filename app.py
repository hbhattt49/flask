export JUPYTER_ALLOW_ORIGIN="https://web-ui.apps.openshift-cluster.com"
export JUPYTER_TORNADO_SETTINGS='{"headers": {"Content-Security-Policy": "frame-ancestors '\''self'\'' https://web-ui.apps.openshift-cluster.com;"}}'

jupyter lab \
  --NotebookApp.allow_origin="$JUPYTER_ALLOW_ORIGIN" \
  --NotebookApp.tornado_settings="$JUPYTER_TORNADO_SETTINGS"
