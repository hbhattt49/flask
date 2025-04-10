from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/custom_routes')
def custom_routes():
    return render_template('custom_route_page.html')

@app.route('/get_active_routes')
def get_active_routes():
    try:
        # Run a shell script to get routes and service info
        result = subprocess.run(["bash", "scripts/get_routes_and_services.sh"], capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"routes": [], "error": result.stderr.strip()}), 500

        # Convert stdout to a list of dicts using eval (assuming script outputs JSON-like Python list)
        routes = eval(result.stdout.strip())
        return jsonify({"routes": routes})
    except Exception as e:
        return jsonify({"routes": [], "error": str(e)}), 500

@app.route('/create_custom_route', methods=['POST'])
def create_custom_route():
    data = request.get_json()
    app_name = data.get("app_name")
    custom_url = data.get("custom_url")
    port = data.get("port")

    if not app_name or not custom_url or not port:
        return jsonify({"message": "All fields are required."}), 400

    try:
        # Use a script to execute oc expose
        result = subprocess.run(["bash", "scripts/create_custom_route.sh", app_name, custom_url, port], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"message": f"Route created for {app_name} at {custom_url}"})
        else:
            return jsonify({"message": result.stderr.strip()}), 500
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
