# app/__init__.py
from flask import Flask
from flask_cors import CORS
import os
import json


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # project_dir = os.getcwd()
    # #project_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))
    # with open('config.json', 'r') as file:
    #     settings = json.load(file)
    #     exec_path = settings['exec_path']
    #     reservoir_data = settings['reservoir_data_path']
    #     outputs_dir = settings['outputs_dir']
    #     outputs = settings['output_name']
    #     optimize_outputs = settings['optimize_name']
    #
    # # Configure the app
    # app.config.from_mapping(
    #     SECRET_KEY='co2block',
    #     PROJECT_DIR=project_dir,
    #     CUR_DIR=project_dir,
    #     DATA_PATH=os.path.join(project_dir, reservoir_data),
    #     EXE_PATH=os.path.join(project_dir, exec_path),
    #     OPTIMIZE_PATH=os.path.join(project_dir, outputs_dir, optimize_outputs),
    #     OPTIMIZE_OUTPUT=optimize_outputs,
    #     OUTPUTS_DIR=os.path.join(project_dir, outputs_dir),
    #     OUTPUTS=outputs
    # )

    # Register routes
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app


# cur_dir = os.getcwd()
# project_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))
# print(project_dir)
# with open(project_dir + '\\config.json', 'r') as file:
#     settings = json.load(file)
#     exec_path = settings['exec_path']
#     reservoir_data = settings['reservoir_data_path']
#     outputs_dir = settings['outputs_dir']
#     outputs = settings['output_name']
#     optimize_outputs = settings['optimize_name']
# print(os.path.join(project_dir, outputs_dir, optimize_outputs))
