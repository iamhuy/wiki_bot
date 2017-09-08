from __future__ import print_function
import json
import sys
import requests
import random

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask import make_response

# Import the database object from the main app module
from app import db

# Import module models (i.e. User)
from app.messages.models import Chat

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_messages = Blueprint('messages', __name__)
def create_conversation(chat_id, user_name):
    new_chat = Chat(chat_id, user_name)
    db.session.add(new_chat)
    db.session.commit()
    return new_chat

def sendMessage(text, chat_id):
    url = 'https://api.telegram.org/bot382360568:AAGn2SWgtTdpafWd-g_dvVkIvZZeAOomB4w/sendMessage?chat_id={chat_id}&text={text}'
    response = requests.post(url.format(chat_id = chat_id, text = text)).json()
    return True if response['ok'] == True else False

def answer(conversation, message_data):

    result = False

    if (conversation.step == 0):
        result = sendMessage("Hey, what do you want to talk about ?", conversation.id)
        conversation.step += 1
        db.session.commit()
        return result


    if (conversation.step == 1):
        result = sendMessage("Do you want to ask a question ?", conversation.id)
        conversation.step += 1
        conversation.direction = True if random.randint(1,10) == 0 else False
        db.session.commit()
        return result

    # Querying
    if (conversation.direction == True):
        if (conversation.step == 2):
            result = sendMessage("Let's ask", conversation.id)
            conversation.step += 1
            db.session.commit()
            return result

        if (conversation.step == 3):
            result = sendMessage("What is the relation of the question ?", conversation.id)
            conversation.step += 1
            db.session.commit()
            return result

        if (conversation.step == 4):
            result = sendMessage("This is the answer ! ", conversation.id)
            conversation.step = 0
            db.session.commit()
            return result

    if (conversation.direction == False):
        if (conversation.step == 2):
            result = sendMessage("This the question for you", conversation.id)
            conversation.step += 1
            db.session.commit()
            return result

        if (conversation.step == 3):
            result = sendMessage("I got the answer and will update the knowledge base", conversation.id)
            conversation.step = 0
            db.session.commit()
            return result

    return False


# Set the route and accepted methods
@mod_messages.route('/messages', methods=['GET', 'POST'])
def incoming_message():

    message_data = request.get_json()

    # print(message_data, file = sys.stderr)
    chat_id = int(message_data['message']['chat']['id'])
    user_id = int(message_data['message']['from']['id'])
    user_name = message_data['message']['from']['first_name']
    # print(chat_id)

    resp = make_response(render_template("index.html"), 200)

    conversation = Chat.query.get(chat_id)

    if (conversation == None):
        conversation = create_conversation(chat_id, user_name)

    print (answer(conversation, message_data))

    # if request.method == 'POST':
    #     print(request.get_json(), file = sys.stderr)

    return resp