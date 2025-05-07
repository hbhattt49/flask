from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
from tornado.web import HTTPError
import secrets
import os

# Globals for token control
used_tokens = set()
current_token = secrets.token_urlsafe(24)
token_file = '/tmp/current_token.txt'

# Save initial token
with open(token_file, 'w') as f:
    f.write(current_token)

print(f"[Initial Token]: {current_token} (saved to {token_file})")

class OneTimeAuthHandler(JupyterHandler):
    def prepare(self):
        global current_token

        token = self.get_argument("token", None)

        if not token:
            raise HTTPError(401, "Token missing in URL")

        if token in used_tokens:
            raise HTTPError(403, "Token already used")

        if token != current_token:
            raise HTTPError(403, "Invalid token")

        # Mark as used
        used_tokens.add(token)
        self.log.info(f"Token {token} used and invalidated")

        # Generate new token
        current_token = secrets.token_urlsafe(24)
        with open(token_file, 'w') as f:
            f.write(current_token)

        print(f"[New Token Generated]: {current_token} (saved to {token_file})")

    def get(self):
        self.finish("Access granted. Your token is now expired.")

def load_jupyter_server_extension(server_app):
    base_url = server_app.web_app.settings["base_url"]
    protected_routes = ["/lab", "/tree", "/notebooks", "/one-time-auth"]

    for route in protected_routes:
        route_pattern = url_path_join(base_url, route)
        server_app.web_app.add_handlers(".*$", [(route_pattern, OneTimeAuthHandler)])

    server_app.log.info("One-time token extension loaded.")
