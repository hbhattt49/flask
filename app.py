from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/custom_routes')
def custom_routes():
    return render_template('custom_route_page.html')

@app.route('/get_active_routes')
def get_active_routes():
    try:
        result = subprocess.run(["oc", "get", "routes", "--no-headers"], capture_output=True, text=True)
        routes = []
        for line in result.stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 3:
                routes.append({
                    "application": parts[0],
                    "url": parts[1],
                    "port": parts[2]  # adjust based on your cluster's column order
                })
        return jsonify({"routes": routes})
    except Exception as e:
        return jsonify({"routes": [], "error": str(e)})

@app.route('/create_custom_route', methods=['POST'])
def create_custom_route():
    data = request.get_json()
    app_name = data.get("app_name")
    custom_url = data.get("custom_url")
    port = data.get("port")

    if not app_name or not custom_url or not port:
        return jsonify({"message": "All fields are required."}), 400

    try:
        command = [
            "oc", "expose", "svc/{}".format(app_name),
            "--name", custom_url,
            "--port", port,
            "--hostname", custom_url
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"message": f"Route created for {app_name} at {custom_url}"})
        else:
            return jsonify({"message": result.stderr.strip()}), 500
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
