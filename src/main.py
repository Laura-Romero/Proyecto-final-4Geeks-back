"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap, add_user_authentification
from admin import setup_admin
from models import db, User
import bcrypt
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

@app.route('/login', methods=['POST'])
def login():
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return 'Missing email', 400
    if not password:
        return 'Missing password', 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return 'User not found', 400

    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return f'Welcome back {username}'
    else:
        return 'Wrong password'

@app.route('/user', methods=['GET'])
def handle_user():
    return jsonify(User.getUsers()), 200

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
    check_new_username = request.json.get('username', None)
    check_new_password = request.json.get('password', None)

    if not check_new_username:
        return 'Missing username', 400
    if not check_new_password:
        return 'Missing Password', 400    

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
  
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
