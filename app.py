import sys
import os

# Add path to extension
sys.path.append(os.path.expanduser("~/.jupyter/one_time_token_extension"))

c.ServerApp.token = ''  # Disable default token
c.ServerApp.open_browser = False
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True

c.ServerApp.jpserver_extensions = {
    "one_time_token_extension": True
}
