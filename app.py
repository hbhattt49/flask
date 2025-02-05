@app.route('/modify_pvc', methods=['POST'])
def modify_pvc():
    data = request.get_json()
    pvc_name = data.get("pvc_name")
    new_size = data.get("new_size")

    if not pvc_name or not new_size:
        return jsonify({"message": "PVC name and new size are required"}), 400

    try:
        result = subprocess.run(["bash", "scripts/modify_pvc.sh", pvc_name, new_size], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"message": f"PVC {pvc_name} resized to {new_size} successfully."})
        else:
            return jsonify({"message": f"Error: {result.stderr}"}), 500
    except Exception as e:
        return jsonify({"message": str(e)}), 500
