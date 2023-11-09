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
    all_student_names = request_data['all_student_names']
    all_week_names = request_data['all_week_names']
    allocation_rule = request_data['allocation_rule']
    


    # ---
    # Call solution
    # ---
    assignment, solver, status = solve_internship(all_location_names=all_location_names, 
                                                  all_location_capacities=all_location_capacities, 
                                                  all_student_names=all_student_names, 
                                                  all_week_names=all_week_names, 
                                                  all_internships=all_internships, 
                                                  allocation_rule=allocation_rule)

    # ---
    # Construct output allocation
    # ---
    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        
        # Construct a dictionary of assignments
        solution = dict()
        for s in range(len(all_student_names)):
            solution[all_student_names[s]] = dict()

            for w in range(len(all_week_names)):
                for i in range(len(all_internships)):
                    for j in range(len(all_internships[i])):
                        if solver.Value(assignment[(s,w,i,j)]):
                            solution[all_student_names[s]][all_week_names[w]] = f"Assigned internship {i} at location {all_location_names[all_internships[i][j]]}"

        # Return
        return jsonify({
            "is_feasible": f"{status == cp_model.FEASIBLE}",
            "is_optimal": f"{status == cp_model.OPTIMAL}",
            "objective": f"{solver.ObjectiveValue()}",
            "conflicts": f"{solver.NumConflicts()}",
            "branches": f"{solver.NumBranches()}",
            "wall_time": f"{solver.WallTime()}",
            "solution": solution
        })

    else:
        # Return
        return jsonify({
            "is_feasible": f"{status == cp_model.FEASIBLE}",
            "is_optimal": f"{status == cp_model.OPTIMAL}"
            })



# ==============================================================================
# RUN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
