#!/bin/bash

# Get routes (host + name + path)
ROUTES=$(oc get routes --no-headers -o custom-columns="NAME:.metadata.name,HOST:.spec.host,PATH:.spec.path,TO:.spec.to.name")
if [ $? -ne 0 ]; then
  echo "Failed to fetch routes" >&2
  exit 1
fi

# Get services and build a map of service name → port
declare -A SERVICE_PORTS
while read -r line; do
  svc_name=$(echo "$line" | awk '{print $1}')
  port_info=$(echo "$line" | awk '{print $5}')
  port_num=$(echo "$port_info" | cut -d/ -f1)
  SERVICE_PORTS["$svc_name"]="$port_num"
done < <(oc get svc --no-headers)

# Output routes with port as a Python list
echo "["

first=true
echo "$ROUTES" | while read -r name host path to; do
  [[ -z "$name" || -z "$host" || -z "$to" ]] && continue

  full_url="$host$path"
  port="${SERVICE_PORTS[$to]:-N/A}"

  if [ "$first" = true ]; then
    first=false
  else
    echo ","
  fi

  echo -n "  {\"application\": \"$name\", \"url\": \"$full_url\", \"port\": \"$port\"}"
done

echo "]"
