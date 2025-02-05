@app.route('/get_routes')
def get_routes():
    try:
        output = subprocess.run(["bash", "scripts/get_routes.sh"], capture_output=True, text=True)
        route_data = []

        for line in output.stdout.split("\n"):
            if line.strip():
                parts = line.split()
                route_data.append({"name": parts[0], "url": parts[1] if len(parts) > 1 else "N/A"})

        return jsonify({"routes": route_data})
    except Exception as e:
        return jsonify({"error": str(e)})
