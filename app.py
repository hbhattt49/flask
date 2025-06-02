# Default: block access
set $is_valid_request 0;

# Allow if Referer starts with frontend domain
if ($http_referer ~* "^https://yourfrontend\.com/.*") {
    set $is_valid_request 1;
}

# Allow if Referer is empty, but Origin is trusted
if ($http_referer = "") {
    if ($http_origin = "https://yourfrontend.com") {
        set $is_valid_request 1;
    }
}

# ✅ NEW: Ensure Host is expected
if ($http_host != "user1.backend.com") {
    set $is_valid_request 0;
}

# Final check — block if still invalid
if ($is_valid_request = 0) {
    return 403;
}
