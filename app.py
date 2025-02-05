#!/bin/bash
PVC_NAME=$1
NEW_SIZE=$2

if [ -z "$PVC_NAME" ] || [ -z "$NEW_SIZE" ]; then
    echo "Error: PVC name and new size required"
    exit 1
fi

oc patch pvc "$PVC_NAME" --type='json' -p '[{"op": "replace", "path": "/spec/resources/requests/storage", "value":"'"$NEW_SIZE"'"}]'
