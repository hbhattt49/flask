worker_processes 1;
events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;

    # WebSocket support fix
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        listen 8080;

        #### 1. JupyterLab at /user1/lab/
        location /user1/lab/ {
            proxy_pass http://localhost:8888/user1/lab/;

            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        #### 2. code-server at /user1/code/ (with path rewrite)
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

        #### 3. Optional WebSocket fallback for code-server (if using /socket.io/)
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
