# -*- coding: utf-8 -*-
import os
import uuid
import pickle
import threading
from flask import Flask
from flask import jsonify
from flask import request
from flask_swagger_ui import get_swaggerui_blueprint
from ortools.sat.python import cp_model
from solver import solve_internship



# ==============================================================================
# VARIABLES
# ------------------------------------------------------------------------------

app = Flask(__name__)

# This is related to the swagger definiton
SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"



# ==============================================================================
# SWAGGER BLUEPRINT CONFIGURATION
# ------------------------------------------------------------------------------

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Internship API'
    }
)

# Add to app
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


# ==============================================================================
# MAIN INTERFACE
# ------------------------------------------------------------------------------

# Define the '/' endpoint
@app.route("/")
def home():
    return jsonify({
        "Message": "App is up and running successfully"
    })

# Define the '/echo' endpoint
@app.route("/echo", methods=["POST"])
def echo():
    request_data = request.get_json()
    return jsonify(request_data)


# Define the '/check' endpoint
@app.route("/check", methods=["POST"])
def check():
    request_data = request.get_json()

    # Map to variables
    guid = request_data['guid']

    # Now check if file is ready to be returned
    if os.path.isfile(f"{guid}.pkl"):
        return jsonify({"guid": guid, "is_ready": True})

    else:
        return jsonify({"guid": guid, "is_ready": False})


# Define the '/solution' (POST) endpoint
@app.route("/solution", methods=["POST"])
def solution():
    request_data = request.get_json()

    # Map to variables
    guid = request_data['guid']

    # Load pickle
    with open(f"{guid}.pkl", 'rb') as f:
        element = pickle.load(f)

    if "solution" in element:
        response = {"is_feasible": element["is_feasible"],
                    "is_optimal": element["is_optimal"],
                    "objective": element["objective"],
                    "conflicts": element["conflicts"],
                    "branches": element["branches"],
                    "wall_time": element["wall_time"],
                    "solution": element["solution"]}
    else:
        response = {"is_feasible": element["is_feasible"],
                    "is_optimal": element["is_optimal"]}

    return(jsonify(response))


# Define the '/solver' (POST) endpoint
@app.route("/solver", methods=["POST"])
def solver():
    request_data = request.get_json()

    # Map to variables
    all_internships = request_data['all_internships']
    all_location_names = request_data['all_location_names']
    all_location_capacities = request_data['all_location_capacities']
    all_student_priorities = request_data['all_student_priorities']
    all_week_names = request_data['all_week_names']
    allocation_rule = request_data['allocation_rule']
    all_student_names = request_data['all_student_names']
    max_time = request_data['max_time']


    # ---
    # Create a unique reference for data in/out
    # ---
    guid = uuid.uuid4()

    # ---
    # Call a threaded solver
    # ---
    x = threading.Thread(target=solve_internship, args=(all_location_names,
                                                        all_location_capacities,
                                                        all_student_names,
                                                        all_student_priorities,
                                                        all_week_names,
                                                        all_internships,
                                                        allocation_rule,
                                                        guid,
                                                        max_time))
    x.start()

    # ---
    # Construct response
    # ---
    return jsonify({"guid": guid})



# ==============================================================================
# RUN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
