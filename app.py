from flask import Flask, render_template, send_file, jsonify, request
from flask import make_response
import zipfile
import os
import subprocess
import shutil

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/generate_project', methods=['POST'])
def generate_project():
    repo_url = 'https://github.com/tomjuggler/SmartPoi-Firmware.git'
    repo_name = 'SmartPoi-Firmware'

    # Clone the repository
    subprocess.run(['git', 'clone', repo_url, repo_name])

    # Create the zip file
    zip_file_name = 'SmartPoi-Firmware.zip'
    zip_file = zipfile.ZipFile(zip_file_name, 'w')
    for root, dirs, files in os.walk(repo_name):
        for file in files:
            file_path = os.path.join(root, file)
            zip_file.write(file_path, os.path.relpath(file_path, repo_name))
    zip_file.close()

    # Remove the cloned repository
    shutil.rmtree(repo_name)

    # Send the zip file as a download
    return send_file(zip_file_name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
