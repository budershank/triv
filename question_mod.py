import db

class Question(object):
    def __init__(self, oid, question, correct,
                 wrong1, wrong2, wrong3,
                 num_right, num_wrong, demographics):
        self.oid = oid
        self.question = question
        self.correct = correct
        self.wrong1 = wrong1
        self.wrong2 = wrong2
        self.wrong3 = wrong3

        self.num_right = num_right
        self.num_wrong = num_wrong

        self.demographics = demographics

    @staticmethod
    def from_oid(question_oid):
        return Question.from_doc(db.question_from_oid(question_oid))

    @classmethod
    def from_doc(cls, doc):
        return cls(doc["_id"], doc["question"], doc["correct"],
                   doc["wrong1"], doc["wrong2"], doc["wrong3"],
                   doc["num_right"], doc["num_wrong"], doc["demographics"])

    def right_answer(self, guess_str):
        return self.correct == guess_str

    def _init_demographic(self, category, value):
        if category not in self.demographics:
            self.demographics[category] = {}

        if value not in self.demographics[category]:
            self.demographics[category][value] = {"right": 0, "wrong": 0}

    def answered_right(self, demographics):
        self.num_right += 1
        for category, value in demographics.items():
            self._init_demographic(category, value)
            self.demographics[category][value]["right"] += 1

        db.update_question_correct(self.oid, demographics)

    def answered_wrong(self, demographics):
        self.num_wrong += 1
        for category, value in demographics.items():
            self._init_demographic(category, value)
            self.demographics[category][value]["wrong"] += 1

        db.update_question_wrong(self.oid, demographics)

    """
    def update(self):
        #to update statistics
        doc = db.question_from_oid(self.oid)
        self.__init__(doc["_id"], doc["question"], doc["correct"],
                      doc["wrong1"], doc["wrong2"], doc["wrong3"],
                      doc["num_right"], doc["num_wrong"], doc["demographics"])
                      """

index = {}
all_questions = []
def init(flush=False):
    global index
    global all_questions

    if flush:
        index = {}
        all_questions = []

    if len(index):
        return False

    for question_doc in db.get_all_question_docs():
        question = Question.from_doc(question_doc)
        index[question.oid] = question

    all_questions = index.values()
    return True

def get_question(question_oid):
    init()

    print "Idx size: " + str(len(index)) + ":" + str(len(all_questions))
    return index.get(question_oid, None)

def add_question(question_doc):
    if init():
        return

    global index
    global all_questions

    question = Question.from_doc(question_doc)
    index[question_doc["_id"]] = question
    all_questions.append(question)

def get_all_questions():
    init()
    return all_questions
