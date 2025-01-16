@app.route('/one_time_setup', methods=['POST'])
def one_time_setup():
    def generate():
        process = subprocess.Popen(['./one_time_setup.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in iter(process.stdout.readline, ''):
            yield f"data: {line.strip()}\\n\\n"
        process.stdout.close()
        return_code = process.wait()
        if return_code != 0:
            yield f"data: Error occurred: {process.stderr.read()}\\n\\n"
        else:
            yield "data: Setup complete!\\n\\n"

    return Response(generate(), mimetype='text/event-stream')
