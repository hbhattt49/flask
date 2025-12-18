download_and_verify_sha512() {
  local url="$1"
  local sha_url="$2"
  local out="$3"
  local sha_file="${out}.sha512"

  # Download archive if missing
  if [[ ! -f "$out" ]]; then
    log "Downloading: $url"
    curl -fL --retry 5 --retry-delay 2 -o "$out" "$url"
  else
    log "Already downloaded: $out (will verify)"
  fi

  # Always download checksum fresh (small)
  log "Downloading SHA512: $sha_url"
  curl -fL --retry 5 --retry-delay 2 -o "$sha_file" "$sha_url"

  # Extract hash from either:
  # 1) "<hash>  filename"
  # 2) "SHA512 (filename) = <hash>"
  local expected
  expected="$(grep -Eo '[0-9a-fA-F]{128}' "$sha_file" | head -n1 || true)"

  if [[ -z "$expected" ]]; then
    echo "ERROR: Could not parse SHA512 hash from $sha_file"
    echo "File content:"
    cat "$sha_file"
    exit 1
  fi

  local actual
  actual="$(sha512sum "$out" | awk '{print $1}')"

  if [[ "${expected,,}" != "${actual,,}" ]]; then
    echo "ERROR: SHA512 mismatch for $out"
    echo "Expected: $expected"
    echo "Actual:   $actual"
    exit 1
  fi

  log "SHA512 OK: $out"
}
