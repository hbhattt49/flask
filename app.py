import secrets
import sys

# Include custom extension path
sys.path.append("/home/YOUR_USERNAME/.jupyter/custom_extensions")

initial_token = secrets.token_urlsafe(24)
print(f"[Initial token]: {initial_token}")

c.ServerApp.token = initial_token
c.ServerApp.open_browser = False
c.ServerApp.allow_origin = '*'

# Register extension
c.ServerApp.jpserver_extensions = {
    "one_time_token_extension": True
}

# Save initial token to temp file
with open('/tmp/current_token.txt', 'w') as f:
    f.write(initial_token)
