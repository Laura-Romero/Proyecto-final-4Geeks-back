from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, select, String, Text

# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

db = SQLAlchemy()

association_table = db.Table('association', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey("user.id")),
    db.Column('widget_id', db.Integer, db.ForeignKey("widget.id")),
    db.Column('status', db.Boolean(), nullable=False),
    db.Column('position', db.Integer, nullable=False)
)


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
    # ASSOCIATION
    widgets = db.relationship("Widget",
                secondary=association_table,
                back_populates="users"
    )
    

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

class Widget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    widget_type = db.Column(db.Enum('Twitter', 'Gmail', 'Tasks', 'Weather', 'Clock', 'Compliments'), unique=True, nullable=False)
    #ASSOCIATION
    users = db.relationship("User",
                secondary=association_table,
                back_populates="widgets"
    )

    def __repr__(self):
        return f'<Widget: {self.widget_type}>'

    def serialize(self):
        return {
            "id": self.id,
            "widget_type": self.widget_type
        }
class Widget_property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    widget_property = db.Column(db.String(250), unique=False, nullable=False)
    property_value = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Widget_Property {self.widget_property}>'
    
    def __serailize__(self):
        return {
            "id": self.id,
            "widget_property": self.widget_property,
            "property_value": self.property_value
        }