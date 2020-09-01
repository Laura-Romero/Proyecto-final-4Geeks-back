from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    fullname = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(30), unique=False, nullable=True)
    twitter = db.Column(db.String(30), unique=True, nullable=True)
    country = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    # CHILDREN
    twitter = db.relationship('Twitter', lazy=True)
    task = db.relationship('Task', lazy=True)
    weather = db.relationship('Weather', lazy=True) 
    mail = db.relationship('Mail', lazy=True)
    clock = db.relationship('Clock', lazy=True)
    compliment = db.relationship('Compliment', lazy=True)
    

    def __repr__(self):
        return f'<User {self.username}>' 

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "fullname": self.fullname,
            "email": self.email,
            "twitter": self.twitter,
            "country": self.country,
            "city": self.city
        }
    
    def add_user(user_data):
        new_user = User()
        new_user.username = user_data['username']
        new_user.password = user_data['password']
        new_user.fullname = user_data['fullname']
        new_user.email = user_data['email']
        new_user.country = user_data['country']
        new_user.city = user_data['city']
        new_user.is_active = user_data['is_active']

        db.session.add(new_user)
        db.session.commit()
    
    def getUsers():
        all_users = User.query.all()
        all_users = list(map(lambda x: x.serialize(), all_users))
        return all_users

    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        user = user.serialize()
        return user

    def modify_user(user_id, new_value):
        user = User.query.get(user_id)
        keys = new_value.keys()
        user[keys] = 2
        db.session.commit()
        # user = User.query.get(2)
        # user.username = "MARICO EL QUE LO LEA"
        # db.session.commit()

    


class Twitter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    token = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=True)
    is_active = db.Column(db.Boolean(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    

    def __repr__(self):
        return f'<Twitter {id}>'

    def __serialize__(self):
        return {
            "id": self.id,
            "position": self.position,
            "is_active": self.is_active
        }
        
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    task = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f'Task: {task}'

    def __serialize__(self):
        return {
            'UserId': self.id,
            'task': self.task
        }

class Mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    token = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=True)
    is_active = db.Column(db.Boolean(), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f'<Mail {id}>'

    def __serialize__(self):
        return {
            "id": self.id,
            "position": self.position,
            "is_active": self.is_active
        }

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=True)
    is_active = db.Column(db.Boolean(), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f'<Weather {position}>'
    
    def __serailize__(self):
        return {
            "id": self.id,
            "position": self.position,
            "is_active": self.is_active
        }

class Clock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=True)
    is_active = db.Column(db.Boolean(), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f'<Time {position}>'
    
    def __serailize__(self):
        return {
            "id": self.id,
            "position": self.position,
            "is_active": self.is_active
        }

class Compliment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.Integer, unique=True, nullable=True)
    is_active = db.Column(db.Boolean(), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f'<Time {position}>'
    
    def __serailize__(self):
        return {
            "id": self.id,
            "position": self.position,
            "is_active": self.is_active
        }