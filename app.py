oc patch route my-secure-route -n your-namespace \
  --type=merge \
  -p "$(oc get secret my-tls-secret -o json | jq '{spec: {tls: {key: (.data["tls.key"] | @base64d), certificate: (.data["tls.crt"] | @base64d), caCertificate: (.data["ca.crt"] | @base64d)}}}')"
