import os
import json
import os
import sqlite3
import requests
import jwt
import bcrypt
import twitter
import tweepy

from flask import Flask, request, jsonify, url_for, redirect,  make_response

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from oauthlib.oauth2 import WebApplicationClient
from utils import APIException, generate_sitemap, add_user_authentification
from admin import setup_admin
from models import db, User, Widget_property
from functools import wraps
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "130980975494-b5rfm4afsnvjr3jeqm4vn3i9l37vn0a5.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "L8AbO4iGJCMWvsLcSGqPHi4q")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEYS')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
  
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

@app.route('/twitter')
def Get_tweets():
    auth = twitter.twitter_auth()
    client = twitter.get_twitter_client(auth)
    if __name__ == 'main':
        user = 'JuanGCardinale'
        tw_client = client
        users_locs = [[tweet.user.screen_name, tweet.text] for tweet in tweepy.Cursor(client.home_timeline, screen_name=user).items(2)]
    return jsonify(users_locs)
    

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
        token = jwt.encode({'username': user.username}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
        # return f'Welcome back {username}'
    else:
        return 'Wrong password'
      
@app.route('/user', methods=['GET'])
@token_required
def get_every_user(current_user):
    print(current_user)
    return jsonify(current_user), 200

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
    check_new_username = request.json.get('username', None)
    check_new_password = request.json.get('password', None)
    
    if not check_new_username:
        return 'Missing username', 400
    if not check_new_password:
        return 'Missing Password', 400    
    if authentification == True:
        user = new_user.add_user(user_data)
        print(user)
        return jsonify(user.serialize()), 200
    else:
        return "Oops! Looks like something went wrong", 406

@app.route('/user/<int:id>', methods=['PUT', 'PATCH'])
# @token_required
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

@app.route("/login", methods=["GET"])
def loginOAuth():
    #return request.base_url, 200
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace('http://', 'https://') + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    print('code')

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace('http://', 'https://'),
        redirect_url=request.base_url.replace('http://', 'https://') ,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
       fullname=users_name, email=users_email, username=users_name
    )
    #LINEA 170 CAMBIAR QUERY POR FUNCION GET BY EMAIL DESPUES DEL MERGE
    # Doesn't exist? Add it to the database.
    if not user.query.filter_by(email=users_email).first():
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("sitemap").replace('http://', 'https://'))


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)





# @app.route('/login', methods=['POST'])
# def login():
#     auth = request.authorization
#     if not auth or not auth.username or not auth.password:
#         return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

#     user = User.query.filter_by(username=auth.username).first()

#     if not user:
#         return jsonify({'message': 'no user found'})

#     if user.password == auth.password:
#         token = jwt.encode({'username': user.username}, app.config['SECRET_KEY'])
#         return jsonify({'token': token.decode('UTF-8')})

#     return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
