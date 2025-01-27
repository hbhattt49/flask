# Route for User 1
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: jupyterlab-user1-route
spec:
  host: example.com
  path: /user1
  to:
    kind: Service
    name: jupyterlab-user1-service
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect

---
# Route for User 2
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: jupyterlab-user2-route
spec:
  host: example.com
  path: /user2
  to:
    kind: Service
    name: jupyterlab-user2-service
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
