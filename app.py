# Use UBI (Red Hat Universal Base Image)
FROM registry.access.redhat.com/ubi9/ubi

# Set environment variables (can be overridden in Deployment)
ENV POSTGRES_USER=myuser \
    POSTGRES_PASSWORD=mypassword \
    POSTGRES_DB=mydb \
    PGDATA=/var/lib/pgsql/data

# Install PostgreSQL
RUN dnf install -y postgresql-server postgresql && \
    dnf clean all && \
    mkdir -p /var/lib/pgsql/data && \
    chown -R 26:26 /var/lib/pgsql && \
    chmod -R 700 /var/lib/pgsql

# Switch to postgres user (recommended for security)
USER 26

# Initialize DB in entrypoint if empty
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose PostgreSQL port
EXPOSE 5432

# Start with custom entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
