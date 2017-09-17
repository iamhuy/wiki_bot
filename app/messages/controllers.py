#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import sys

import requests
from flask import Blueprint, request, render_template
from flask import make_response

from app import db
from app.messages.utils import *
from app.messages.models import *
from constants import  *


# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_messages = Blueprint('messages', __name__)

def create_conversation(chat_id, user_name):
    new_chat = Chat(chat_id, user_name)
    db.session.add(new_chat)
    db.session.commit()
    return new_chat

def extractDomain(message_data):
    try:
        domain = message_data['message']['text'].strip().lower()
        distance, domain = pick_one(domain, list_domains)
        if (distance > 2):
            print('Error: Invalid domain')
            return None
        return domain_to_num[domain]
    except Exception, e:
        print('Error:', str(e))
        return None

def extractRelation(message_data):
    try:
        relation = message_data['message']['text'].strip().lower()
        distance, relation = pick_one(relation, list_relations)
        if (distance > 2):
            print('Error: Invalid Relation')
            return None
        return relation_to_num[relation]
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

def extractQuestion(message_data):
    try:
        question = message_data['message']['text'].strip()
        t = question_classify(question)
        if t == 0:
            print('Error: Invalid question')
            return None
        return question
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
    if re.match('(what|where|how|when|which|whom|why|who)\s', question, re.IGNORECASE) != None:
        return 2
    return 0

def segment_cmp(s1, s2):

    if (s1.start < s2.start or (s1.start == s2.start and s1.end > s2.end)):
        return -1
    if s1.start == s2.start and s1.end == s2.end:
        return 0
    return 1

def isOverlap(s1, s2):
    if (s1.start < s2.start < s1.end or s1.start < s2.end < s1.end):
        return True
    return False


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
                start = list_segments[i].start
                end = list_segments[j].end
                pairing_lists.append(Segment(start,end))
    return pairing_lists

def unique_list_segment(list_segments):
    new_list = []
    span_set = []
    for segment in list_segments:
        start = segment.start
        end = segment.end
        if (start, end) not in span_set:
            new_list.append(segment)
            span_set.append((start,end))

    return new_list

def answer_generator(conversation):

    question = conversation.question.strip()
    list_names = babelfy(question, "ALL")
    list_names = list_names + pairing_elements(list_names)
    list_names = unique_list_segment(list_names)
    question_type = question_classify(question)

    if question_type == 1:
        answer = "No"
    else:
        answer = "I do not know the answer !"

    for subject_candidate in list_names:
        text = question[subject_candidate.start : subject_candidate.end + 1]
        answer_list =  get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId)
        if len(answer_list) != 0:
            # yes/no question
            if question_type == 1:
                for answer in answer_list:
                    print(answer.c2)
                    distance, (start, end) = substring_match(answer.c2, question)
                    if distance <= 2:
                        if not isOverlap(subject_candidate, Segment(start, end)):
                            return "Yes"

            else: # normal question
                return answer_list[0].c2

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
            sendMessage("Your domain is not valid.\nPlease type anything to start a new session", conversation.id)
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
            question = extractQuestion(message_data)
            if question == None:
                conversation.step = 0
                result = sendMessage("Your question is not valid.\nPlease type anything to start a new session",
                                     conversation.id)
            else:
                conversation.question = question
                result = sendMessage("What is the relation of the question ?", conversation.id)
                conversation.step += 1

            db.session.commit()
            return result

        if (conversation.step == 4):
            relation = extractRelation(message_data)
            if (relation == None):
                result = sendMessage("Your relation is not valid.\nPlease type anything to start a new session",
                            conversation.id)
            else:
                conversation.relation = relation
                answer = answer_generator(conversation)
                result = sendMessage(answer, conversation.id)

            conversation.step = 0
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
    chat_id = int(message_data['message']['chat']['id'])
    user_name = message_data['message']['from']['first_name']
    conversation = Chat.query.get(chat_id)

    if (conversation == None):
        conversation = create_conversation(chat_id, user_name)
    # conversation.question = "Is Gladsaxehus an example of ruined castle ?"
    # conversation.step = 4
    # conversation.direction = True
    # conversation.domain = 1

    print (answer(conversation, message_data))

    if request.method == 'POST':
        print(request.get_json(), file = sys.stderr)

    return resp