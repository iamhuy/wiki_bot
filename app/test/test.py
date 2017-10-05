import json
from app.messages.models import  *
from app.messages.utils import *


def test():
    file_test = open('data/test_data/test_yesno.txt',"r")
    file_result = open('data/test_data/result_yesno.txt',"w")
    test = json.loads(file_test.read())
    sum_count = 0

    dump_conversation = Chat.query.get(0)
    if dump_conversation == None:
        dump_conversation = create_conversation(0, None)

    for relation in test:
        count = 0
        print(relation)
        for pair in test[relation]:
            dump_conversation.question = pair['question']
            dump_conversation.answer = pair['answer']
            actual_relation = intent_predict(dump_conversation.question).lower()
            dump_conversation.relation = relation_to_num[actual_relation]
            actual_answer = answer_generator(dump_conversation)
            pair['actual_answer'] = actual_answer
            pair['actual_relation'] = actual_relation
            if actual_answer == dump_conversation.answer and relation == actual_relation:
                count+=1
        test[relation].append(count)
        sum_count += count

    test['sum_true_count'] = sum_count

    file_result.write(json.dumps(test, indent=4))
    file_result.close()