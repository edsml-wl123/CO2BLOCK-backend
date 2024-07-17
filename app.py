# backend/app.py
from flask import Flask, jsonify, request, render_template, send_from_directory, url_for
from flask_cors import CORS
import pandas as pd
from copy import deepcopy
import subprocess
import matplotlib.pyplot as plt
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

entered_inputs, entered_limits, optimize_inputs = {}, {}, None

with open('config.json', 'r') as file:
    settings = json.load(file)
    exec_path = settings['exec_path']
    cur_dir = settings['current_dir']
    outputs_dir = cur_dir + settings['outputs_dir']
    outputs = settings['output_name']
    optimize_result = settings['optimize_name']

fpath = cur_dir
fname = 'temp.xlsx'


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/reservoirs', methods=['GET'])
def send_reservoirs():
    reservoirs = pd.read_excel('./CO2BLOCK/data/reservoir_data.xlsx', sheet_name='UK_data')
    reservoirs = reservoirs.to_json(orient='records')

    print(reservoirs)
    if reservoirs:
        return reservoirs
    else:
        return jsonify({"error": "Reservoir not found"}), 404


@app.route('/save-inputs', methods=['POST'])
def save_inputs():
    if os.path.exists(fpath + fname):
        try:
            os.remove(fpath + fname)
            print(f"Temporary file {fname} of last running deleted successfully.")
        except Exception as e:
            print(e)

    inputs = request.get_json()
    global entered_inputs
    entered_inputs = deepcopy(inputs)

    df = pd.DataFrame([inputs])
    columns = ['name', 'domainType', 'minDepth', 'meanDepth', 'thickness', 'area', 'meanPermeability',
               'meanPorosity', 'rockCompressibility', 'waterCompressibility', 'co2Density', 'co2Viscosity',
               'waterViscosity', 'porePressure', 'meanPressure', 'meanTemperature', 'brineSalinity',
               'principalStress', 'stressRatio', 'frictionCoefficient', 'cohesion', 'tensileStrength']
    df = df[columns]

    for column in columns:
        if (column == 'name') | (column == 'domainType'): continue

        value = df[column][0]
        if (value is None) | (value == ''):
            df[column][0] = 0.0
        else:
            df[column][0] = float(df[column][0])
    df.to_excel('temp.xlsx', index=False)
    print('save inputs locally in temporary temp.xlsx')
    return 'backend received inputs', 201


@app.route('/model/enter-inputs/run', methods=['POST'])
@app.route('/model/map/run', methods=['POST'])
def run_model():
    for output in outputs:
        if os.path.exists(outputs_dir + output):
            try:
                os.remove(outputs_dir + output)
            except Exception as e:
                print(e)
    print(f"Outputs from last running deleted successfully")

    limits = request.get_json()
    global entered_limits
    entered_limits = deepcopy(limits)
    result = run_executable(correction=entered_limits['correction'], time_yr=entered_limits['injectionTime'],
                            dist_min=entered_limits['minDistance'], dist_max=entered_limits['maxDistance'],
                            nr_dist=entered_limits['numDistance'], nr_well_max=entered_limits['maxWellNum'],
                            rw=entered_limits['wellRadius'], maxQ=entered_limits['maxQ'])
    if result != 0:
        return result, 201
    return 'CO2BLOCK ran successfully', 201


def run_executable(correction, dist_min, dist_max, nr_dist, nr_well_max, rw, time_yr, maxQ):
    print('running')
    result = ''
    try:
        result = subprocess.run([exec_path, fpath, fname, correction, dist_min, dist_max, nr_dist, nr_well_max, rw,
                                 time_yr, maxQ], capture_output=True, text=True, encoding='utf-8')
        print(result)
        print(result.stdout)

        if result.returncode != 0:
            raise Exception(result.stderr)
    except Exception as e:
        print(e)

    if result.returncode != 0:
        return 'returncode:' + str(result.returncode) + '\n' + result.stderr
    return 0


@app.route('/model/results', methods=['GET'])
def get_results():
    # Generate URLs for the images
    outputs_urls = [url_for('serve_output', filename=output) for output in outputs]
    return jsonify(outputs_urls)


@app.route('/model/results/<filename>')
def serve_output(filename):
    return send_from_directory(outputs_dir, filename)


@app.route('/model/maxScenario', methods=['GET'])
def get_max_scenario():
    df = pd.read_excel(outputs_dir + outputs[3])
    df_value = df.iloc[:, 1:]

    max_value = df_value.max().max()
    print(max_value)

    max_location = df_value.stack().idxmax()
    print(max_location)
    row_header = df.iloc[max_location[0], 0]
    column_header = max_location[1]
    wellNum = int(row_header)
    wellDistance = int(column_header.split('_')[4])
    return {"maxStorage": max_value, "wellNum": wellNum, "wellDistance": wellDistance}


@app.route('/optimize/run', methods=['POST'])
def revenue_optimization():
    if os.path.exists('optimize.png'):
        try:
            os.remove(cur_dir + 'optimize.png')
            print('Optimization result from last running deleted.')
        except Exception as e:
            print(e)

    readOutputs, rates = request.get_json()['readOutputs'], request.get_json()['rates']
    print(rates)
    capture_cost_rate, transport_cost_rate = rates['capture_cost'], rates['transport_cost']
    revenue_rates = rates['revenue']

    try:
        temp = pd.read_excel(fpath + fname)
        name = temp['name'][0]
    except Exception as e:
        name = 'Unknown'

    if readOutputs:
        well_num = max_storage_each_wellNum()
    else:
        well_num = max_storage_each_wellNum(None)
    costs = cost_calculation(well_num, capture_rate=capture_cost_rate, transport_rate=transport_cost_rate)

    revenues, well_nums = [], []
    for rate in revenue_rates:
        revenue, wellNum = [], []
        for dic in costs:
            well_num, storage, cost = dic['wellNum'], dic['maxStorage'], dic['cost']
            revenue.append((storage * rate * 1000000 - cost) / 100000)
            wellNum.append(well_num)
        revenues.append(revenue)
        well_nums.append(wellNum)
    print(revenues)

    plt.figure(figsize=(8, 6))
    colors = ['blue', 'maroon', 'orange', 'purple', 'green', 'navy', 'darkgreen', 'red', 'pink', 'magenta']
    for i in range(len(revenue_rates)):
        plt.plot(well_nums[i], revenues[i], label=f'Revenue = {revenue_rates[i]}€/tCO2', color=colors[i])

    plt.axhline(0, color='black', linestyle='--')

    plt.xlabel('Number of wells, n')
    plt.ylabel('Revenue - Investment (G€)')
    plt.title(name)
    plt.legend()
    plt.tight_layout()
    plt.savefig('optimize.png')
    return 'backend received rates', 201


def max_storage_each_wellNum(max_storage_file=outputs_dir + outputs[3]):
    if max_storage_file is None:
        global optimize_inputs
        df = deepcopy(optimize_inputs)
    else:
        df = pd.read_excel(max_storage_file)

    well_num_storage = []
    for i in range(0, len(df)):
        well_num = df['number_of_wells'][i]
        max_storage = df.iloc[:, 1:].iloc[i].max()
        well_num_storage.append({'wellNum': well_num, 'maxStorage': max_storage})
    return well_num_storage


def cost_calculation(well_num_storage, capture_rate=50, transport_rate=8):
    costs = []
    for pairs in well_num_storage:
        well_num, storage = pairs['wellNum'], pairs['maxStorage']
        drilling_cost = 0
        fixed_cost = 8200 * well_num
        surface_cost = 6120 * well_num
        site_cost = 24097
        monitor_cost = 1530
        storage_cost = (drilling_cost + fixed_cost + surface_cost + site_cost + monitor_cost) * 1.05
        capture_cost = storage * capture_rate * 1000000
        transport_cost = storage * transport_rate * 1000000
        costs.append({'wellNum': well_num, 'maxStorage': storage,
                      'cost': storage_cost + capture_cost + transport_cost})
    print(costs)
    return costs


@app.route('/optimize/upload', methods=['POST'])
def save_optimize_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file:
        print(file)
        global optimize_inputs
        optimize_inputs = pd.read_excel(file)
        return jsonify({'message': 'File successfully uploaded'}), 200


@app.route('/optimize/result', methods=['GET'])
def get_optimize_result():
    outputs_urls = [url_for('serve_optimize', filename='optimize.png')]
    return jsonify(outputs_urls)


@app.route('/optimize/result/<filename>')
def serve_optimize(filename):
    return send_from_directory(cur_dir, filename)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
