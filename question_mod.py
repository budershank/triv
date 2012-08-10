import db

class Question(object):
    def __init__(self, question_doc):
        self.oid = question_doc["_id"]
        self.question = question_doc["question"]
        self.correct = question_doc["correct"]
        self.wrong1 = question_doc["wrong1"]
        self.wrong2 = question_doc["wrong2"]
        self.wrong3 = question_doc["wrong3"]

    def right_answer(self, guess_str):
        return self.correct == guess_str

index = {}
all_questions = []
def init():
    global index
    global all_questions

    if len(index):
        return

    for question_doc in db.get_all_question_docs():
        question = Question(question_doc)
        index[question.oid] = question

    all_questions = index.values()

def get_question(question_oid):
    init()

    print "Idx size: " + str(len(index)) + ":" + str(len(all_questions))
    return index.get(question_oid, None)

def get_all_questions():
    init()
    return all_questions
