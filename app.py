# -*- coding: utf-8 -*-
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

# Define the '/test' endpoint
@app.route("/test", methods=["POST"])
def test():
    request_data = request.get_json()
    return jsonify(request_data)


# Define the '/solver' endpoint
@app.route("/solver", methods=["POST"])
def solver():
    request_data = request.get_json()

    # Map to variables
    all_internships = request_data['all_internships']
    all_location_names = request_data['all_location_names']
    all_location_capacities = request_data['all_location_capacities']
    #all_student_priorities = request_data['all_student_priorities']
    all_week_names = request_data['all_week_names']
    allocation_rule = request_data['allocation_rule']
    all_student_names = request_data['all_student_names']
    max_time = request_data['max_time']


    # ---
    # Debug arguments
    # ---
    if True:
        print("")
        print("==================")
        print("all_internships")
        print("------------------")
        print(all_internships)
        print("")
        print("==================")
        print("all_location_names")
        print("------------------")
        print(all_location_names)
        print("")
        print("==================")
        print("all_location_capacities")
        print("------------------")
        print(all_location_capacities)
        print("")
        print("==================")
        print("all_week_names")
        print("------------------")
        print(all_week_names)
        print("")
        print("==================")
        print("allocation_rule")
        print("------------------")
        print(allocation_rule)
        print("")
        print("==================")
        print("all_student_names")
        print("------------------")
        print(all_student_names)
        print("")


    # ---
    # Call solution
    # ---
    assignment, solver, status = solve_internship(all_location_names=all_location_names, 
                                                  all_location_capacities=all_location_capacities, 
                                                  all_student_names=all_student_names, 
                                                  all_week_names=all_week_names, 
                                                  all_internships=all_internships, 
                                                  allocation_rule=allocation_rule,
                                                  max_time=max_time)

    # ---
    # Construct output allocation
    # ---
    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        
        # Construct a dictionary of assignments
        solution = list()

        for s in range(len(all_student_names)):
            _new_entries = list()

            for w in range(len(all_week_names)):
                _new_entry = dict()

                for i in range(len(all_internships)):
                    for j in range(len(all_internships[i])):

                        # Only append if True in assignment
                        if solver.Value(assignment[(s,w,i,j)]):

                            # Append anythig
                            if len(_new_entries) == 0:
                                _new_entry["student"] = all_student_names[s]
                                _new_entry["start_week"] = all_week_names[w]
                                _new_entry["duration"] = 1
                                _new_entry["location"] = all_location_names[all_internships[i][j]]
                                _new_entry["internship"] = i
                                _new_entries.append(_new_entry)
                            else:
                                # Check if previous entry matches current internship
                                if _new_entries[-1]["internship"] == i:
                                    _new_entries[-1]["duration"] += 1

                                else:
                                    # Insert a new entry
                                    _new_entry["student"] = all_student_names[s]
                                    _new_entry["start_week"] = all_week_names[w]
                                    _new_entry["duration"] = 1
                                    _new_entry["location"] = all_location_names[all_internships[i][j]]
                                    _new_entry["internship"] = i
                                    _new_entries.append(_new_entry)

            # Copy list to solution
            for e in _new_entries:
                solution.append(e)


        # Return
        return jsonify({
            "is_feasible": status == cp_model.FEASIBLE,
            "is_optimal": status == cp_model.OPTIMAL,
            "objective": solver.ObjectiveValue(),
            "conflicts": solver.NumConflicts(),
            "branches": solver.NumBranches(),
            "wall_time": solver.WallTime(),
            "solution": solution
        })

    else:
        # Return
        return jsonify({
            "is_feasible": status == cp_model.FEASIBLE,
            "is_optimal": status == cp_model.OPTIMAL
            })



# ==============================================================================
# RUN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
