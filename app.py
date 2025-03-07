from flask import Flask, render_template, send_file, jsonify, request, send_from_directory
from flask import make_response
import zipfile
import os
import subprocess
import shutil
import re

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/generate_project', methods=['POST'])
def generate_project():
    repo_url = 'https://github.com/tomjuggler/SmartPoi-Firmware.git'
    repo_name = 'SmartPoi-Firmware'

    # Check if the repository exists, if not clone it
    if not os.path.exists(repo_name):
        subprocess.run(['git', 'clone', repo_url, repo_name])
    # Stash local changes before switching branches
    subprocess.run(['git', '-C', repo_name, 'stash'])
    # Switch to main branch before pulling updates
    subprocess.run(['git', '-C', repo_name, 'checkout', 'main'])
    # Check for updates and pull if necessary
    subprocess.run(['git', '-C', repo_name, 'fetch', 'origin'])
    subprocess.run(['git', '-C', repo_name, 'merge', 'origin/main'])

    # Get the values from the request
    data_pin = request.form['data_pin']
    clock_pin = request.form['clock_pin']
    num_pixels = int(request.form['num_pixels'])
    ap_name = request.form['ap_name']
    ap_pass = request.form['ap_pass']
    led_type = request.form['led_type']
    horizontal_pixels = 180 # todo: this is too large for 100 - fix below using better hack:

    if num_pixels > 100:
        horizontal_pixels = 160
    if num_pixels > 120: 
        horizontal_pixels = 140
    if num_pixels > 140: 
        horizontal_pixels = num_pixels 
    # Determine the correct directory in static/bins/bin_ based on num_pixels
    size_dirs = {
        36: "bin_36",
        60: "bin_60",
        72: "bin_72",
        120: "bin_120",
        144: "bin_144",
    }
    bin_dir = size_dirs.get(num_pixels, "bin_")
    bin_path = os.path.join("static/bins", bin_dir)

    # Create the data directory in the repo if it doesn't exist
    data_path = os.path.join(repo_name, 'main', 'data')
    os.makedirs(data_path, exist_ok=True)

    # Remove all existing .bin files from the data directory
    for file in os.listdir(data_path):
        if file.endswith(".bin"):
            os.remove(os.path.join(data_path, file))

    # Copy new .bin files from the determined directory to the data directory
    for file in os.listdir(bin_path):
        if file.endswith(".bin"):
            shutil.copy(os.path.join(bin_path, file), data_path)

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
            elif re.match(r'^\s*//\s*#define LED_APA102', line):
                if led_type == 'APA102':
                    f.write('#define LED_APA102')
                else:
                    f.write(re.sub(r'^\s*//\s*#define LED_APA102', '// #define LED_APA102', line))
            elif re.match(r'^\s*#define LED_APA102', line):
                if led_type == 'APA102':
                    f.write('#define LED_APA102')
                else:
                    f.write(re.sub(r'^\s*#define LED_APA102', '// #define LED_APA102', line))
            elif line.startswith('#define NUM_LEDS'):
                f.write(f'#define NUM_LEDS {num_pixels + 1}\n')
            elif line.startswith('#define NUM_PX'):
                f.write(f'#define NUM_PX {num_pixels}\n')
            elif line.startswith('const int maxPX'):
                f.write(f'const int maxPX = {num_pixels * horizontal_pixels};\n')
            elif line.startswith('char apName[]'):
                f.write(f'char apName[] = "{ap_name}";\n')
            elif line.startswith('char apPass[]'):
                f.write(f'char apPass[] = "{ap_pass}";\n')
            elif line.startswith('boolean auxillary'):                                                                                                                        
                f.write('boolean auxillary = false;\n')
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

    # Send the zip file as a download
    response = make_response(send_file(zip_file_name, as_attachment=True))
    response.headers['Content-Disposition'] = 'attachment; filename="SmartPoi_Firmware.zip"'
    return response

if __name__ == '__main__':
    app.run()
