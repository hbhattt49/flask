#!/bin/bash

# Get all routes in JSON format
ROUTES_JSON=$(oc get routes -o json)
if [ $? -ne 0 ]; then
  echo "Failed to fetch routes" >&2
  exit 1
fi

# Get services and build a map of service name -> port
declare -A SERVICE_PORTS
while read -r line; do
  svc_name=$(echo "$line" | awk '{print $1}')
  port_info=$(echo "$line" | awk '{print $5}')
  port_num=$(echo "$port_info" | cut -d/ -f1)
  SERVICE_PORTS["$svc_name"]="$port_num"
done < <(oc get svc --no-headers)

# Parse route data and format output
echo "["

echo "$ROUTES_JSON" | jq -r '.items[] | [.metadata.name, .spec.host, (.spec.path // ""), .spec.to.name] | @tsv' | \
while IFS=$'\t' read -r name host path svc_name; do
  full_url="$host$path"
  port="${SERVICE_PORTS[$svc_name]:-N/A}"

  echo "  {\"application\": \"$name\", \"url\": \"$full_url\", \"port\": \"$port\"},"
done | sed '$ s/,$//'

echo "]"
