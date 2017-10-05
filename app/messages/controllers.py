#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys

from flask import Blueprint, request, render_template
from flask import make_response
from app.messages.utils import *

mod_messages = Blueprint('messages', __name__)

# Set the route and accepted methods
@mod_messages.route('/messages', methods=['GET', 'POST'])
def incoming_message():
    resp = make_response(render_template("index.html"), 200)

    if (request.method == 'GET'):
        return resp

    if request.method == 'POST':
        print(request.get_json(), file = sys.stderr)

    message_data = request.get_json()
    chat_id = int(message_data['message']['chat']['id'])
    user_name = message_data['message']['from']['first_name']

    # check if a user has been stored in the database or not
    conversation = Chat.query.get(chat_id)

    # if not create a new conversation
    if (conversation == None):
        conversation = create_conversation(chat_id, user_name)

    answer(conversation, message_data)

    return resp