#!/bin/bash

# Get all pods ending with "_deploy" and in "Completed" state
pods_to_delete=$(oc get pods --no-headers | awk '$1 ~ /_deploy$/ && $3 == "Completed" {print $1}')

# Check if there are any pods to delete
if [[ -z "$pods_to_delete" ]]; then
    echo "No completed '_deploy' pods found."
    exit 0
fi

# Delete each pod
echo "Deleting completed '_deploy' pods..."
for pod in $pods_to_delete; do
    echo "Deleting pod: $pod"
    oc delete pod $pod
done

echo "All completed '_deploy' pods deleted successfully!"
