import json

from flask import Flask, request, render_template, redirect, url_for, flash, send_file, jsonify, send_from_directory
import os
import subprocess
import time
from PIL import Image
import io

# Path to your .exe file
exe_path = "C:\\Users\\14569\\Desktop\\IRP\\dev\\CO2BLOCK\\executables\\CO2BLOCK.exe"

app = Flask(__name__)
app.secret_key = '123'

with open('config.json', 'r') as file:
    settings = json.load(file)
    exec_path = settings['exec_path']
    cur_dir = settings['current_dir']
    outputs_dir = cur_dir + settings['outputs_dir']
    outputs = list(settings['output_name'])

fpath = cur_dir
fname = 'temp.xlsx'

print(outputs)
# correction, dist_min, dist_max, nr_dist, nr_well_max, rw, time_yr, maxQ

# home page route
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/run', methods=['POST'])
def run():
    # Extract form data
    correction = request.form.get('correction')
    dist_min = request.form.get('dist_min')
    dist_max = request.form.get('dist_max')
    nr_dist = request.form.get('nr_dist')
    nr_well_max = request.form.get('nr_well_max')
    rw = request.form.get('rw')
    time_yr = request.form.get('time_yr')
    maxQ = request.form.get('maxQ')

    output_file = run_executable(correction, dist_min, dist_max, nr_dist, nr_well_max, rw, time_yr, maxQ)

    if not output_file:
        flash('Failed to process the file.', 'error')
        return render_template('index.html')
    return redirect(url_for('home'))


def run_executable(fpath, fname, correction, dist_min, dist_max, nr_dist, nr_well_max, rw, time_yr, maxQ):
    output_path = 'output.txt'

    try:
        result = subprocess.run([exe_path, fpath, fname, correction, str(dist_min), str(dist_max), str(nr_dist),
                                 str(nr_well_max), str(rw), str(time_yr), str(maxQ)],
                                capture_output=True, text=True, encoding='utf-8')
        print(result)

    except Exception as e:
        print(e)
        return None
    return output_path


@app.route('/images')
def get_images():
    # Generate URLs for the images
    image_urls = [url_for('serve_image', filename=output) for output in outputs]
    return jsonify(image_urls)


@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(outputs_dir, filename)


if __name__ == '__main__':
    # run_executable('C:\\Users\\14569\\Desktop\\IRP\\dev\\','example_data.xlsx', 'off', 2, 'auto', 30, 15, 0.2, 30, 5)
    app.run(debug=True,port=4000)
