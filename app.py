
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: jupyterlab-route
spec:
  host: example.com  # Replace with your desired domain
  path: /
  rules:
    - path: /user1
      to:
        kind: Service
        name: jupyterlab-user1-service
        weight: 100
    - path: /user2
      to:
        kind: Service
        name: jupyterlab-user2-service
        weight: 100
  tls:
    termination: edge  # Use 'passthrough' if you want SSL termination at the backend
    insecureEdgeTerminationPolicy: Redirect
