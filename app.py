from notebook.notebookapp import random_token

# Set a fresh token at startup
token = random_token()
print(f"Generated one-time token: {token}")

c.ServerApp.token = token
c.ServerApp.open_browser = False
c.ServerApp.allow_origin = '*'
c.ServerApp.server_extensions.append('one_time_token_extension')

# You can optionally store the token somewhere
with open('/tmp/current_token.txt', 'w') as f:
    f.write(token)
