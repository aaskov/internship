# -*- coding: utf-8 -*-
from flask import Flask
from flask import jsonify
from flask import request
from flask_swagger_ui import get_swaggerui_blueprint


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


# Define the '/solver' endpoint
@app.route("/solver", methods=["POST"])
def solver():
    request_data = request.get_json()

    # ---
    # Call solution
    # ---


    # ---
    # Construct output allocation
    # ---



    # ---
    # Set return parameters
    # ---


    return jsonify({
        "Message": request_data['message']
    })



# ==============================================================================
# RUN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
