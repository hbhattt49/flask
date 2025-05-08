FROM registry.access.redhat.com/ubi9/ubi

USER root

ENV CODE_SERVER_VERSION=4.89.1
ENV PASSWORD=yourpassword

# Install tar and shadow-utils
RUN dnf install -y tar shadow-utils && \
    dnf clean all

# Add non-root user
RUN useradd -m coder

WORKDIR /tmp

# 👇 Copy full downloaded tar.gz into image
COPY code-server-${CODE_SERVER_VERSION}-linux-amd64.tar.gz .

# Extract and move entire code-server dir
RUN tar -xzf code-server-${CODE_SERVER_VERSION}-linux-amd64.tar.gz && \
    mv code-server-${CODE_SERVER_VERSION}-linux-amd64 /usr/local/lib/code-server && \
    ln -s /usr/local/lib/code-server/bin/code-server /usr/local/bin/code-server && \
    rm -f code-server-${CODE_SERVER_VERSION}-linux-amd64.tar.gz

# Setup workspace
RUN mkdir -p /home/coder/project && \
    chown -R coder:coder /home/coder

USER coder
WORKDIR /home/coder/project

EXPOSE 8080

CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "password"]
