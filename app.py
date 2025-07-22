# Extract and decode values, then escape them as JSON strings
TLS_CERT=$(oc get secret my-tls-secret -o jsonpath='{.data.tls\.crt}' | base64 -d | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
TLS_KEY=$(oc get secret my-tls-secret -o jsonpath='{.data.tls\.key}' | base64 -d | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
TLS_CA=$(oc get secret my-tls-secret -o jsonpath='{.data.ca\.crt}' | base64 -d | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')

# Create the patch file
cat > patch-route.json <<EOF
{
  "spec": {
    "tls": {
      "termination": "edge",
      "certificate": $TLS_CERT,
      "key": $TLS_KEY,
      "caCertificate": $TLS_CA,
      "insecureEdgeTerminationPolicy": "Redirect"
    }
  }
}
EOF

# Apply the patch
oc patch route my-secure-route -n your-namespace --type=merge --patch-file=patch-route.json
