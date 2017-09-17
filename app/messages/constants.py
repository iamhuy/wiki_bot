

relation_to_num = dict()
list_relations = ['sound', 'material', 'specialization', 'similarity',
             'taste', 'activity', 'generalization', 'color',
             'shape', 'part', 'place', 'purpose',
             'time', 'how_to_use', 'smell', 'size']
for i, relation in enumerate(list_relations):
    relation_to_num[relation] = i


domain_to_num = dict()
list_domains = []
f = open("domain_list.txt")
content = f.readlines()
for i, line in enumerate(content):
    list_domains.append(line.strip().lower())
    domain_to_num[line.strip().lower()] = i