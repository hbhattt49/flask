from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy LDAP authentication function
def ldap_authenticate(username, password, lob):
    # Replace this with actual LDAP authentication logic
    valid_users = {
        "LOB1": {"admin": "password1"},
        "LOB2": {"user": "password2"},
        "LOB3": {"manager": "password3"},
    }
    return valid_users.get(lob, {}).get(username) == password

@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    lob = request.form.get('lob')

    if not username or not password or not lob:
        return render_template('login.html', error="All fields are required")

    if ldap_authenticate(username, password, lob):
        session['username'] = username
        session['lob'] = lob
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error="Invalid credentials or LOB")

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('lob', None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'], lob=session['lob'])

@app.route('/status_check', methods=['GET'])
def status_check():
    try:
        # Call status.sh script
        result = subprocess.run(['./status.sh'], capture_output=True, text=True, check=True)
        status = result.stdout.strip().lower() == 'true'
        return jsonify({"status": status})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to retrieve status", "details": e.stderr}), 500

@app.route('/one_time_setup', methods=['POST'])
def one_time_setup():
    try:
        # Call one_time_setup.sh script
        result = subprocess.run(['./one_time_setup.sh'], capture_output=True, text=True, check=True)
        return jsonify({"message": "Setup complete"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Setup failed", "details": e.stderr}), 500

if __name__ == '__main__':
    app.run(debug=True)
