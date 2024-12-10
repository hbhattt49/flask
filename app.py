@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Run scripts and get results
    abc_result = subprocess.run(['bash', './abc.sh'], capture_output=True, text=True).stdout
    xyz_result = subprocess.run(['bash', './xyz.sh'], capture_output=True, text=True).stdout
    
    # Placeholder or logic for Index result
    index_result = "Index tile content here."

    return render_template('home.html', abc_result=abc_result, xyz_result=xyz_result, index_result=index_result)
