worker_processes 1;

events {
    worker_connections 1024;
}

http {
    # Required to prevent "could not build map hash" error
    map_hash_bucket_size 128;

    # 🔐 Allow access only if:
    # 1. Referer starts with frontend domain AND host matches
    # 2. OR Referer is empty, Origin is frontend domain, AND host matches
    map "$http_referer|$http_origin|$http_host" $is_valid_request {
        default                                                   0;
        "~^https://yourfrontend\.com/.*|||user1.backend.com"       1;
        "|https://yourfrontend.com|user1.backend.com"              1;
    }

    # For WebSocket connection upgrades
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        listen 8080;

        # Log access attempts (optional for debugging)
        log_format debug_format '$remote_addr - Referer:"$http_referer" - Origin:"$http_origin" - Host:"$http_host"';
        access_log /var/log/nginx/iframe_debug.log debug_format;

        # ⛔ Block all invalid requests (not from iframe with proper headers)
        if ($is_valid_request = 0) {
            return 403;
        }

        # ✅ Set CSP so only yourfrontend.com can iframe this
        add_header Content-Security-Policy "frame-ancestors https://yourfrontend.com" always;

        # ---------------- JupyterLab ----------------
        location /user1/lab/ {
            proxy_pass http://localhost:8888/user1/lab/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # ---------------- code-server ----------------
        location /user1/code/ {
            rewrite ^/user1/code/(.*)$ /$1 break;
            proxy_pass http://localhost:8081/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # Rewrite internal paths (code-server doesn't support base paths)
            sub_filter_once off;
            sub_filter 'href="/' 'href="/user1/code/';
            sub_filter 'src="/' 'src="/user1/code/';
            sub_filter 'action="/' 'action="/user1/code/';
        }

        # ---------------- WebSocket (code-server) ----------------
        location /user1/code/socket.io/ {
            rewrite ^/user1/code/socket.io/(.*)$ /socket.io/$1 break;
            proxy_pass http://localhost:8081/socket.io/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
        }
    }
}
