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

    # Get the values from the request
    data_pin = request.form['data_pin']
    clock_pin = request.form['clock_pin']
    num_pixels = int(request.form['num_pixels'])

    # Modify the main.ino file
    main_ino_path = os.path.join(repo_name, 'main', 'main.ino')
    with open(main_ino_path, 'r') as f:
        lines = f.readlines()
    with open(main_ino_path, 'w') as f:
        for line in lines:
            if line.startswith('#define DATA_PIN'):
                f.write(f'#define DATA_PIN {data_pin}\n')
            elif line.startswith('#define CLOCK_PIN'):
                f.write(f'#define CLOCK_PIN {clock_pin}\n')
            elif line.startswith('#define NUM_LEDS'):
                f.write(f'#define NUM_LEDS {num_pixels + 1}\n')
            elif line.startswith('#define NUM_PX'):
                f.write(f'#define NUM_PX {num_pixels}\n')
            else:
                f.write(line)

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
