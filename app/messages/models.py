# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

# Define a User model
class Chat(Base):

    __tablename__ = 'chat'

    # User Name
    user_name    = db.Column(db.String(128),  nullable=False)
    domain = db.Column(db.Integer)
    direction = db.Column(db.Boolean)
    question = db.Column(db.String(1000))
    relation = db.Column(db.Integer)
    step = db.Column(db.Integer)

    # New instance instantiation procedure
    def __init__(self, id, user_name):
        self.id = id
        self.user_name = user_name
        self.step = 0

    def __repr__(self):
        return '<User %r>' % (self.name)