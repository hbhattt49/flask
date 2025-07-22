# Extract and decode cert components
TLS_CERT=$(oc get secret my-tls-secret -o jsonpath='{.data.tls\.crt}' | base64 -d | awk '{printf "%s\\n", $0}')
TLS_KEY=$(oc get secret my-tls-secret -o jsonpath='{.data.tls\.key}' | base64 -d | awk '{printf "%s\\n", $0}')
TLS_CA=$(oc get secret my-tls-secret -o jsonpath='{.data.ca\.crt}' | base64 -d | awk '{printf "%s\\n", $0}')

# Create a JSON patch file
cat > patch-route.json <<EOF
{
  "spec": {
    "tls": {
      "termination": "edge",
      "certificate": "$TLS_CERT",
      "key": "$TLS_KEY",
      "caCertificate": "$TLS_CA",
      "insecureEdgeTerminationPolicy": "Redirect"
    }
  }
}
EOF

# Apply the patch
oc patch route my-secure-route -n your-namespace --type=merge --patch-file=patch-route.json
