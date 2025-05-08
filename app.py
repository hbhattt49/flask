FROM registry.access.redhat.com/ubi9/ubi

USER root

ENV CODE_SERVER_VERSION=4.89.1
ENV PASSWORD=yourpassword

RUN dnf install -y tar shadow-utils && \
    dnf clean all

RUN useradd -m coder

# Use curl-minimal safely (with user-agent)
WORKDIR /tmp
RUN curl -L -A "Mozilla/5.0" \
    -o code-server.tar.gz \
    https://github.com/coder/code-server/releases/download/v${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION}-linux-amd64.tar.gz && \
    tar -xzf code-server.tar.gz && \
    mv code-server-${CODE_SERVER_VERSION}-linux-amd64/code-server /usr/local/bin/code-server && \
    rm -rf code-server*

# Create project folder and fix permissions
RUN mkdir -p /home/coder/project && \
    chown -R coder:coder /home/coder

USER coder
WORKDIR /home/coder/project

EXPOSE 8080

CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "password"]
