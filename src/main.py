import os
import json
import os
import sqlite3
import requests
from flask import Flask, request, jsonify, url_for, redirect
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from oauthlib.oauth2 import WebApplicationClient
from utils import APIException, generate_sitemap, add_user_authentification
from admin import setup_admin
from models import db, User, UserOAuth
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.url_map.strict_slashes = False
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
    return UserOAuth.get(user_id)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

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

    print("You just got every single user")

    return jsonify(User.getUsers()), 200

@app.route('/user/<int:id>', methods=['GET'])
def handle_user_by_id(id):
    
    print(f"You just got the user by id = {id}")
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

@app.route("/login")
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
        picture = userinfo_response.json()["picture"]
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






  
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
