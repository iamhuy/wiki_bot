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

def extractDomain(message_data):
    try:
        text = message_data['message']['text']
        domain_number = int(text)
        if (domain_number < 0 or domain_number > 33):
            print('Error: Invalid domain number')
            return None
        return domain_number
    except Exception, e:
        print('Error:', str(e))
        return None

def extractRelation(message_data):
    try:
        text = message_data['message']['text']
        relation_number = int(text)
        if (relation_number < 0 or relation_number > 16):
            print('Error: Invalid Relation number')
            return None
        return relation_number
    except Exception, e:
        print('Error:', str(e))
        return None

def extractDirection(message_data):
    try:
        direction = message_data['message']['text'].lower()
        if (direction != "yes" and direction != "no"):
            print('Error: Invalid answer')
            return None
        return True if direction == "yes" else False
    except Exception, e:
        print('Error:', str(e))
        return None

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
        domain_number = extractDomain(message_data)
        if (domain_number == None):
            conversation.step = 0
            sendMessage("Your domain number is not valid.\nPlease type anything to start a new session", conversation.id)
        else:
            conversation.domain = domain_number
            conversation.step += 1
            result = sendMessage("Do you want to ask a question ?", conversation.id)
        db.session.commit()
        return result

    # Querying

    if (conversation.step == 2):
        direction = extractDirection(message_data)
        if (direction == None):
            conversation.step = 0
            conversation.direction = None
            result = sendMessage("Your answer is not valid.\nPlease type anything to start a new session", conversation.id)
        else:
            conversation.direction = direction
            conversation.step += 1
            if (direction):
                result = sendMessage("Ask me a question !",conversation.id)
            else:
                questionGenerator = "This is your question"
                result = sendMessage(questionGenerator, conversation.id)


        db.session.commit()
        return result

    if (conversation.direction == True):

        if (conversation.step == 3):
            result = sendMessage("What is the relation of the question ?", conversation.id)
            conversation.step += 1
            db.session.commit()
            return result

        if (conversation.step == 4):
            relation = extractRelation(message_data)

            if (relation == None):
                conversation.step = 0
                result = sendMessage("Your relation number is not valid.\nPlease type anything to start a new session",
                            conversation.id)
            else:
                conversation.relation = relation
                conversation.step += 1
                answerGenerator = "This is the answer!"
                result = sendMessage(answerGenerator, conversation.id)

            db.session.commit()
            return result

    if (conversation.direction == False):
        if (conversation.step == 3):
            result = sendMessage("I got the answer and will update the knowledge base", conversation.id)
            conversation.step = 0
            db.session.commit()
            return result

    return False


# Set the route and accepted methods
@mod_messages.route('/messages', methods=['GET', 'POST'])
def incoming_message():
    resp = make_response(render_template("index.html"), 200)

    if (request.method == 'GET'):
        return resp

    message_data = request.get_json()

    # print(message_data, file = sys.stderr)
    chat_id = int(message_data['message']['chat']['id'])
    user_id = int(message_data['message']['from']['id'])
    user_name = message_data['message']['from']['first_name']
    # print(chat_id)



    conversation = Chat.query.get(chat_id)

    if (conversation == None):
        conversation = create_conversation(chat_id, user_name)

    print (answer(conversation, message_data))

    if request.method == 'POST':
        print(request.get_json(), file = sys.stderr)

    return resp