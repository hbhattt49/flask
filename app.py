oc patch route abc-container --type=merge -p '{
  "spec": {
    "tls": {
      "termination": "edge",
      "insecureEdgeTerminationPolicy": "Redirect",
      "certificate": "'"$(oc get secret abc-container-tls -o jsonpath='{.data.tls\.crt}' | base64 -d)"'",
      "key": "'"$(oc get secret abc-container-tls -o jsonpath='{.data.tls\.key}' | base64 -d)"'"
    }
  }
}'
