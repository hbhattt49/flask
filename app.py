from flask import Flask, render_template, jsonify, request
import subprocess

app = Flask(__name__)

def execute_script(script_path, args=[]):
    try:
        result = subprocess.run(["bash", script_path] + args, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return str(e)

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/get_pods')
def get_pods():
    try:
        output = subprocess.run(["bash", "scripts/get_pods.sh"], capture_output=True, text=True)
        pod_data = [line.split() for line in output.stdout.split("\n") if line.strip()]
        return jsonify({"pods": [{"name": pod[0], "status": pod[1]} for pod in pod_data]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/delete_pods', methods=['POST'])
def delete_pods():
    data = request.get_json()
    pods = data.get("items", [])

    if not pods:
        return jsonify({"message": "No pods selected for deletion."}), 400

    for pod in pods:
        subprocess.run(["bash", "scripts/delete_pod.sh", pod["name"]])

    return jsonify({"message": "Selected pods deleted successfully."})

@app.route('/get_routes')
def get_routes():
    try:
        output = subprocess.run(["bash", "scripts/get_routes.sh"], capture_output=True, text=True)
        route_data = [line.split() for line in output.stdout.split("\n") if line.strip()]
        return jsonify({"routes": [{"name": route[0], "url": route[1]} for route in route_data]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/delete_routes', methods=['POST'])
def delete_routes():
    data = request.get_json()
    routes = data.get("items", [])

    if not routes:
        return jsonify({"message": "No routes selected for deletion."}), 400

    for route in routes:
        subprocess.run(["bash", "scripts/delete_route.sh", route["name"]])

    return jsonify({"message": "Selected routes deleted successfully."})

@app.route('/get_services')
def get_services():
    return jsonify({"output": execute_script("scripts/get_services.sh")})

@app.route('/get_pvc')
def get_pvc():
    return jsonify({"output": execute_script("scripts/get_pvc.sh")})

if __name__ == '__main__':
    app.run(debug=True)
