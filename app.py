TLS_CERT=$(oc get secret my-tls-secret -o jsonpath='{.data.tls\.crt}' | base64 -d)
TLS_KEY=$(oc get secret my-tls-secret -o jsonpath='{.data.tls\.key}' | base64 -d)
TLS_CA=$(oc get secret my-tls-secret -o jsonpath='{.data.ca\.crt}' | base64 -d)

oc patch route my-secure-route -n your-namespace --type=merge -p \
  "{
    \"spec\": {
      \"tls\": {
        \"termination\": \"edge\",
        \"key\": \"$TLS_KEY\",
        \"certificate\": \"$TLS_CERT\",
        \"caCertificate\": \"$TLS_CA\",
        \"insecureEdgeTerminationPolicy\": \"Redirect\"
      }
    }
  }"
