from __future__ import print_function
import json
import sys

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask import make_response

# Import the database object from the main app module
from app import db

# Import module models (i.e. User)
from app.messages.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_messages = Blueprint('messages', __name__)

# Set the route and accepted methods
@mod_messages.route('/', methods=['GET', 'POST'])
def incoming_message():

    resp = make_response(render_template("index.html"), 200)

    if request.method == 'POST':
        print(request.get_json(), file = sys.stderr)

    return resp