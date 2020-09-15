import os
import jwt
from flask import Flask, request, jsonify, url_for, make_response
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap, add_user_authentification
from admin import setup_admin
from models import db, User
from functools import wraps

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEYS')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

def token_required(f):
    #Este wraps debes importarlo
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #el header tiene dentro un objeto, X-Access-Point es la key
        if 'X-Access-Point' in request.headers:
            token = request.headers['X-Access-Point']
        
        if not token:
            return jsonify({'message': 'token missing'}, 401)
        
        try:
         
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.get_user_by_username(data['username'])
            
        except:
            return jsonify({'message': 'token is invalid'}), 401

    
        return f(current_user, *args, **kwargs)
    
    return decorated


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_every_user():
    return jsonify(User.getUsers()), 200

@app.route('/user/<int:id>', methods=['GET'])
@token_required
def handle_user_by_id(current_user, id):

    status_user = User.get_user_by_id(id)
    
    if current_user['username'] != status_user['username']:
        return jsonify({'message': 'cannot perfom function'})
        
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
@token_required
def modify_user_info(id):
    data_to_modify = request.get_json()
    User.update_user_info(id, data_to_modify)

    return f"the user number {id} has been modified", 201

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user_by_id(id):
    User.delete_user(id)
    return "user delete"

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return jsonify({'message': 'no user found'})

    if user.password == auth.password:
        token = jwt.encode({'username': user.username}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})


  
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
