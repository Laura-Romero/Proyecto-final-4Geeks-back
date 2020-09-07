"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap, add_user_authentification
from admin import setup_admin
from models import db, User, Widget_property
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])

def handle_user():
    return  jsonify(User.getUsers()), 200
    

@app.route('/user/<int:id>', methods=['GET'])
def handle_user_by_id(id):
    
    status_user = User.get_user_by_id(id)
    if status_user == False:
        return "Not Found", 400
    else:
        return jsonify(User.get_user_by_id(id)), 200

@app.route('/user', methods=['POST'])
def create_user():
    new_user = User()
    user_data = request.get_json()
    authentification = add_user_authentification(user_data)    

    if authentification == True:
        new_user.add_user(user_data)
        return "New user created", 200
    else:
        return "Oops! Looks like something went wrong", 406

@app.route('/user/<int:id>', methods=['PUT', 'PATCH'])
def modify_user_info(id):
    data_to_modify = request.get_json()
    User.update_user_info(id, data_to_modify)

    return f"the user number {id} has been modified", 201

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user_by_id(id):
    User.delete_user(id)
    return "user delete"

@app.route('/widgets/<int:id>', methods=['GET'])
def get_properties_by_widget_id(id):

    widget_props = Widget_property.get_widget_properties(id)
    if widget_props == False:
        return "NOT FOUND", 404
    else:
        return jsonify(widget_props), 200

@app.route('/widgets/<int:id>/properties', methods=['POST'])
def add_properties_to_widget(id):
    new_props = Widget_property()
    prop_data = request.get_json()    
    new_props.set_prop(id, prop_data)
    return "New props added", 200   

@app.route('/widgets/<int:id>/properties', methods=['PUT', 'PATCH'])
def modify_properties(id):
    data_to_modify = request.get_json()
    Widget_property.update_props(id, data_to_modify)

    return f"the property of the widget number {id} has been modified", 201

@app.route('/widgets/<int:id>/properties', methods=['DELETE'])
def delete_widget_props(id):

    return "props deleted", 200




# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
