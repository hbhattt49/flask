from jupyter_server.base.handlers import JupyterHandler
from notebook.utils import url_path_join
from tornado.web import HTTPError
import secrets

# Token management
used_tokens = set()
new_token = secrets.token_urlsafe(24)

def generate_token():
    return secrets.token_urlsafe(24)

class OneTimeAuthHandler(JupyterHandler):
    def prepare(self):
        token = self.get_argument('token', None)

        if not token:
            raise HTTPError(401, "Token missing")

        if token in used_tokens:
            raise HTTPError(403, "This token has already been used.")

        # Allow access and expire token
        used_tokens.add(token)
        global new_token
        new_token = generate_token()

        # Save new token for next time
        with open('/tmp/current_token.txt', 'w') as f:
            f.write(new_token)

        print(f"[Token used]: {token}")
        print(f"[New token generated]: {new_token}")

    def get(self):
        self.finish("Access granted. This token is now expired.")

def load_jupyter_server_extension(server_app):
    route_pattern = url_path_join(server_app.web_app.settings["base_url"], "/one-time-auth")
    server_app.web_app.add_handlers(".*$", [(route_pattern, OneTimeAuthHandler)])
    server_app.log.info("One-time token extension loaded.")
