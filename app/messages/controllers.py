from __future__ import print_function
import json
import sys
import requests
import re

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask import make_response

# Import the database object from the main app module
from app import db

# Import module models (i.e. User)
from app.messages.models import Chat

from app.utils.messages import babelfy

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

def question_classify(question):
    if re.match('(is|are|was|were|have|has|had|do|does|did|will|shall|would)\s', question, re.IGNORECASE) != None:
        return 1
    if re.match('(what|where|how|when|which|whom|why)\s', question, re.IGNORECASE) != None:
        return 2
    return 0

def segment_cmp(s1, s2):
    left1 = s1['charFragment']['start']
    left2 = s2['charFragment']['start']
    right1 = s1['charFragment']['end']
    right2 = s2['charFragment']['end']

    if (left1 < left2 or (left1 == left2 and right1 > right2)):
        return -1
    if left1 == left2 and right1 == right2:
        return 0
    return 1

def isOverlap(s1, s2):
    left1 = s1['charFragment']['start']
    left2 = s2['charFragment']['start']
    right1 = s1['charFragment']['end']
    right2 = s2['charFragment']['end']
    if (left1 < left2 < right1 or left1 < right2 < right1):
        return True
    return False

def new_segment(start, end):
    segment = {}
    segment['charFragment'] = {}
    segment['charFragment']['start'] = start
    segment['charFragment']['end'] = end
    segment['babelSynsetID'] = None
    return segment

def getText(text, segment):
    start = segment['charFragment']['start']
    end = segment['charFragment']['end']
    return text[start:end+1]

def pairing_elements(list_segments):
    list_segments = sorted(list_segments, cmp=segment_cmp)
    n = len(list_segments)
    pairing_lists = []
    # print(n)
    for k in reversed(range(1,n)):
        for i in range(0,n-k):
            j = i + k
            # print(i, '     ', j)
            if not isOverlap(list_segments[i], list_segments[j]):
                start = list_segments[i]['charFragment']['start']
                end = list_segments[j]['charFragment']['end']
                pairing_lists.append(new_segment(start, end))
    return pairing_lists

def unique_list_segment(list_segments):
    new_list = []
    span_set = []
    for segment in list_segments:
        start = segment['charFragment']['start']
        end = segment['charFragment']['end']
        if (start, end) not in span_set:
            new_list.append(segment)
            span_set.append((start,end))

    return new_list


def answer_generator(conversation, message_data):
    answer = "I do not know the answer !"
    try:
        question = message_data['message']['text']
    except Exception, e:
        print('Error:', str(e))
        return None

    question = question.strip()
    list_names = babelfy(question, "NAMED_ENTITIES")


    list_concepts = babelfy(question, "CONCEPTS")


    list_mixed = babelfy(question, "ALL")



    if question_classify(question) == 2:
        list_names
    else:



    return answer

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
                conversation.step = 0

                answer_generator()
                answer = "This is the answer!"
                result = sendMessage(answer, conversation.id)

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
    list_segments = babelfy('BabelNet is both a multilingual encyclopedic dictionary and a semantic network', "ALL")


    if (request.method == 'GET'):
        return resp

    message_data = request.get_json()
    
    # print(message_data, file = sys.stderr)
    chat_id = int(message_data['message']['chat']['id'])
    user_id = int(message_data['message']['from']['id'])
    user_name = message_data['message']['from']['first_name']
    text = message_data['message']['text']

    conversation = Chat.query.get(chat_id)

    if (conversation == None):
        conversation = create_conversation(chat_id, user_name)

    print (answer(conversation, message_data))

    if request.method == 'POST':
        print(request.get_json(), file = sys.stderr)

    return resp