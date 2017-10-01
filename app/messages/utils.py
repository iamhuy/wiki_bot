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
from nltk.tag import pos_tag, map_tag
import re
import requests

def babelfy(text, annotation_type):
    service_url = 'https://babelfy.io/v1/disambiguate'

    lang = 'EN'
    key  = '61dc9d2b-8bf8-434e-b3ec-08f32e523959'

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

        # retrieving data
        for result in data:
                    # retrieving token fragment
                    # new_tuple = {}
                    # charFragment = result.get('charFragment')
                    # new_tuple['start'] = charFragment.get('start')
                    # new_tuple['end'] = charFragment.get('end')
                    # new_tuple['id'] = result.get('babelSynsetID')
                    # new_tuple['score'] = result.get('score')
                    # new_tuple['text'] = text[charFragment.get('start') : charFragment.get('end') + 1]
                    list_fragment.append(Segment.serialize(result))

    return list_fragment


def get_lemma(id):

    service_url = 'https://babelnet.io/v4/getSynset'

    key = '61dc9d2b-8bf8-434e-b3ec-08f32e523959'

    params = {
        'id': id,
        'key': key
    }

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

    return simple_lemma

def update_centralized_kbs(conversation):

    service_url = 'http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/add_item_test'

    key = '61dc9d2b-8bf8-434e-b3ec-08f32e523959'

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


def dl_distance(s1, s2, substitutions=[], deletions = [], insertions =[],  symetric=True,
                returnMatrix=False, printMatrix=False, nonMatchingEnds=False, transposition=True,
                secondHalfDiscount=False):
    """
    Return DL distance between s1 and s2. Default cost of substitution, insertion, deletion and transposition is 1
    substitutions is list of tuples of characters (what, substituted by what, cost),
        maximal value of substitution is 2 (ie: cost deletion & insertion that would be otherwise used)
        eg: substitutions=[('a','e',0.4),('i','y',0.3)]
    symetric=True mean that cost of substituting A with B is same as B with A
    returnMatrix=True: the matrix of distances will be returned, if returnMatrix==False, then only distance will be returned
    printMatrix==True: matrix of distances will be printed
    transposition=True (default): cost of transposition is 1. transposition=False: cost of transpositin is Infinity
    """
    if not isinstance(s1, unicode):
        s1 = unicode(s1, "utf8")
    if not isinstance(s2, unicode):
        s2 = unicode(s2, "utf8")

    from collections import defaultdict
    dels = defaultdict(lambda: 1)
    ins = defaultdict(lambda : 1)
    subs = defaultdict(lambda: 1)  # default cost of substitution is 1
    for a, b, v in substitutions:
        subs[(a, b)] = v
        if symetric:
            subs[(b, a)] = v
    for a, v in deletions:
        dels[a] = v
    for a, v in insertions:
        ins[a] = v

    if nonMatchingEnds:
        matrix = [[j for j in range(len(s2) + 1)] for i in range(len(s1) + 1)]
    else:  # start and end are aligned
        matrix = [[i + j for j in range(len(s2) + 1)] for i in range(len(s1) + 1)]
    # matrix |s1|+1 x |s2|+1 big. Only values at border matter
    half1 = len(s1) / 2
    half2 = len(s2) / 2
    for i in range(len(s1)):
        for j in range(len(s2)):
            ch1, ch2 = s1[i], s2[j]
            if ch1 == ch2:
                cost = 0
            else:
                cost = subs[(ch1, ch2)]
            if secondHalfDiscount and (s1 > half1 or s2 > half2):
                deletionCost, insertionCost = 0.6, 0.6
            else:
                deletionCost, insertionCost = 1, 1

            deletionCost = dels[ch1]
            insertionCost = ins[ch2]
            matrix[i + 1][j + 1] = min([matrix[i][j + 1] + deletionCost,  # deletion
                                        matrix[i + 1][j] + insertionCost,  # insertion
                                        matrix[i][j] + cost  # substitution or no change
                                        ])

            if transposition and i >= 1 and j >= 1 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                matrix[i + 1][j + 1] = min([matrix[i + 1][j + 1],
                                            matrix[i - 1][j - 1] + cost])

    if printMatrix:
        print "     ",
        for i in s2:
            print i, "",
        print
        for i, r in enumerate(matrix):
            if i == 0:
                print " ", r
            else:
                print s1[i - 1], r
    if returnMatrix:
        return matrix
    else:
        return matrix[-1][-1]


def dl_ratio(s1, s2, **kw):
    'returns distance between s1&s2 as number between [0..1] where 1 is total match and 0 is no match'
    try:
        return 1 - (dl_distance(s1, s2, **kw)) / (2.0 * max(len(s1), len(s2)))
    except ZeroDivisionError:
        return 0.0


def match_list(s, l, **kw):
    '''
    returns list of elements of l with each element having assigned distance from s
    '''
    return map(lambda x: (dl_distance(s, x, **kw), x), l)


def pick_N(s, l, num=3, **kw):
    ''' picks top N strings from options best matching with s
        - if num is set then returns top num results instead of default three
    '''
    return sorted(match_list(s, l, **kw))[:num]


def pick_one(s, l, **kw):
    try:
        return pick_N(s, l, 1, **kw)[0]
    except IndexError:
        return None


def substring_match(text, s, transposition=True, **kw):  # TODO: isn't backtracking too greedy?
    """
    fuzzy substring searching for text in s
    """
    for k in ("nonMatchingEnds", "returnMatrix"):
        if kw.has_key(k):
            del kw[k]

    matrix = dl_distance(s, text, returnMatrix=True, nonMatchingEnds=True, **kw)

    minimum = float('inf')
    minimumI = 0
    for i, row in enumerate(matrix):
        if row[-1] < minimum:
            minimum = row[-1]
            minimumI = i

    x = len(matrix[0]) - 1
    y = minimumI

    # backtrack:
    while x > 0:
        locmin = min(matrix[y][x - 1],
                     matrix[y - 1][x - 1],
                     matrix[y - 1][x])
        if matrix[y - 1][x - 1] == locmin:
            y, x = y - 1, x - 1
        elif matrix[y - 1][x] == locmin:
            y = y - 1
        elif matrix[y][x - 1] == locmin:
            x = x - 1

    return minimum, (y, minimumI)


def substring_score(s, text, **kw):
    return substring_match(s, text, **kw)[0]


def substring_position(s, text, **kw):
    return substring_match(s, text, **kw)[1]


def substring_search(s, text, **kw):
    score, (start, end) = substring_match(s, text, **kw)
    # print score, (start, end)
    return text[start:end]


def match_substrings(s, l, score=False, **kw):
    'returns list of elements of l with each element having assigned distance from s'
    return map(lambda x: (substring_score(x, s, **kw), x), l)


def pick_N_substrings(s, l, num=3, **kw):
    ''' picks top N substrings from options best matching with s
        - if num is set then returns top num results instead of default three
    '''
    return sorted(match_substrings(s, l, **kw))[:num]

def pick_one_substring(s, l, **kw):
    try:
        return pick_N_substrings(s, l, 1, **kw)[0]
    except IndexError:
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
        direction = message_data['message']['text'].lower()
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
    new_chat = Chat(chat_id, user_name)
    db.session.add(new_chat)
    db.session.commit()
    return new_chat

def sendMessage(text, chat_id):
    url = 'https://api.telegram.org/bot382360568:AAGn2SWgtTdpafWd-g_dvVkIvZZeAOomB4w/sendMessage?chat_id={chat_id}&text={text}'
    response = requests.post(url.format(chat_id=chat_id, text=text)).json()
    return True if response['ok'] == True else False

def question_classify(question):
    if re.match('(is|are|was|were|have|has|had|do|does|did|will|shall|would)\s', question.strip().lower(),
                re.IGNORECASE) != None:
        return 1
    if re.match('(what|where|how|when|which|whom|why|who)\s', question.strip().lower(), re.IGNORECASE) != None:
        return 2
    return 0

def segment_cmp(s1, s2):

    if (s1.start < s2.start or (s1.start == s2.start and s1.end > s2.end)):
        return -1
    if s1.start == s2.start and s1.end == s2.end:
        return 0
    return 1

def isOverlap(s1, s2):
    if (s1.start >= s2.end or s2.start >= s1.end):
        return False
    return True

def pairing_elements(list_segments):
    list_segments = sorted(list_segments, cmp=segment_cmp)
    n = len(list_segments)
    pairing_lists = []
    # print(n)
    for k in reversed(range(1, n)):
        for i in range(0, n - k):
            j = i + k
            # print(i, '     ', j)
            if not isOverlap(list_segments[i], list_segments[j]):
                start = list_segments[i].start
                end = list_segments[j].end
                pairing_lists.append(Segment(start, end))
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
    list_segments = []
    tokens = nltk.word_tokenize(sentence)
    posTagged = pos_tag(tokens, tagset='universal')
    ix = 0
    for tag in posTagged:
        ix = sentence.find(tag[0], ix)
        end = ix + len(tag[0])
        if ix != 0 and tag[1] in ('NOUN', 'NUM', 'PRON', 'VERB', 'ADJ'):
            list_segments.append(Segment(ix, end - 1, None, tag[0]))
        ix = end

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
    encode = "0000000000000000000000000000000000"
    for i in list_domains:
        # print type(i)
        if i == '' or i == '[]':
            continue
        encode = encode[:domain_to_num[i.strip().lower()]] + '1' + encode[domain_to_num[i.strip().lower()] + 1 : ]

    return encode


def list_domain_decode(s):
    domains = []
    for i in range(len(s)):
        if s[i] =='1':
            domains.append(list_domains[i])

    return domains

def list_domain_num_encode(list_domains_num):
    encode = "0000000000000000000000000000000000"
    for i in list_domains_num:
        encode = encode[:i] + '1' + encode[i+1:]

    return encode


def update_kbs(conversation):
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


def update_concept(conversation):
    concept = Concept.query.get(conversation.concept_id)
    concept.relation_count -= 1
    relation_num = conversation.relation
    concept.relation_check = concept.relation_check[:relation_num] + '2' + concept.relation_check[relation_num + 1:]
