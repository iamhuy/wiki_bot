


# Load relation list
relation_to_num = dict()
list_relations = []
f = open("data/given_data/relation_list.txt")
content = f.readlines()
for i, line in enumerate(content):
    list_relations.append(line.strip().lower())
    relation_to_num[line.strip().lower()] = i


# Load domain list
domain_to_num = dict()
list_domains = []
f = open("data/given_data/domain_list.txt")
content = f.readlines()
for i, line in enumerate(content):
    list_domains.append(line.strip().lower())
    domain_to_num[line.strip().lower()] = i

# Load question templates
question_templates = []
for i in range(len(list_relations)):
    question_templates.append([])

f = open("data/given_data/patterns.txt")
content = f.readlines()
for line in content:
    question = line.strip()
    if len(question) > 0:
        question = question.split('\t')
        relation_num = relation_to_num[question[1].strip()]
        question_templates[relation_num].append(question[0])
