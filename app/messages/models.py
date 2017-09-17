# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)

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

class KBS(Base):
    __tablename__ = 'kbs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c1 = db.Column(db.String)
    c1_id = db.Column(db.String)
    c2 = db.Column(db.String)
    c2_id = db.Column(db.String)
    relation = db.Column(db.String, nullable=False)
    relation_num = db.Column(db.Integer, nullable=False)
    domains = db.Column(db.String, nullable=False)

    def __repr__(self):
        return self.c2

def get_kbs_by_relation_and_c1(relation, c1, c1_id):
    query = KBS.query.filter(db.and_(KBS.relation_num == relation))
    if c1_id != None:
        query = query.filter(KBS.c1_id == c1_id)
    if c1 != None:
        query = query.filter(db.func.lower(KBS.c1) == db.func.lower(c1))

    return query.all()