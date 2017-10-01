#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys

from flask import Blueprint, request, render_template
from flask import make_response
from app.intent import intent_predict
from app.messages.utils import *
from app.messages.models import *
from constants import  *

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_messages = Blueprint('messages', __name__)

def get_question(concept):

    X = "subject"

    if concept.c1 != None:
        X = concept.c1
    else:
        X = get_lemma(concept.babel_id)
        concept.c1 = X

    relation_num = get_random_relation(concept.relation_check)
    question_template = get_question_template(relation_num)
    question = re.sub(r'\[X\]', X, question_template)

    return question, concept, relation_num


def question_generator(conversation):

    domain_num = conversation.domain

    max_relation_num = get_max_relation_value(domain_num, True)
    concept_count = get_concept_count(domain_num, max_relation_num, True)
    if concept_count > 0:
        concept = get_concept(domain_num, max_relation_num, True)
        question, concept, relation_num = get_question(concept)
    else:
        max_relation_num = get_max_relation_value(domain_num, False)
        # concept_count = get_concept_count(domain_num, max_relation_num, False)
        concept = get_concept(domain_num, max_relation_num, False)
        question, concept, relation_num = get_question(concept)

    conversation.question = question
    conversation.relation = relation_num
    conversation.c1 = concept.c1
    conversation.c1_id = concept.babel_id

    return question

def answer_generator(conversation):

    question = conversation.question.strip()
    question_type = question_classify(question)
    list_token_segments = get_list_token_segments(question)
    list_names = babelfy(question, "NAMED_ENTITIES")
    list_concepts = babelfy(question, "CONCEPTS")
    list_candidates = list_names + list_concepts
    list_candidates = list_candidates + pairing_elements(list_token_segments)
    list_candidates = unique_list_segment(list_candidates)

    answer = "I do not know the answer !"

    for subject_candidate in list_candidates:
        list_object_candidates = [question[i.start: i.end + 1] for i in list_candidates if not isOverlap(subject_candidate, i)]
        text = question[subject_candidate.start : subject_candidate.end + 1]
        if question_type == 1:
            # yes/no question
            answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = None, strict = True)
            for ans in answer_list:
                if ans.c2 == None: continue
                distance, c2 = pick_one(ans.c2, list_object_candidates)
                if distance <= 2:
                    return "Yes" if ans.truth else "No"

            answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = None, strict= False)
            for ans in answer_list:
                if ans.c2 == None: continue
                distance, c2 = pick_one(ans.c2, list_object_candidates)
                if distance <= 2:
                    return "Yes" if ans.truth else "No"

        else: # normal question
            answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = True,
                                                     strict=True)
            if len(answer_list) == 0:
                answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = True,
                                                     strict=False)

            if len(answer_list) != 0:
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
        domain_number = extract_domain(message_data)
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
        direction = extract_direction(message_data)
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
                question = question_generator(conversation)
                result = sendMessage(question, conversation.id)


        db.session.commit()
        return result

    if (conversation.direction == True):
        if (conversation.step == 3):
            question = extract_question(message_data)
            if question == None:
                conversation.step = 0
                result = sendMessage("Your question is not valid.\nPlease type anything to start a new session",
                                     conversation.id)
            else:
                conversation.question = question
                relation = intent_predict(question)
                print (relation)
                if relation != "_UNK":
                    conversation.relation = relation_to_num[relation.lower()]
                    answer = answer_generator(conversation)
                    result = sendMessage(answer, conversation.id)
                    conversation.step = 0
                else:
                    result = sendMessage("What is the relation of the question ?", conversation.id)
                    conversation.step += 1

            db.session.commit()
            return result

        if (conversation.step == 4):
            relation = extract_relation(message_data)
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
            answer = extract_answer(message_data)
            if answer == None:
                result = sendMessage("Don't worry ! You will can answer it next time. ", conversation.id)
            else:
                result = sendMessage("I got the answer. Thank you !", conversation.id)
                conversation.answer = answer
                update_kbs(conversation)

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
    # conversation.question = "Is Welch College placed in Nashville ?"
    # conversation.step = 4
    # conversation.direction = True
    # conversation.domain = 2
    # print(question_generator(conversation))
    # print(intent_predict(conversation.question))
    print (answer(conversation, message_data))

    if request.method == 'POST':
        print(request.get_json(), file = sys.stderr)

    return resp