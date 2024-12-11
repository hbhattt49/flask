from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy LDAP authentication function
def ldap_authenticate(username, password):
    # Replace this with actual LDAP authentication logic
    return username == "admin" and password == "password"

@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if ldap_authenticate(username, password):
        session['username'] = username
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error="Invalid credentials")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/deploy', methods=['POST'])
def deploy():
    username = session.get('username')
    if not username:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        # Call deploy.sh script with username
        result = subprocess.run(['./deploy.sh', username], capture_output=True, text=True, check=True)
        return jsonify({"message": "Deployment successful", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Deployment failed", "details": e.stderr}), 500

@app.route('/status', methods=['GET'])
def status():
    if 'username' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        # Call status.sh script
        result = subprocess.run(['./status.sh'], capture_output=True, text=True, check=True)
        return jsonify({"message": "Status retrieved successfully", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to retrieve status", "details": e.stderr}), 500

@app.route('/launch', methods=['GET'])
def launch():
    if 'username' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        # Call retrieve_url.sh script
        result = subprocess.run(['./retrieve_url.sh'], capture_output=True, text=True, check=True)
        url = result.stdout.strip()
        return render_template('launch.html', url=url)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to retrieve URL", "details": e.stderr}), 500

if __name__ == '__main__':
    app.run(debug=True)
