# -*- coding: utf-8 -*-
"""
@author: Gia Huy

Constants initializations
  - Creates mapping between domain string presentation and its id in "data/given_data/domain_list.txt"
  - Creates mapping between relation string presentation and its id in "data/given_data/relation_list.txt"
  - Load templates of questions
"""

# Data directory
data_dir = "data/given_data/"

# Babelnet API Key
BABELNET_KEY = "2805fb42-65c1-4f03-8689-687b4455eae6"
KBS_KEY = "61dc9d2b-8bf8-434e-b3ec-08f32e523959"
TELEGRAM_KEY = "bot382360568:AAGn2SWgtTdpafWd-g_dvVkIvZZeAOomB4w"

# Load relation list
relation_to_num = dict()
list_relations = []
f = open(data_dir + "relation_list.txt")
content = f.readlines()
for i, line in enumerate(content):
    list_relations.append(line.strip().lower())
    relation_to_num[line.strip().lower()] = i


# Load domain list
domain_to_num = dict()
list_domains = []
f = open(data_dir + "domain_list.txt")
content = f.readlines()
for i, line in enumerate(content):
    list_domains.append(line.strip().lower())
    domain_to_num[line.strip().lower()] = i


# Load question templates
question_templates = []
for i in range(len(list_relations)):
    question_templates.append([])

f = open(data_dir + "patterns.txt")
content = f.readlines()
for line in content:
    question = line.strip()
    if len(question) > 0:
        question = question.split('\t')
        relation_num = relation_to_num[question[1].strip()]
        question_templates[relation_num].append(question[0])

# Template of answers
WELCOME_REPONSES = ["Hello, what would you like to talk about ?",
                    "Hi, which topic would you like to discuss ?",
                    "Hello, which field should we need to discuss ?"]

DIRECTION_RESPONSES = ["Would you like to ask a question ?",
                      "You would like to ask me a question ?",
                       "Do you have a question for me ? "]

QUERYING_RESONSES = ["Please ask me a question !",
                     "What is your question ?",
                     "What would you like to ask ?"]

SUCCESSFUL_ENRICH_RESPONSES = ["I got your answer ! Thank you !",
                               "Bravo ! Your answer is appreciated.",
                               "Thank you ! I will update my knowledge base using your answer."]

UNSUCCESSFUL_ENRICH_RESPONSES = ["Don't worry ! You will can answer it next time.",
                                 "Nevermind, it's difficult question ! ",
                                 "Ah, you will answer it soon."]

def INVALID_ANSWER(field):
    return "Your " + field +" is not valid.\nPlease type anything to start a new session"