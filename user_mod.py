import db
import question_mod
import random

class User(object):
    def __init__(self, user_oid, correct, wrong, demographics):
        self._oid = user_oid
        self._num_correct = len(correct)
        self._num_wrong = len(wrong)
        self._answered_questions = set(correct + wrong)
        self._demographics = demographics

    @staticmethod
    def from_oid(user_oid):
        return User.from_doc(db.user_from_oid(user_oid))

    @staticmethod
    def from_username(username):
        return User.from_doc(db.user_from_username(username))

    @classmethod
    def from_doc(cls, doc):
        return cls(doc["_id"], doc["correct"], doc["wrong"], doc["demographics"])

    def get_question(self):
        all_questions = question_mod.get_all_questions()
        for try_num in xrange(100):
            ret = random.choice(all_questions)
            if ret.oid not in self._answered_questions:
                return ret

        return None

    def answered_question(self, question_oid):
        return question_oid in self._answered_questions

    def was_correct(self, question_oid):
        self._answered_questions.add(question_oid)
        self._num_correct += 1
        db.user_guess_right(self._oid, question_oid)

    def was_wrong(self, question_oid):
        self._answered_questions.add(question_oid)
        self._num_wrong += 1
        db.user_guess_wrong(self._oid, question_oid)

    def timed_out(self, question_oid):
        self._answered_questions.add(question_oid)
        db.user_guess_wrong(self._oid, question_oid)
        db.update_question_wrong(question_oid, self._demographics)

    def add_demographic(self, category, value):
        self._demographics[category] = value
        db.add_demographic(self._oid, category, value)
