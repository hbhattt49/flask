apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: myapp-route
spec:
  host: myapp.example.com
  to:
    kind: Service
    name: service-a
  port:
    targetPort: 8080
  path: /api/v1
