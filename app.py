from flask import Flask, render_template, send_file, jsonify
from flask import make_response
from flask import request
import zipfile
import os
from jinja2 import Template

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/generate_project', methods=['POST'])
def generate_project():
    template = Template(open('templates/blink.ino.j2').read())
    ino_content = template.render()
    zip_file = zipfile.ZipFile('blink.zip', 'w')
    zip_file.writestr('blink/blink.ino', ino_content)
    zip_file.close()
    return send_file('blink.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
