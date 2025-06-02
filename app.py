# Set flags
set $is_valid_request 0;
set $is_referer_empty 0;

# Case 1: Valid Referer
if ($http_referer ~* "^https://yourfrontend\.com/.*") {
    set $is_valid_request 1;
}

# Case 2a: Referer is empty
if ($http_referer = "") {
    set $is_referer_empty 1;
}

# Case 2b: Origin matches and Referer was empty
if ($http_origin = "https://yourfrontend.com") {
    if ($is_referer_empty = 1) {
        set $is_valid_request 1;
    }
}

# Case 3: Host mismatch — force invalid
if ($http_host != "user1.backend.com") {
    set $is_valid_request 0;
}

# Final decision
if ($is_valid_request = 0) {
    return 403;
}
