from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join
from tornado import web
from notebook.notebookapp import list_running_servers
import os

used_tokens = set()

class OneTimeTokenHandler(IPythonHandler):
    def prepare(self):
        token = self.get_argument('token', default=None)

        if not token:
            raise web.HTTPError(401, "Token required")

        if token in used_tokens:
            raise web.HTTPError(403, "Token has already been used")

        # Mark token as used
        used_tokens.add(token)

        # (Optional) Regenerate token or log here
        print(f"Token '{token}' has been used and is now invalid.")

    def get(self):
        self.finish("Access granted with one-time token.")

def load_jupyter_server_extension(nbapp):
    web_app = nbapp.web_app
    host_pattern = ".*$"
    route_pattern = url_path_join(web_app.settings["base_url"], "/one-time-auth")
    web_app.add_handlers(host_pattern, [(route_pattern, OneTimeTokenHandler)])
    nbapp.log.info("One-time token extension loaded.")
