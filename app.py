@app.route('/deploy', methods=['GET'])
def deploy():
    def generate():
        # Run the deploy.sh script
        process = subprocess.Popen(['./deploy.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            # Stream stdout line by line
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield f"data: {line.strip()}\\n\\n"
            process.stdout.close()
            return_code = process.wait()
            if return_code != 0:
                yield f"data: Error occurred: {process.stderr.read()}\\n\\n"
        except Exception as e:
            yield f"data: Exception occurred: {str(e)}\\n\\n"
    return Response(generate(), mimetype='text/event-stream')
