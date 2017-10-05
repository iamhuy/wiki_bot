# -*- encoding: utf8 -*-
import urllib2
import urllib
import json
import gzip
import random

from StringIO import StringIO
from models import *
from constants import  *
import nltk
from nltk.tag import pos_tag
import re
import requests
from app.intent import *
from app.levenshtein_distance import *

def babelfy(text, annotation_type):
    """
        Babelfy a sentence into list of disambiguated records.
    :param text: a sentence
    :param annotation_type: one of 3 type CONCEPT, NAME ENTITIES, or ALL
    :return: A list of babelnet Record
    """
    service_url = 'https://babelfy.io/v1/disambiguate'

    lang = 'EN'
    key  = BABELNET_KEY

    params = {
        'text' : text,
        'lang' : lang,
        'key'  : key,
        'annType': annotation_type
    }

    url = service_url + '?' + urllib.urlencode(params)
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)

    list_fragment = []

    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = json.loads(f.read())
        for result in data:
            list_fragment.append(Segment.serialize(result))

    return list_fragment


def get_main_lemma(id):
    """
        Get the first lemma representation of a BabelNet ID
    :param id: babelnet ID
    :return: A string which is lemma of id
    """

    service_url = 'https://babelnet.io/v4/getSynset'

    key = BABELNET_KEY

    params = {
        'id': id,
        'key': key
    }
    try:
        url = service_url + '?' + urllib.urlencode(params)
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)

        simple_lemma = "None"

        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = json.loads(f.read())
            result = data['senses'][0]
            simple_lemma = result.get('simpleLemma')
            simple_lemma = re.sub(r'_', ' ', simple_lemma)  .strip()

    except Exception, e:
        print('Error:', str(e))
        return None

    return simple_lemma


def update_centralized_kbs(conversation):
    """
        Update a new record to online KBS
    :param conversation: record which contain information about conversation
    :return: None
    """
    try:
        service_url = 'http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/add_item_test'

        key = KBS_KEY
        params = {
            'key': key
        }

        data = {}
        data['question'] = conversation.question
        data['answer'] = conversation.answer
        data['relation'] = list_relations[conversation.relation].upper()
        data['context'] = ""
        data['domains'] = [list_domains[conversation.domain]]
        data['c1'] = conversation.c1 + ("" if conversation.c1_id == None else "::" + conversation.c1_id)
        data['c2'] = conversation.answer

        url = service_url + '?' + urllib.urlencode(params)
        request = urllib2.Request(url)
        request.add_data(json.dumps(data))
        urllib2.urlopen(request)

    except Exception, e:
        print('Error:', str(e))
        return None


def extract_answer(message_data):
    try:
        answer = message_data['message']['text'].lower()
        return answer if answer != "no" else None
    except Exception, e:
        print('Error:', str(e))
        return None


def extract_domain(message_data):
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


def extract_relation(message_data):
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


def extract_direction(message_data):
    try:
        direction = message_data['message']['text'].lower().strip()
        if (direction != "yes" and direction != "no"):
            print('Error: Invalid answer')
            return None
        return True if direction == "yes" else False
    except Exception, e:
        print('Error:', str(e))
        return None


def extract_question(message_data):
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


def create_conversation(chat_id, user_name):
    """
        Create a new conversation record in database
    :param chat_id: id of conversation
    :param user_name: name of sender
    :return: conversation object
    """
    try:
        new_chat = Chat(chat_id, user_name)
        db.session.add(new_chat)
        db.session.commit()
    except Exception, e:
        print('Error:', str(e))
        return None

    return new_chat

def sendMessage(text, chat_id):
    """
        Send a message to a conversation by Telegram API
    :param text: content of the message
    :param chat_id: id of conversation
    :return: Boolean indicates if sending  was successful
    """
    try:
        url = 'https://api.telegram.org/{telegram_key}/sendMessage?chat_id={chat_id}&text={text}'
        response = requests.post(url.format(chat_id=chat_id, text=text, telegram_key = TELEGRAM_KEY)).json()
    except Exception, e:
        print('Error:', str(e))
        return None

    return True if response['ok'] == True else False


def question_classify(question):
    """
        Classify a question into 3 types:
            1: Yes/no question
            2: Normal question
            3: Not a question
    :param question:
    :return:
    """
    try:
        if re.match('(is|are|was|were|have|has|had|do|does|did|will|shall|would)\s', question.strip().lower(),
                    re.IGNORECASE) != None:
            return 1
        if re.match('(what|where|how|when|which|whom|why|who)\s', question.strip().lower(), re.IGNORECASE) != None:
            return 2
    except Exception, e:
        print('Error:', str(e))
        return None

    return 0


def segment_cmp(s1, s2):
    """
            Check if two segments identical
        :param s1: Segment #1
        :param s2: Segment #2
        :return: True if 2 segments identical, otherwise False
        """
    if (s1.start < s2.start or (s1.start == s2.start and s1.end > s2.end)):
        return -1
    if s1.start == s2.start and s1.end == s2.end:
        return 0
    return 1


def isOverlap(s1, s2):
    """
        Check if two segments overlappe
    :param s1: Segment #1
    :param s2: Segment #2
    :return: True if 2 segments overlappe, otherwise False
    """
    if (s1.start >= s2.end or s2.start >= s1.end):
        return False
    return True


def pairing_elements(list_segments):
    """
        Make new segments from orignal segments
    :param list_segments: list of single token segments
    :return: New list of Segments with variable length
    """
    try:
        list_segments = sorted(list_segments, cmp=segment_cmp)
        n = len(list_segments)
        pairing_lists = []
        for k in reversed(range(1, n)):
            for i in range(0, n - k):
                j = i + k
                if not isOverlap(list_segments[i], list_segments[j]):
                    start = list_segments[i].start
                    end = list_segments[j].end
                    pairing_lists.append(Segment(start, end))

        pairing_lists = pairing_lists + list_segments

    except Exception, e:
        print('Error:', str(e))
        return None

    return pairing_lists


def unique_list_segment(list_segments):
    new_list = []
    span_set = []
    for segment in list_segments:
        start = segment.start
        end = segment.end
        if (start, end) not in span_set:
            new_list.append(segment)
            span_set.append((start, end))

    return new_list


def get_list_token_segments(sentence):
    """
        Retrieve a list of single tokent segments from a sentence
    :param sentence: A string represent sentence
    :return: A list of segments
    """
    try:
        list_segments = []
        tokens = nltk.word_tokenize(sentence)
        posTagged = pos_tag(tokens, tagset='universal')
        ix = 0
        for tag in posTagged:
            ix = sentence.find(tag[0], ix)
            end = ix + len(tag[0])
            if ix != 0 and tag[1] in ('NOUN', 'NUM', 'VERB', 'ADJ', 'PRON','ADV', 'X', 'DET'):
                list_segments.append(Segment(ix, end - 1, None, tag[0]))
            ix = end

    except Exception, e:
        print('Error:', str(e))
        return None

    return list_segments


def get_random_relation(relation_check):
    res = []
    for index in range(len(relation_check)):
        if relation_check[index] == '1':
            res.append(index)

    return random.choice(res)


def get_question_template(relation_num):
    return random.choice(question_templates[relation_num])


def list_domain_encode(list_domains):
    """
        Encode a list of domains to a string, each character conrresponds to a domain :
            1 if belongs to that domain
            0 if not belongs to that domain
    :param list_domains: list of domains
    :return: Encoding string
    """
    try:
        encode = "0000000000000000000000000000000000"
        for i in list_domains:
            if i == '' or i == '[]':
                continue
            encode = encode[:domain_to_num[i.strip().lower()]] + '1' + encode[domain_to_num[i.strip().lower()] + 1 : ]

    except Exception, e:
        print('Error:', str(e))
        return None

    return encode


def list_domain_decode(s):
    try:
        domains = []
        for i in range(len(s)):
            if s[i] =='1':
                domains.append(list_domains[i])

    except Exception, e:
        print('Error:', str(e))
        return None

    return domains


def list_domain_num_encode(list_domains_num):
    try:
        encode = "0000000000000000000000000000000000"
        for i in list_domains_num:
            encode = encode[:i] + '1' + encode[i+1:]

    except Exception, e:
        print('Error:', str(e))
        return None

    return encode


def update_kbs(conversation):
    """
        Update local and online KBS from a conversation
    :param conversation: a conversation object
    :return: None
    """
    try:
        new_record = KBS(c1=conversation.c1,
                         c1_id=conversation.c1_id,
                         c2=conversation.answer,
                         c2_id=None,
                         relation=list_relations[conversation.relation].upper(),
                         relation_num=conversation.relation,
                         domains=list_domain_num_encode([conversation.domain]),
                         truth=True)
        db.session.add(new_record)
        update_centralized_kbs(conversation)

    except Exception, e:
        print('Error:', str(e))
        return None


def update_concept(conversation):
    """
        Update a concept in database
    :param conversation: conversation object
    :return: None
    """
    try:
        concept = Concept.query.get(conversation.concept_id)
        concept.relation_count -= 1
        relation_num = conversation.relation
        concept.relation_check = concept.relation_check[:relation_num] + '2' + concept.relation_check[relation_num + 1:]

    except Exception, e:
        print('Error:', str(e))
        return None


def get_question(concept):
    """
        Get a question from templates for a concept
    :param concept: concept as a string
    :return: A string represents string
    """

    try:
        X = "subject"

        if concept.c1 != None:
            X = concept.c1
        else:
            X = get_main_lemma(concept.babel_id)
            concept.c1 = X

        relation_num = get_random_relation(concept.relation_check)
        question_template = get_question_template(relation_num)
        question = re.sub(r'\[X\]', X, question_template)

    except Exception, e:
        print('Error:', str(e))
        return None

    return question, concept, relation_num


def question_generator(conversation):
    """
        Generate a question from a conversation object
    :param conversation: conversation object
    :return: A string represents the question
    """

    try:
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
        conversation.concept_id = concept.id

    except Exception, e:
        print('Error:', str(e))
        return None

    return question


def answer_generator(conversation):
    """
        Generate an answer for a question
    :param conversation: conversation object
    :return: A string represents the answer
    """

    try:
        question = conversation.question.strip()
        question_type = question_classify(question)
        list_token_segments = get_list_token_segments(question)
        # list_names = babelfy(question, "NAMED_ENTITIES")
        # list_concepts = babelfy(question, "CONCEPTS")
        # list_candidates = list_names + list_concepts
        # list_candidates = list_candidates + pairing_elements(list_token_segments)
        list_candidates = pairing_elements(list_token_segments)
        list_candidates = unique_list_segment(list_candidates)

        answer = "I do not know the answer !"

        for subject_candidate in list_candidates:
            list_object_candidates = [question[i.start: i.end + 1] for i in list_candidates if not isOverlap(subject_candidate, i)]
            text = question[subject_candidate.start : subject_candidate.end + 1]
            if question_type == 1:
                # yes/no question
                if len(list_object_candidates) == 0: continue

                # check for strict strategy first
                answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = None, strict = True)
                for ans in answer_list:
                    if ans.c2 == None : continue
                    # choose best match from object candidates
                    distance, c2 = pick_one(ans.c2, list_object_candidates)
                    if distance <= 2:
                        return "Yes" if ans.truth else "No"

                # if not, more reflexible way is used to query
                answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = None, strict= False)
                for ans in answer_list:
                    if ans.c2 == None : continue
                    # choose best match from object candidates
                    distance, c2 = pick_one(ans.c2, list_object_candidates)
                    if distance <= 2:
                        return "Yes" if ans.truth else "No"

            else: # normal question
                # check for strict strategy first
                answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = True,
                                                         strict=True)
                # if not, more reflexible way is used to query
                if len(answer_list) == 0:
                    answer_list = get_kbs_by_relation_and_c1(conversation.relation, text, subject_candidate.babelId, truth = True,
                                                         strict=False)

                if len(answer_list) != 0:
                    return answer_list[0].c2

    except Exception, e:
        print('Error:', str(e))
        return None

    return answer


def answer(conversation, message_data):
    """
        Handle the flow of conversations
    :param conversation: conversation object
    :param message_data: json object of message from Telegram
    :return: True if message sent successfully, otherwise False
    """

    try:
        result = False

        # Ask about domain
        if (conversation.step == 0):
            result = sendMessage(random.choice(WELCOME_REPONSES), conversation.id)
            conversation.step += 1
            db.session.commit()
            return result


        #Ask about direction
        if (conversation.step == 1):
            domain_number = extract_domain(message_data)
            if (domain_number == None):
                conversation.step = 0
                sendMessage(INVALID_ANSWER('domain'), conversation.id)
            else:
                conversation.domain = domain_number
                conversation.step += 1
                result = sendMessage(random.choice(DIRECTION_RESPONSES), conversation.id)
            db.session.commit()
            return result


        # Ask a question or receive a question
        if (conversation.step == 2):
            direction = extract_direction(message_data)
            if (direction == None):
                conversation.step = 0
                conversation.direction = None
                result = sendMessage(INVALID_ANSWER('answer'), conversation.id)
            else:
                conversation.direction = direction
                conversation.step += 1
                if (direction):
                    result = sendMessage(random.choice(QUERYING_RESONSES), conversation.id)
                else:
                    question = question_generator(conversation)
                    result = sendMessage(question, conversation.id)

            db.session.commit()
            return result


        # Querying phase
        if (conversation.direction == True):
            if (conversation.step == 3):
                question = extract_question(message_data)
                if question == None:
                    conversation.step = 0
                    result = sendMessage(INVALID_ANSWER('question'),conversation.id)
                else:
                    conversation.question = question
                    relation = intent_predict(question)
                    if relation != "_UNK":
                        conversation.relation = relation_to_num[relation.lower()]
                        answer = answer_generator(conversation)
                        print(answer)
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
                    result = sendMessage(INVALID_ANSWER('relation'),conversation.id)
                else:
                    conversation.relation = relation
                    answer = answer_generator(conversation)
                    result = sendMessage(answer, conversation.id)

                conversation.step = 0
                db.session.commit()
                return result



        # Enriching Phase
        if (conversation.direction == False):
            if (conversation.step == 3):
                answer = extract_answer(message_data)
                if answer == None:
                    result = sendMessage(random.choice(UNSUCCESSFUL_ENRICH_RESPONSES), conversation.id)
                else:
                    result = sendMessage(random.choice(SUCCESSFUL_ENRICH_RESPONSES), conversation.id)
                    conversation.answer = answer
                    update_kbs(conversation)
                    update_concept(conversation)

                conversation.step = 0
                db.session.commit()
                return result

        return False


    except Exception, e:
        print('Error:', str(e))
        return None


