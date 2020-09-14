from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import array
db = SQLAlchemy()


def compliments ():
    phrases = ["Have a great day!!", "Smile 😁, you are fantastic ", "All day's are a new beginning", "You look amazing today", "Today is gonna be great!!", "Don't forget... You are awesome!!", "You rock!!🤘", ""]
    
    for phrases, i in array-phrases.items():
        key =  i
        value = phrases
        db.session.add(key,value)
    db.session.commit()

