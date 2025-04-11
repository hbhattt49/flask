#!/bin/bash

# Check if abc.txt exists
if [[ ! -f abc.txt ]]; then
  echo "Error: abc.txt not found."
  exit 1
fi

# Read each line (filename) from abc.txt
while IFS= read -r file; do
  # Skip empty lines
  [[ -z "$file" ]] && continue

  # Check if the file exists
  if [[ -f "$file" ]]; then
    # Define the new filename
    new_file="${file}_new"

    # Copy the original file to the new file
    cp "$file" "$new_file"

    # Delete the original file
    rm "$file"

    # Rename the new file to the original filename
    mv "$new_file" "$file"

    echo "Processed: $file"
  else
    echo "Warning: File '$file' not found."
  fi
done < abc.txt
