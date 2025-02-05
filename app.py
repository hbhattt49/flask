from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__)

# Admin Dashboard
@app.route('/admin')
def admin_index():
    return render_template('admin_index.html')

# Resources Page
@app.route('/resources')
def resources():
    return render_template('resources.html')

# Compute Metrics Page
@app.route('/metrics')
def metrics():
    return render_template('metrics.html')

# Execute OC Commands via Bash Scripts
def execute_script(script_path):
    try:
        result = subprocess.run(["bash", script_path], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return str(e)

@app.route('/get_pods')
def get_pods():
    return execute_script("scripts/get_pods.sh")

@app.route('/get_routes')
def get_routes():
    return execute_script("scripts/get_routes.sh")

@app.route('/get_services')
def get_services():
    return execute_script("scripts/get_services.sh")

@app.route('/get_pvc')
def get_pvc():
    return execute_script("scripts/get_pvc.sh")

@app.route('/get_metrics')
def get_metrics():
    return execute_script("scripts/get_metrics.sh")

if __name__ == '__main__':
    app.run(debug=True)
