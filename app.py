worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;

    # WebSocket upgrade mapping
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    # ✅ Secure access map based on Referer, Origin, and Host
    map "$http_referer|$http_origin|$http_host" $is_valid_request {
        default                                             0;
        "~^https://yourfrontend\.com/.*|||user1.backend.com"     1;
        "|https://yourfrontend.com|user1.backend.com"            1;
    }

    server {
        listen 8080;

        # ✅ Block if request doesn't meet access criteria
        if ($is_valid_request = 0) {
            return 403;
        }

        # ✅ CSP for iframe embedding protection
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

            sub_filter_once off;
            sub_filter 'href="/' 'href="/user1/code/';
            sub_filter 'src="/' 'src="/user1/code/';
            sub_filter 'action="/' 'action="/user1/code/';
        }

        # ---------------- code-server WebSocket ----------------
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
