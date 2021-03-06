from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, select, String, Text
from flask_login import UserMixin
import bcrypt


db = SQLAlchemy()

association_table = db.Table('association', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey("user.id")),
    db.Column('widget_id', db.Integer, db.ForeignKey("widget.id")),
    db.Column('status', db.Boolean(), nullable=False),
    db.Column('position', db.Integer, nullable=False)
)


class User(db.Model,  UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=True)
    fullname = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(30), unique=False, nullable=True)
    twitter = db.Column(db.String(30), unique=True, nullable=True)
    country = db.Column(db.String(50), unique=False, nullable=True)
    city = db.Column(db.String(50), unique=False, nullable=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=True)
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

    @classmethod
    def add_user(cls, user_data):
        new_user = cls(
        username = user_data['username'],
        password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()),
        fullname = user_data['fullname'],
        email = user_data['email'],
        country = user_data['country'],
        city = user_data['city'],
        is_active = True
        )

        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def getUsers():
        all_users = User.query.filter_by(is_active = True)
        all_users = list(map(lambda x: x.serialize(), all_users))
        return all_users

    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        
        if user.is_active == True:
            return user.serialize()
        else:
            return False
    def get_user_by_username(user_name):
        
        user = User.query.filter_by(username = user_name).first()
        user = user.serialize()
        return user

    def delete_user(id):
        user = User.query.get(id)
        user.is_active = False
        db.session.commit()

    def update_user_info(user_id, new_data):
        user = User.query.get(user_id)
        for key, value in new_data.items():
            setattr(user, key, value)
        db.session.commit()
    
    def check_user_login(user_name, passw):
        user = User.query.filter(User.username == user_name).one_or_none()
        password = user.password

        if user != None:
            if passw == password:
                return True
            else:
                return False
        else:
            return False


    @classmethod
    def create(cls, id_, name, email, profile_pic):
        user = cls(id_=id_, name=name, email=email, profile_pic=profile_pic)
        db.session.add(user)
        db.session.commit()
        return user

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }

    @classmethod
    def get(cls, user_id):
        return cls.query.filter_by(id=user_id).one_or_none()

class UserOAuth(db.Model,):
    id = db.Column(db.String(767), primary_key=True)
    email = db.Column(db.String(767), unique=True, nullable=False)
    name = db.Column(db.Text(), nullable=False)
    profile_pic = db.Column(db.Text(), nullable=False)


class Widget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    widget_type = db.Column(db.Enum('Twitter', 'Gmail', 'Tasks', 'Weather', 'Clock', 'Compliments'), unique=True, nullable=False)
    #ASSOCIATION
    users = db.relationship("User",
                secondary=association_table,
                back_populates="widgets"
    )
    widget_properties = db.relationship('Widget_property', lazy=True)

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
    widget_id = db.Column(db.Integer, db.ForeignKey("widget.id"))

    def __repr__(self):
        return f'<Widget_Property {self.widget_property}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "widget_property": self.widget_property,
            "property_value": self.property_value,
            "widget_id": self.widget_id
        }
    
    def get_widget_properties(id):
        widget_properties = Widget_property.query.filter_by(widget_id = id).first()
        if widget_properties == None:
            return False
        else: 
            return widget_properties.serialize()

    @classmethod
    def set_prop(cls, id, prop_data):
        new_properties = cls(
            widget_property = prop_data['widget_property'], 
            property_value = prop_data['property_value'], 
            widget_id = id
            )

        db.session.add(new_properties)
        db.session.commit()
    
    def update_props(id_widget, new_data):
        props = Widget_property.query.filter_by(widget_id = id_widget).first()
        for key, value in new_data.items():
            setattr(props, key, value)
        db.session.commit()

    def delete_props(id_widget):
        property_to_delete = Widget_property.query.filter_by(widget_id = id)
                
        property_to_delete.delete()
        db.session.commit
