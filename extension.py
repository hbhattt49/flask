from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
from tornado.web import HTTPError
import secrets

used_tokens = set()
current_token = secrets.token_urlsafe(24)
token_file = '/tmp/current_token.txt'

# Save the initial token
with open(token_file, 'w') as f:
    f.write(current_token)

print(f"[Initial Token]: {current_token} (saved to {token_file})")

class OneTimeAuthHandler(JupyterHandler):
    def prepare(self):
        global current_token
        token = self.get_argument("token", None)

        if not token:
            raise HTTPError(401, "Token missing")

        if token in used_tokens:
            raise HTTPError(403, "Token already used")

        if token != current_token:
            raise HTTPError(403, "Invalid token")

        # Mark token as used
        used_tokens.add(token)

        # Set secure cookie
        self.set_secure_cookie("authenticated", "true", httponly=True)
        print("[Auth Passed] Cookie set. Token now invalid.")

        # Generate new token (for next session)
        current_token = secrets.token_urlsafe(24)
        with open(token_file, 'w') as f:
            f.write(current_token)
        print(f"[New Token Generated]: {current_token}")

    def get(self):
        self.finish("Authentication successful. You may now access /lab")

class ProtectedHandler(JupyterHandler):
    def prepare(self):
        auth_cookie = self.get_secure_cookie("authenticated")
        if auth_cookie != b"true":
            raise HTTPError(403, "Access denied. Authenticate at /one-time-auth?token=...")

    def get(self):
        self.finish("Access granted to protected route")

def load_jupyter_server_extension(server_app):
    base_url = server_app.web_app.settings["base_url"]

    # Protect /lab, /tree, etc.
    protected_routes = ["/lab", "/tree", "/notebooks"]
    for route in protected_routes:
        route_pattern = url_path_join(base_url, route)
        server_app.web_app.add_handlers(".*$", [(route_pattern, ProtectedHandler)])

    # Auth route
    auth_route = url_path_join(base_url, "/one-time-auth")
    server_app.web_app.add_handlers(".*$", [(auth_route, OneTimeAuthHandler)])

    server_app.log.info("🔒 One-time token extension with cookie-based /lab protection loaded.")
