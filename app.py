from flask import Flask, render_template, jsonify, request
import subprocess

app = Flask(__name__)

# Function to execute a shell script
def execute_script(script_path, args=[]):
    try:
        result = subprocess.run(["bash", script_path] + args, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return str(e)

# API to get Pods (User-Limited Namespace)
@app.route('/get_pods')
def get_pods():
    try:
        output = subprocess.run(["bash", "scripts/get_pods.sh"], capture_output=True, text=True)
        pod_data = []

        for line in output.stdout.split("\n"):
            if line.strip():
                parts = line.split()
                pod_data.append({"name": parts[0], "status": parts[1]})  # No namespace info

        return jsonify({"pods": pod_data})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)

